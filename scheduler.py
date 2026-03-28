from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from flask import current_app

from models import Lesson, Learning, User
from email_utils import send_email

# ===============================
# ⚙️ INIT
# ===============================
scheduler = BackgroundScheduler()
notifications = []


# ===============================
# 🚀 START SCHEDULER (SAFE)
# ===============================
def start_scheduler():
    if not scheduler.running:
        scheduler.start()
        print("✅ Scheduler started")


# ===============================
# ⏰ LESSON REMINDER SCHEDULER
# ===============================
def schedule_lesson(lesson):
    intervals = [1, 3, 10]  # minutes

    for i, mins in enumerate(intervals):
        run_time = lesson.created_at + timedelta(minutes=mins)

        scheduler.add_job(
            func=trigger_lesson_notification,
            trigger="date",
            run_date=run_time,
            args=[lesson.id],
            id=f"lesson_{lesson.id}_{i}",
            replace_existing=True,
        )


# ===============================
# 🔔 LESSON NOTIFICATION
# ===============================
def trigger_lesson_notification(lesson_id):
    with current_app.app_context():
        lesson = Lesson.query.get(lesson_id)

        if not lesson:
            return

        user = User.query.get(lesson.user_id)
        if not user:
            return

        # 🧠 Message
        message = (
            f"📘 Revise: {lesson.title}"
            if lesson.category == "Education"
            else f"💚 Reminder: {lesson.title}"
        )

        # 🔔 Store notification (UI)
        notifications.append({
            "user_id": user.id,
            "message": message,
            "time": datetime.utcnow().strftime("%H:%M:%S"),
        })

        # 📧 Email
        email_body = f"""
Hello 👋

{message}

Details:
{lesson.sub_details or "No details provided"}

Stay consistent 💪
"""

        try:
            send_email(user.email, "Adaptive Reminder 🔔", email_body)
        except Exception as e:
            print("❌ Email failed:", e)


# ===============================
# 🧠 LEARNING REMINDER SCHEDULER
# ===============================
def schedule_learning(learning):
    base_time = learning.time_spent or 10  # fallback safety

    # Smart spaced repetition
    intervals = [
        (1, int(base_time * 0.5)),
        (3, int(base_time * 0.3)),
        (5, int(base_time * 0.1)),
    ]

    for i, (mins, effort) in enumerate(intervals):
        run_time = datetime.utcnow() + timedelta(minutes=mins)

        scheduler.add_job(
            func=trigger_learning_notification,
            trigger="date",
            run_date=run_time,
            args=[learning.id, effort],
            id=f"learning_{learning.id}_{i}",
            replace_existing=True,
        )


# ===============================
# 🔔 LEARNING NOTIFICATION
# ===============================
def trigger_learning_notification(learning_id, effort):
    with current_app.app_context():
        learning = Learning.query.get(learning_id)

        if not learning:
            return

        user = User.query.get(learning.user_id)
        if not user:
            return

        message = f"""
📘 Revise: {learning.title}

Summary:
{(learning.summary or "")[:300]}

⏱ Suggested Time: {effort} minutes
"""

        # 🔔 Store for UI
        notifications.append({
            "user_id": user.id,
            "message": f"📘 Revise: {learning.title}",
            "time": datetime.utcnow().strftime("%H:%M:%S"),
        })

        # 📧 Email
        try:
            send_email(user.email, "AI Learning Reminder 📚", message)
        except Exception as e:
            print("❌ Email error:", e)