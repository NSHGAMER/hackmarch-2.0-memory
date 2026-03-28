from flask import Blueprint, render_template, request, redirect, jsonify, session
from flask_login import login_required, current_user
from models import db, Lesson, Learning, ChatMessage, QuizAttempt, Reminder
from datetime import datetime, timedelta
from scheduler import schedule_lesson, schedule_learning, notifications
from PyPDF2 import PdfReader
from ai import generate_summary, chat_ai
import json

# ✅ MUST BE BEFORE ROUTES
routes = Blueprint("routes", __name__)


# ===============================
# 🏠 HOME
# ===============================
@routes.route("/")
def home():
    return redirect("/login")


# ===============================
# 📊 DASHBOARD
# ===============================
@routes.route("/dashboard")
@login_required
def dashboard():
    lessons = Lesson.query.filter_by(user_id=current_user.id).all()
    learnings = Learning.query.filter_by(user_id=current_user.id).all()
    return render_template("dashboard.html", lessons=lessons, learnings=learnings)


# ===============================
# ➕ ADD LESSON
# ===============================
@routes.route("/add", methods=["POST"])
@login_required
def add_lesson():
    lesson = Lesson(
        title=request.form["title"],
        category=request.form["category"],
        sub_details=request.form.get("details", ""),
        created_at=datetime.utcnow(),
        next_review=datetime.utcnow() + timedelta(minutes=1),
        user_id=current_user.id
    )

    db.session.add(lesson)
    db.session.commit()
    schedule_lesson(lesson)

    return redirect("/dashboard")


# ===============================
# 🔔 NOTIFICATIONS
# ===============================
@routes.route("/notifications")
@login_required
def get_notifications():
    user_notes = [n for n in notifications if n["user_id"] == current_user.id]
    return jsonify(user_notes)


# ===============================
# 📄 PDF TEXT EXTRACTION
# ===============================
def extract_pdf_text(file):
    reader = PdfReader(file)
    text_chunks = []

    for page in reader.pages:
        try:
            text = page.extract_text()
            if text:
                text_chunks.append(text)
        except:
            continue

    return "\n".join(text_chunks)[:15000]


# ===============================
# 📄 UPLOAD
# ===============================
@routes.route("/upload", methods=["POST"])
@login_required
def upload_pdf():
    try:
        file = request.files.get("file")
        title = request.form.get("title")
        time_spent = int(request.form.get("time", 10))

        if not file:
            return jsonify({"error": "No file uploaded"}), 400

        text = extract_pdf_text(file)

        if not text.strip():
            return jsonify({"error": "PDF extraction failed"}), 400

        summary = generate_summary(text)

        learning = Learning(
            title=title,
            content=text,
            summary=summary,
            time_spent=time_spent,
            user_id=current_user.id
        )

        db.session.add(learning)
        db.session.commit()

        # default reminder
        reminder = Reminder(
            user_id=current_user.id,
            learning_id=learning.id,
            minutes=time_spent,
            is_custom=False
        )

        db.session.add(reminder)
        db.session.commit()

        schedule_learning(learning)

        return jsonify({
            "success": True,
            "learning_id": learning.id,
            "summary": summary
        })

    except Exception as e:
        print("UPLOAD ERROR:", e)
        return jsonify({"error": "Upload failed"}), 500


# ===============================
# 💬 AI CHAT
# ===============================
@routes.route("/ask_ai", methods=["POST"])
@login_required
def ask_ai():
    try:
        data = request.get_json()
        user_msg = data.get("message")
        learning_id = data.get("learning_id")

        learning = Learning.query.get_or_404(learning_id)

        prompt = f"""
You are an AI tutor.

Study Material:
{learning.content[:3000]}

User:
{user_msg}

Explain clearly and ask follow-up questions.
"""

        reply = chat_ai(prompt)

        db.session.add(ChatMessage(
            role="user",
            message=user_msg,
            user_id=current_user.id,
            learning_id=learning_id
        ))

        db.session.add(ChatMessage(
            role="ai",
            message=reply,
            user_id=current_user.id,
            learning_id=learning_id
        ))

        db.session.commit()

        return jsonify({"reply": reply})

    except Exception as e:
        print("CHAT ERROR:", e)
        return jsonify({"reply": "AI error"})


