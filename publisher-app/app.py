import os
from flask import Flask, request, jsonify
from google.cloud import pubsub_v1
import json
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
CORS(app)

# Configure the GCP credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./alpha-1996-ce2d16a16421.json"

# Initialize the Pub/Sub client
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(os.getenv('GCP_PROJECT_ID'), 'save-note')


# Configure the SQLAlchemy part of the app instance
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create the SQLAlchemy db instance
db = SQLAlchemy(app)


class Message(db.Model):
    __tablename__ = 'messages'  # Specify the table name
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())


@app.route('/messages', methods=['GET'])
def fetch_messages():
    messages = Message.query.all()
    messages_list = [
        {
            "id": message.id,
            "message": message.message,
            "created_at": message.created_at
        } for message in messages
    ]
    return jsonify(messages_list)


@app.route('/publish', methods=['POST'])
def publish_message():
    try:
        message_data = request.json.get('message')
        if not message_data:
            return jsonify({"error": "No message provided"}), 400

        # Convert message to bytes and publish
        future = publisher.publish(topic_path, data=message_data.encode('utf-8'))
        message_id = future.result()

        return jsonify({"message_id": message_id}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
