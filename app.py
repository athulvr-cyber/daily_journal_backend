# app.py
import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from models import db, JournalEntry

app = Flask(__name__)
CORS(app)

# Use DATABASE_URL when provided by the host (Render, Railway, etc.)
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    # some providers give postgres:// which SQLAlchemy doesn't like
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL.replace("postgres://", "postgresql://")
else:
    # local fallback during development
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///journal.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# create tables if they don't exist
with app.app_context():
    db.create_all()


@app.route('/add_entry', methods=['POST'])
def add_entry():
    data = request.get_json()
    if not data or 'title' not in data or 'content' not in data:
        return jsonify({"error": "title and content required"}), 400
    new_entry = JournalEntry(title=data['title'], content=data['content'])
    db.session.add(new_entry)
    db.session.commit()
    # Return empty body with 201 — safer for mobile clients
    return ("", 201)


@app.route('/get_entries', methods=['GET'])
def get_entries():
    entries = JournalEntry.query.order_by(JournalEntry.date_created.desc()).all()
    return jsonify([e.to_dict() for e in entries])


@app.route('/update_entry/<int:id>', methods=['PUT'])
def update_entry(id):
    data = request.get_json()
    entry = JournalEntry.query.get_or_404(id)
    entry.title = data.get('title', entry.title)
    entry.content = data.get('content', entry.content)
    db.session.commit()
    return jsonify({"message": "Entry updated successfully!"})


@app.route('/delete_entry/<int:id>', methods=['DELETE'])
def delete_entry(id):
    entry = JournalEntry.query.get_or_404(id)
    db.session.delete(entry)
    db.session.commit()
    return jsonify({"message": "Entry deleted successfully!"})


@app.route("/journal", methods=["GET"])
def get_journal():
    sample_data = {
        "title": "My First Journal",
        "content": "Today I started my first Android + Flask project!"
    }
    return jsonify(sample_data)


if __name__ == '__main__':
    # keep debug=True locally only
    app.run(debug=True)
