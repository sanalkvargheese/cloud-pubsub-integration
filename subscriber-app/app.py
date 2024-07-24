import os
import logging
from flask import Flask, jsonify
from google.cloud import pubsub_v1
from flask_sqlalchemy import SQLAlchemy
from concurrent.futures import TimeoutError
from sqlalchemy.exc import SQLAlchemyError
from threading import Thread

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Configure the GCP credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./alpha-1996-ce2d16a16421.json"

subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path("alpha-1996", "save-note-sub")

# Global list to store received messages (for demonstration purposes)
received_messages = []

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


def callback(message):
    logging.info(f"Received message: {message.data.decode('utf-8')}")
    received_messages.append(message.data.decode('utf-8'))

    with app.app_context():
        try:
            new_message = Message(
                message=message.data.decode('utf-8')
            )
            db.session.add(new_message)
            db.session.commit()
        except SQLAlchemyError as e:
            logging.error(f"Error inserting message into the database: {str(e)}")
            db.session.rollback()
        except Exception as e:
            logging.error(f"Unexpected error: {str(e)}")
        finally:
            message.ack()

# Function to start the subscriber
def start_subscriber():
    future = subscriber.subscribe(subscription_path, callback=callback)
    logging.info(f"Listening for messages on {subscription_path}...\n")

    try:
        future.result()
    except TimeoutError:
        future.cancel()
        logging.error("Listening for messages timed out.")
    except Exception as e:
        logging.error(f"Unexpected error in subscriber: {str(e)}")

# Start the subscriber in a separate thread when the Flask app starts
subscriber_thread = Thread(target=start_subscriber)
subscriber_thread.start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)
