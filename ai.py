from openai import OpenAI
import os

# ===============================
# 🔐 SECURE API CONFIG
# ===============================
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="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"  # ✅ use env variable
)


# ===============================
# ✂️ TEXT CHUNKING
# ===============================
def chunk_text(text, max_chars=2000):
    return [text[i:i + max_chars] for i in range(0, len(text), max_chars)]


# ===============================
# 🧠 SUMMARY FUNCTION
# ===============================
def generate_summary(text):
    try:
        chunks = chunk_text(text)
        summaries = []

        # 🔥 limit chunks (performance safe)
        for chunk in chunks[:3]:
            response = client.chat.completions.create(
                model="meta/llama3-70b-instruct",
                messages=[
                    {
                        "role": "user",
                        "content": f"Summarize clearly:\n{chunk}"
                    }
                ]
            )

            summaries.append(response.choices[0].message.content.strip())

        return "\n\n".join(summaries)

    except Exception as e:
        print("AI ERROR:", e)
        return "Summary could not be generated."


# ===============================
# 💬 CHAT FUNCTION
# ===============================
def chat_ai(prompt, content=None):
    try:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an AI tutor.\n"
                    "- Explain clearly\n"
                    "- Help revise\n"
                    "- Ask follow-up questions\n"
                )
            }
        ]

        # 🔥 Inject PDF knowledge
        if content:
            messages.append({
                "role": "system",
                "content": f"STUDY MATERIAL:\n{content[:3000]}"
            })

        messages.append({
            "role": "user",
            "content": prompt
        })

        response = client.chat.completions.create(
            model="meta/llama3-70b-instruct",
            messages=messages
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print("AI CHAT ERROR:", e)
        return "AI could not respond."