from flask import Flask, render_template, request, redirect, url_for, jsonify
import firebase_admin
from firebase_admin import credentials, firestore
import os


app = Flask(__name__)

# --- Configuration ---
# Set the project ID dynamically based on the environment or Fallback to a placeholder
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "your-gcp-project-id")
FIRESTORE_COLLECTION = "notes"


# --- Firestore Initialization ---
# For Cloud Run, Application Default Credentials will be used.
# For local development, GOOGLE_APPLICATION_CREDENTIALS env var pointing to a service account key is expected.
try:
    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred, {'projectId': PROJECT_ID})
    db = firestore.client()
    print(f"Firestore initialized for project: {PROJECT_ID}")
except Exception as e:
    print(f"Error initializing Firebase Admin SDK: {e}")
    print("Ensure 'GOOGLE_APPLICATION_CREDENTIALS' is set for local development, or running in GCP environment.")
    db = None # Set db to None if initialization fails

@app.route("/")
def hello_world():
    return "Hello, world!"

@app.route("/notes", methods=["POST"])
def create_note():
    if not db:
        return jsonify({"error": "Firestore not initialized"}), 500

    try:
        data = request.get_json()
        title = data.get("title")
        content = data.get("content")

        if not title or not content:
            return jsonify({"error": "Title and content are required"}), 400

        # Add a new document with a generated ID
        new_note_ref = db.collection(FIRESTORE_COLLECTION).document()
        new_note_ref.set({
            "title": title,
            "content": content,
            "timestamp": firestore.SERVER_TIMESTAMP
        })

        return jsonify({
            "id": new_note_ref.id,
            "message": "Note created successfully"
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500