# ===============================
# 📜 LOAD CHAT
# ===============================
@routes.route("/get_chat/<int:learning_id>")
@login_required
def get_chat(learning_id):
    chats = ChatMessage.query.filter_by(
        user_id=current_user.id,
        learning_id=learning_id
    ).order_by(ChatMessage.timestamp).all()

    return jsonify([{"role": c.role, "message": c.message} for c in chats])


# ===============================
# 🧠 CHAT SIDEBAR
# ===============================
@routes.route("/chat_sessions")
@login_required
def chat_sessions():
    learnings = Learning.query.filter_by(user_id=current_user.id)\
        .order_by(Learning.created_at.desc()).all()

    return jsonify([{"id": l.id, "title": l.title} for l in learnings])


# ===============================
# ✏️ RENAME CHAT
# ===============================
@routes.route("/rename_chat/<int:learning_id>", methods=["PUT"])
@login_required
def rename_chat(learning_id):
    data = request.get_json()
    learning = Learning.query.filter_by(id=learning_id, user_id=current_user.id).first()

    if learning:
        learning.title = data.get("title")
        db.session.commit()
        return jsonify({"success": True})

    return jsonify({"success": False})


# ===============================
# ❌ DELETE CHAT
# ===============================
@routes.route("/delete_chat/<int:learning_id>", methods=["DELETE"])
@login_required
def delete_chat(learning_id):
    try:
        ChatMessage.query.filter_by(
            user_id=current_user.id,
            learning_id=learning_id
        ).delete()

        learning = Learning.query.filter_by(
            id=learning_id,
            user_id=current_user.id
        ).first()

        if learning:
            db.session.delete(learning)

        db.session.commit()
        return jsonify({"success": True})

    except Exception as e:
        print("DELETE ERROR:", e)
        return jsonify({"success": False})


# ===============================
# 🧪 AI QUIZ GENERATION
# ===============================
@routes.route("/generate_quiz", methods=["POST"])
@login_required
def generate_quiz():
    try:
        data = request.get_json()
        learning = Learning.query.get_or_404(data["learning_id"])

        prompt = f"""
Generate 5 MCQs.

STRICT JSON ONLY:
[
  {{
    "question": "...",
    "options": ["A","B","C","D"],
    "answer": "..."
  }}
]

CONTENT:
{learning.summary[:3000]}
"""

        response = chat_ai(prompt)

        start = response.find("[")
        end = response.rfind("]") + 1
        quiz = json.loads(response[start:end])

        session["quiz"] = quiz

        return jsonify({"quiz": quiz})

    except Exception as e:
        print("QUIZ ERROR:", e)

        fallback = [{
            "question": "Fallback Question",
            "options": ["A", "B", "C", "D"],
            "answer": "A"
        }]

        session["quiz"] = fallback
        return jsonify({"quiz": fallback})


# ===============================
# 📊 SUBMIT QUIZ
# ===============================
@routes.route("/submit_quiz", methods=["POST"])
@login_required
def submit_quiz():
    data = request.get_json()
    answers = data.get("answers", [])

    quiz = session.get("quiz", [])
    correct = [q["answer"] for q in quiz]

    score = sum(
        1 for i in range(len(answers))
        if i < len(correct) and answers[i] == correct[i]
    )

    total = len(correct)

    db.session.add(QuizAttempt(
        user_id=current_user.id,
        learning_id=data["learning_id"],
        score=score,
        total=total
    ))

    db.session.commit()

    return jsonify({"score": score, "total": total})


# ===============================
# 📈 PROGRESS
# ===============================
@routes.route("/progress/<int:learning_id>")
@login_required
def progress(learning_id):
    attempts = QuizAttempt.query.filter_by(
        learning_id=learning_id,
        user_id=current_user.id
    ).all()

    return jsonify([a.score for a in attempts])


# ===============================
# ⏰ REMINDER
# ===============================
@routes.route("/set_reminder", methods=["POST"])
@login_required
def set_reminder():
    data = request.get_json()

    reminder = Reminder(
        user_id=current_user.id,
        learning_id=data["learning_id"],
        minutes=data["minutes"],
        is_custom=True
    )

    db.session.add(reminder)
    db.session.commit()

    return jsonify({"success": True})


# ===============================
# 📘 PAGES
# ===============================
@routes.route("/education")
@login_required
def education_page():
    return render_template("education.html")


@routes.route("/health")
@login_required
def health_page():
    return render_template("health.html")