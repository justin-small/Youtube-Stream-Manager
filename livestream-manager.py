import sys
import os
import pickle
import logging
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QPushButton,
    QLineEdit, QLabel, QVBoxLayout, QWidget, QComboBox, QTimeEdit, QMessageBox, QListWidget
)
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from datetime import datetime, timezone, timedelta
from PIL import Image
from time import sleep

# Configure logging
log_file = "youtube_live_stream_manager.log"
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)


class YouTubeLiveStreamApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("YouTube Live Stream Manager")
        self.setGeometry(300, 300, 600, 800)

        self.api_service = None  # Holds the authenticated API service
        self.thumbnail_path = None  # Path to the selected thumbnail image
        self.current_broadcast_id = None  # Holds the ID of the currently selected broadcast
        self.stream_id = None  # Holds the ID of the created stream
        self.credentials_path = "youtube_credentials.pkl"  # Path to cache credentials

        # Central widget and layout
        self.central_widget = QWidget()
        self.layout = QVBoxLayout(self.central_widget)
        self.setCentralWidget(self.central_widget)

        # GUI Elements
        self.label_title = QLabel("Stream Title:")
        self.layout.addWidget(self.label_title)

        self.input_title = QLineEdit()
        self.input_title.setText(self.get_default_title())  # Prepopulate the title
        self.layout.addWidget(self.input_title)

        self.label_start_time = QLabel("Start Time (Local Time, AM/PM Format):")
        self.layout.addWidget(self.label_start_time)

        self.input_start_time = QTimeEdit()
        self.input_start_time.setDisplayFormat("hh:mm AP")  # AM/PM format
        self.input_start_time.setTime(datetime.now().time())  # Default to the current time
        self.layout.addWidget(self.input_start_time)

        self.label_end_time = QLabel("End Time (Local Time, AM/PM Format):")
        self.layout.addWidget(self.label_end_time)

        self.input_end_time = QTimeEdit()
        self.input_end_time.setDisplayFormat("hh:mm AP")  # AM/PM format
        self.input_end_time.setTime((datetime.now() + timedelta(hours=1)).time())  # Default to one hour later
        self.layout.addWidget(self.input_end_time)

        self.label_privacy = QLabel("Privacy Status:")
        self.layout.addWidget(self.label_privacy)

        self.combo_privacy = QComboBox()
        self.combo_privacy.addItems(["Public", "Unlisted", "Private"])
        self.layout.addWidget(self.combo_privacy)

        self.button_upload_thumbnail = QPushButton("Upload Thumbnail")
        self.button_upload_thumbnail.clicked.connect(self.upload_thumbnail)
        self.layout.addWidget(self.button_upload_thumbnail)

        self.button_authenticate = QPushButton("Authenticate")
        self.button_authenticate.clicked.connect(self.authenticate)
        self.layout.addWidget(self.button_authenticate)

        self.button_create_stream = QPushButton("Create Live Stream")
        self.button_create_stream.clicked.connect(self.create_live_stream)
        self.layout.addWidget(self.button_create_stream)

        self.label_scheduled_streams = QLabel("Scheduled Streams:")
        self.layout.addWidget(self.label_scheduled_streams)

        self.list_scheduled_streams = QListWidget()
        self.layout.addWidget(self.list_scheduled_streams)

        self.button_refresh_streams = QPushButton("Refresh Scheduled Streams")
        self.button_refresh_streams.clicked.connect(self.load_scheduled_streams)
        self.layout.addWidget(self.button_refresh_streams)

        self.button_start_stream = QPushButton("Start Live Stream")
        self.button_start_stream.clicked.connect(self.start_live_stream)
        self.layout.addWidget(self.button_start_stream)

        self.button_stop_stream = QPushButton("Stop Live Stream")
        self.button_stop_stream.clicked.connect(self.stop_live_stream)
        self.layout.addWidget(self.button_stop_stream)

    def get_default_title(self):
        """Generate a default title with the current date and AM/PM."""
        now = datetime.now()
        return now.strftime(" | %B %d, %Y %A %p")

    def authenticate(self):
        """Authenticate the user and set up the API service."""
        logging.info("Starting authentication process.")
        try:
            credentials = None
            if os.path.exists(self.credentials_path):
                with open(self.credentials_path, "rb") as token:
                    credentials = pickle.load(token)
                    logging.info("Loaded cached credentials.")

            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
                logging.info("Refreshed expired credentials.")
            elif not credentials:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "client_secrets.json", scopes=["https://www.googleapis.com/auth/youtube.force-ssl"]
                )
                credentials = flow.run_local_server(port=0)
                with open(self.credentials_path, "wb") as token:
                    pickle.dump(credentials, token)
                    logging.info("Cached new credentials.")

            self.api_service = build("youtube", "v3", credentials=credentials)
            logging.info("Authentication successful.")
            QMessageBox.information(self, "Success", "Authentication successful!")
        except Exception as e:
            logging.error(f"Authentication failed: {e}")
            QMessageBox.critical(self, "Error", f"Authentication failed: {e}")

    def create_live_stream(self):
        """Create a new YouTube live stream."""
        logging.info("Creating a new live stream.")
        if not self.api_service:
            logging.error("Cannot create live stream. User is not authenticated.")
            QMessageBox.critical(self, "Error", "Please authenticate first!")
            return

        title = self.input_title.text().strip()
        now = datetime.now()
        start_time = datetime.combine(now.date(), self.input_start_time.time().toPyTime()).astimezone().isoformat()
        end_time = datetime.combine(now.date(), self.input_end_time.time().toPyTime()).astimezone().isoformat()
        privacy_status = self.combo_privacy.currentText().lower()

        if not title or not start_time or not end_time:
            logging.error("Missing required fields for live stream creation.")
            QMessageBox.critical(self, "Error", "Please fill in all fields!")
            return

        try:
            # 1. Create the livestream first
            stream_request = self.api_service.liveStreams().insert(
                part="snippet,cdn",
                body={
                    "snippet": {
                        "title": title
                    },
                    "cdn": {
                        "frameRate": "60fps",
                        "ingestionType": "rtmp",
                        "resolution": "1080p"
                    }
                }
            )
            stream_response = stream_request.execute()
            self.stream_id = stream_response['id']
            logging.info(f"Stream created with ID: {self.stream_id}")

            # 2. Create the broadcast
            broadcast_request = self.api_service.liveBroadcasts().insert(
                part="snippet,status,contentDetails",
                body={
                    "snippet": {
                        "title": title,
                        "scheduledStartTime": start_time,
                        "scheduledEndTime": end_time,
                    },
                    "status": {
                        "privacyStatus": privacy_status,
                    },
                    "contentDetails": {
                        "enableAutoStart": True,
                        "enableAutoStop": True
                    },
                },
            )
            broadcast_response = broadcast_request.execute()
            self.current_broadcast_id = broadcast_response["id"]
            logging.info(f"Broadcast created with ID: {self.current_broadcast_id}")

            # 3. Bind the stream to the broadcast
            bind_request = self.api_service.liveBroadcasts().bind(
                part="id,contentDetails",
                id=self.current_broadcast_id,
                streamId=self.stream_id
            )
            bind_request.execute()
            logging.info("Stream bound to broadcast successfully")

            QMessageBox.information(self, "Success", "Live stream created and bound successfully!")
            self.load_scheduled_streams()
        except Exception as e:
            logging.error(f"Failed to create live stream: {e}")
            QMessageBox.critical(self, "Error", f"Failed to create live stream: {e}")

    def upload_thumbnail(self):
        """Select, resize, and upload a thumbnail image."""
        logging.info("Prompting user to select a thumbnail.")
        thumbnail_path, _ = QFileDialog.getOpenFileName(self, "Select Thumbnail", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        if not thumbnail_path:
            return

        try:
            # Resize the image to 1280x720 with a 16:9 aspect ratio
            with Image.open(thumbnail_path) as img:
                img = img.convert("RGB")
                img = img.resize((1280, 720), Image.LANCZOS)
                resized_thumbnail_path = "resized_thumbnail.jpg"
                img.save(resized_thumbnail_path, "JPEG", quality=85)

            file_size = os.path.getsize(resized_thumbnail_path)
            if file_size > 2 * 1024 * 1024:  # 2 MB limit
                logging.error("Thumbnail file size exceeds 2 MB after resizing.")
                QMessageBox.critical(
                    self, "Error", "Thumbnail file size exceeds 2 MB. Please select a smaller image."
                )
                return

            self.thumbnail_path = resized_thumbnail_path
            logging.info(f"Thumbnail resized and saved: {self.thumbnail_path}")

            if not self.current_broadcast_id:
                logging.error("No broadcast selected for thumbnail upload.")
                QMessageBox.critical(self, "Error", "Please create or select a broadcast first!")
                return

            self.api_service.thumbnails().set(
                videoId=self.current_broadcast_id,
                media_body=self.thumbnail_path,
            ).execute()
            logging.info("Thumbnail uploaded successfully.")
            QMessageBox.information(self, "Success", "Thumbnail uploaded successfully!")

        except Exception as e:
            logging.error(f"Failed to upload thumbnail: {e}")
            QMessageBox.critical(self, "Error", f"Failed to upload thumbnail: {e}")

    def load_scheduled_streams(self):
        """Load currently scheduled live streams into the list widget."""
        logging.info("Loading scheduled live streams.")
        if not self.api_service:
            logging.error("Cannot load scheduled streams. User is not authenticated.")
            QMessageBox.critical(self, "Error", "Please authenticate first!")
            return

        try:
            response = self.api_service.liveBroadcasts().list(
                part="id,snippet,status",
                broadcastStatus="upcoming",
                maxResults=10,
            ).execute()

            self.list_scheduled_streams.clear()
            for item in response.get("items", []):
                title = item["snippet"]["title"]
                broadcast_id = item["id"]
                self.list_scheduled_streams.addItem(f"{title} ({broadcast_id})")
                logging.info(f"Scheduled stream found: {title} (ID: {broadcast_id})")
            QMessageBox.information(self, "Success", "Scheduled streams loaded successfully!")
        except Exception as e:
            logging.error(f"Failed to load scheduled streams: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load scheduled streams: {e}")

    def get_selected_broadcast_id(self):
        selected_item = self.list_scheduled_streams.currentItem()
        if not selected_item:
            QMessageBox.critical(self, "Error", "Please select a stream from the list.")
            logging.error("No stream selected from the list.")
            return None
        broadcast_id = selected_item.text().split("(")[-1][:-1]
        logging.info(f"Selected stream ID: {broadcast_id}")
        return broadcast_id

    def start_live_stream(self):
        """Start the live stream by transitioning from 'ready' to 'live' if conditions are met."""
        logging.info("Starting live stream.")
        broadcast_id = self.get_selected_broadcast_id()
        if not broadcast_id:
            return

        try:
            # Fetch current lifecycle status
            response = self.api_service.liveBroadcasts().list(
             part="status",
                id=broadcast_id
        ).execute()

            if not response.get("items"):
                raise ValueError("Broadcast not found.")

            current_status = response["items"][0]["status"]["lifeCycleStatus"]
            logging.info(f"Current lifecycle status: {current_status}")

            if current_status == "ready":
            # Confirm RTMP ingestion status
            # This is a placeholder; replace it with a function to verify the ingestion.
            # Ensure the streaming software (e.g., OBS) is sending data to the RTMP endpoint.

                logging.info("Attempting to transition from 'ready' to 'live'.")
                self.api_service.liveBroadcasts().transition(
                    broadcastStatus="live",
                    id=broadcast_id,
                    part="id,status",
                ).execute()
                logging.info("Successfully transitioned from 'ready' to 'live'.")
                QMessageBox.information(self, "Success", "Live stream started successfully!")
            elif current_status == "live":
                QMessageBox.information(self, "Info", "Stream is already live!")
            else:
                logging.error(f"Invalid transition from '{current_status}'.")
            QMessageBox.critical(
                self,
                "Error",
                f"Cannot start live stream: Broadcast is in '{current_status}' state."
            )

        except ValueError as ve:
            logging.error(f"Validation error: {ve}")
            QMessageBox.critical(self, "Error", str(ve))
        except Exception as e:
            logging.error(f"Failed to start live stream: {e}")
            QMessageBox.critical(self, "Error", f"Failed to start live stream: {str(e)}")

    def stop_live_stream(self):
        """Stop the live stream by transitioning from 'live' to 'complete'."""
        logging.info("Stopping live stream.")
        broadcast_id = self.get_selected_broadcast_id()
        if not broadcast_id:
            return

        try:
            # Fetch current lifecycle status
            response = self.api_service.liveBroadcasts().list(
                part="status",
                id=broadcast_id
            ).execute()

            if not response.get("items"):
                raise ValueError("Broadcast not found")

            current_status = response["items"][0]["status"]["lifeCycleStatus"]
            logging.info(f"Current lifecycle status: {current_status}")

            # Valid transitions:
            # live -> complete
            # If the broadcast is still 'ready', it can't go directly to 'complete'.
            # You must go live first, then complete once done.

            if current_status == "live":
                self.api_service.liveBroadcasts().transition(
                    broadcastStatus="complete",
                    id=broadcast_id,
                    part="id,status",
                ).execute()
                logging.info(f"Stream transitioned to complete: {broadcast_id}")
                QMessageBox.information(self, "Success", "Live stream stopped successfully!")
                self.load_scheduled_streams()

            elif current_status == "complete":
                QMessageBox.information(self, "Info", "Stream is already complete!")

            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Cannot stop live stream: Broadcast is in '{current_status}' state. You can only stop a stream that is live."
                )

        except Exception as e:
            logging.error(f"Failed to stop live stream: {e}")
            QMessageBox.critical(self, "Error", f"Failed to stop live stream: {str(e)}")

if __name__ == "__main__":
    logging.info("Application started.")
    app = QApplication(sys.argv)
    window = YouTubeLiveStreamApp()
    window.show()
    sys.exit(app.exec())
