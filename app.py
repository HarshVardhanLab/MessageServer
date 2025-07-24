from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)

DATABASE = "messages.db"
ADMIN_PASSWORD = "1234"

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                message TEXT NOT NULL
            )
        """)
        conn.commit()

@app.route("/messages", methods=["POST"])
def receive_message():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    message = data.get("message")

    if not all([name, email, message]):
        return jsonify({"error": "All fields are required"}), 400

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO messages (name, email, message) VALUES (?, ?, ?)",
                       (name, email, message))
        conn.commit()

    return jsonify({"message": "Message received successfully"}), 200

@app.route("/", methods=["GET"])
def show_messages():
    password = request.args.get("password", "")
    if password != ADMIN_PASSWORD:
        return "Unauthorized. Add `?password=1234` to URL", 401

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, email, message FROM messages")
        rows = cursor.fetchall()

    messages = [{"name": row[0], "email": row[1], "message": row[2]} for row in rows]
    return render_template("index.html", messages=messages)

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
