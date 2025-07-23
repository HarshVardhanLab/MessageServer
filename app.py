from flask import Flask, request, jsonify
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

@app.route("/messages", methods=["GET"])
def get_messages():
    password = request.args.get("password")
    if password != ADMIN_PASSWORD:
        return jsonify({"error": "Unauthorized access"}), 401

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, email, message FROM messages")
        rows = cursor.fetchall()

    messages = [{"name": row[0], "email": row[1], "message": row[2]} for row in rows]
    return jsonify(messages), 200

if __name__ == "__main__":
    init_db()  # Initialize DB before starting the app
    app.run(debug=True, port=4000)
