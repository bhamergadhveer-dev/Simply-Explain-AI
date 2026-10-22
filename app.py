from flask import Flask, render_template, jsonify
from dotenv import load_dotenv
import os, requests
from flask import request

load_dotenv()

app = Flask(__name__)

@app.get("/")
def home():
    return render_template("index.html")

@app.get("/health")
def health():
    return jsonify(status="ok")


@app.post("/api/explain")
def explain():
    text = (request.get_json(silent=True) or {}).get("text", "").strip()
    if len(text) < 5:
        return jsonify(error="Enter a topic."), 400

    key = os.environ.get("GROQ_API_KEY")
    if not key:
        return jsonify(error="Missing GROQ_API_KEY"), 500

    model = os.environ.get("GROQ_MODEL", "")
    if not model:
        return jsonify(error="Missing GROQ_MODEL"), 500

    try:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}"},
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": "You explain things simply for beginner students."},
                    {"role": "user", "content": "Explain in 4 sentences with one example: " + text[:3000]},
                ],
            },
            timeout=25,
        )
        data = r.json()
        if not r.ok:
            return jsonify(error=data.get("error", {}).get("message", "AI request failed.")), 502
        return jsonify(answer=data["choices"][0]["message"]["content"])
    except Exception:
        return jsonify(error="Could not reach the AI. Try again."), 500


if __name__ == "__main__":
    app.run