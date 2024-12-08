import sys
import os
import pickle
import logging
import json
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QPushButton, QVBoxLayout,
    QLineEdit, QLabel, QWidget, QComboBox, QTimeEdit, QMessageBox, QListWidget
)
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from datetime import datetime, timezone, timedelta
from PIL import Image
import obsws_python as obs

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

OBS_CONFIG_FILE = "obs_config.json"


class YouTubeLiveStreamApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("YouTube Live Stream Manager with OBS Control")
        self.setGeometry(300, 300, 800, 900)

        self.api_service = None  # Holds the authenticated API service
        self.thumbnail_path = None  # Path to the selected thumbnail image
        self.current_broadcast_id = None  # Holds the ID of the currently selected broadcast
        self.stream_id = None  # Holds the ID of the created stream
        self.credentials_path = "youtube_credentials.pkl"  # Path to cache credentials

        # OBS WebSocket
        self.obs_client = None
        self.obs_config = self.load_obs_config()

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

        self.label_start_time = QLabel("Start Time (Local Time):")
        self.layout.addWidget(self.label_start_time)

        self.input_start_time = QTimeEdit()
        self.input_start_time.setTime(datetime.now().time())  # Default to the current time
        self.layout.addWidget(self.input_start_time)

        self.label_end_time = QLabel("End Time (Local Time):")
        self.layout.addWidget(self.label_end_time)

        self.input_end_time = QTimeEdit()
        self.input_end_time.setTime((datetime.now() + timedelta(hours=1)).time())  # Default to one hour later
        self.layout.addWidget(self.input_end_time)

        self.label_privacy = QLabel("Privacy Status:")
        self.layout.addWidget(self.label_privacy)

        self.combo_privacy = QComboBox()
        self.combo_privacy.addItems(["Public", "Unlisted", "Private"])
        self.layout.addWidget(self.combo_privacy)

        self.label_stream_key = QLabel("Stream Key:")
        self.layout.addWidget(self.label_stream_key)

        self.combo_stream_key = QComboBox()
        self.layout.addWidget(self.combo_stream_key)

        self.label_scheduled_streams = QLabel("Scheduled Streams:")
        self.layout.addWidget(self.label_scheduled_streams)

        self.combo_scheduled_streams = QComboBox()
        self.layout.addWidget(self.combo_scheduled_streams)

        self.label_playlist = QLabel("Select Playlist:")
        self.layout.addWidget(self.label_playlist)

        self.combo_playlist = QComboBox()
        self.layout.addWidget(self.combo_playlist)

        self.button_upload_thumbnail = QPushButton("Upload Thumbnail")
        self.button_upload_thumbnail.clicked.connect(self.upload_thumbnail)
        self.layout.addWidget(self.button_upload_thumbnail)

        self.button_authenticate = QPushButton("Authenticate")
        self.button_authenticate.clicked.connect(self.authenticate)
        self.layout.addWidget(self.button_authenticate)

        self.button_create_stream = QPushButton("Create Live Stream")
        self.button_create_stream.clicked.connect(self.create_live_stream)
        self.layout.addWidget(self.button_create_stream)

        self.button_refresh_streams = QPushButton("Refresh Scheduled Streams")
        self.button_refresh_streams.clicked.connect(self.load_scheduled_streams)
        self.layout.addWidget(self.button_refresh_streams)

        self.button_start_stream = QPushButton("Start Live Stream")
        self.button_start_stream.clicked.connect(self.start_live_stream)
        self.layout.addWidget(self.button_start_stream)

        self.button_stop_stream = QPushButton("Stop Live Stream")
        self.button_stop_stream.clicked.connect(self.stop_live_stream)
        self.layout.addWidget(self.button_stop_stream)

        self.button_refresh_stream_keys = QPushButton("Refresh Stream Keys")
        self.button_refresh_stream_keys.clicked.connect(self.load_stream_keys)
        self.layout.addWidget(self.button_refresh_stream_keys)

        # OBS Control Buttons
        self.button_connect_obs = QPushButton("Connect to OBS")
        self.button_connect_obs.clicked.connect(self.connect_to_obs)
        self.layout.addWidget(self.button_connect_obs)

        self.button_start_obs_stream = QPushButton("Start OBS Streaming")
        self.button_start_obs_stream.clicked.connect(self.start_obs_streaming)
        self.layout.addWidget(self.button_start_obs_stream)

        self.button_stop_obs_stream = QPushButton("Stop OBS Streaming")
        self.button_stop_obs_stream.clicked.connect(self.stop_obs_streaming)
        self.layout.addWidget(self.button_stop_obs_stream)

        # Initialize data
        self.auto_authenticate()
        self.load_scheduled_streams()
        self.load_playlists()
        self.load_stream_keys()

    def auto_authenticate(self):
        """Automatically authenticate using cached credentials."""
        logging.info("Checking for cached credentials.")
        try:
            credentials = None
            if os.path.exists(self.credentials_path):
                with open(self.credentials_path, "rb") as token:
                    credentials = pickle.load(token)
                    logging.info("Loaded cached credentials.")

            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
                logging.info("Refreshed expired credentials.")
                self.api_service = build("youtube", "v3", credentials=credentials)
            elif credentials:
                self.api_service = build("youtube", "v3", credentials=credentials)
                logging.info("Using cached credentials.")
            else:
                self.authenticate()
        except Exception as e:
            logging.error(f"Auto-authentication failed: {e}")
            QMessageBox.critical(self, "Error", f"Auto-authentication failed: {e}")

    def authenticate(self):
        """Authenticate the user and set up the API service."""
        logging.info("Starting authentication process.")
        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                "client_secrets.json", scopes=["https://www.googleapis.com/auth/youtube.force-ssl"]
            )
            credentials = flow.run_local_server(port=0)
            with open(self.credentials_path, "wb") as token:
                pickle.dump(credentials, token)
            self.api_service = build("youtube", "v3", credentials=credentials)
            logging.info("Authentication successful.")
            QMessageBox.information(self, "Success", "Authentication successful!")
            self.load_stream_keys()
        except Exception as e:
            logging.error(f"Authentication failed: {e}")
            QMessageBox.critical(self, "Error", f"Authentication failed: {e}")

    def load_scheduled_streams(self):
        """Load scheduled streams into the dropdown."""
        logging.info("Loading scheduled streams.")
        try:
            self.combo_scheduled_streams.clear()
            response = self.api_service.liveBroadcasts().list(
                part="snippet",
                mine=True,
                maxResults=25
            ).execute()
            for item in response.get("items", []):
                stream_title = item["snippet"]["title"]
                stream_id = item["id"]
                self.combo_scheduled_streams.addItem(stream_title, stream_id)
            logging.info("Scheduled streams loaded successfully.")
        except Exception as e:
            logging.error(f"Failed to load scheduled streams: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load scheduled streams: {e}")

    def load_playlists(self):
        """Load playlists into the dropdown."""
        logging.info("Loading playlists.")
        try:
            self.combo_playlist.clear()
            response = self.api_service.playlists().list(
                part="snippet",
                mine=True,
                maxResults=25
            ).execute()
            for item in response.get("items", []):
                self.combo_playlist.addItem(item["snippet"]["title"], item["id"])
            logging.info("Playlists loaded successfully.")
        except Exception as e:
            logging.error(f"Failed to load playlists: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load playlists: {e}")

    def load_stream_keys(self):
        """Load available stream keys into the dropdown."""
        logging.info("Loading available stream keys.")
        try:
            self.combo_stream_key.clear()
            response = self.api_service.liveStreams().list(
                part="snippet,cdn",
                mine=True,
                maxResults=25
            ).execute()
            for item in response.get("items", []):
                stream_name = item["snippet"]["title"]
                stream_id = item["id"]
                self.combo_stream_key.addItem(stream_name, stream_id)
            logging.info("Stream keys loaded successfully.")
        except Exception as e:
            logging.error(f"Failed to load stream keys: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load stream keys: {e}")

    def upload_thumbnail(self):
        """Upload a thumbnail for the selected stream."""
        logging.info("Uploading thumbnail.")
        try:
            options = QFileDialog.Options()
            self.thumbnail_path, _ = QFileDialog.getOpenFileName(self, "Select Thumbnail", "", "Images (*.png *.jpg *.jpeg)", options=options)
            if not self.thumbnail_path:
                return

            # Check for a selected stream
            if not self.current_broadcast_id:
                QMessageBox.critical(self, "Error", "No scheduled stream selected.")
                return

            # Upload thumbnail
            with open(self.thumbnail_path, "rb") as file:
                self.api_service.thumbnails().set(
                    videoId=self.current_broadcast_id,
                    media_body=file
                ).execute()
            logging.info("Thumbnail uploaded successfully.")
            QMessageBox.information(self, "Success", "Thumbnail uploaded successfully!")
        except Exception as e:
            logging.error(f"Failed to upload thumbnail: {e}")
            QMessageBox.critical(self, "Error", f"Failed to upload thumbnail: {e}")

    
    def load_obs_config(self):
        """Load OBS WebSocket configuration from a JSON file."""
        if not os.path.exists(OBS_CONFIG_FILE):
            default_config = {"host": "localhost", "port": 4455, "password": "your_password"}
            with open(OBS_CONFIG_FILE, "w") as file:
                json.dump(default_config, file, indent=4)
            return default_config
        with open(OBS_CONFIG_FILE, "r") as file:
            return json.load(file)

    def connect_to_obs(self):
        """Connect to OBS WebSocket."""
        try:
            # Initialize and connect automatically
            self.obs_client = obs.ReqClient(
                host=self.obs_config["host"],
                port=self.obs_config["port"],
                password=self.obs_config["password"]
            )
            logging.info("Connected to OBS WebSocket.")
            QMessageBox.information(self, "Success", "Connected to OBS successfully!")
        except Exception as e:
            logging.error(f"Failed to connect to OBS: {e}")
            QMessageBox.critical(self, "Error", f"Failed to connect to OBS: {e}")
    
    def start_obs_streaming(self):
        """Start streaming in OBS."""
        try:
            self.obs_client.start_stream()
            logging.info("Started OBS streaming.")
            QMessageBox.information(self, "Success", "OBS streaming started!")
        except Exception as e:
            logging.error(f"Failed to start OBS streaming: {e}")
            QMessageBox.critical(self, "Error", f"Failed to start OBS streaming: {e}")

    def stop_obs_streaming(self):
        """Stop streaming in OBS."""
        try:
            self.obs_client.stop_stream()
            logging.info("Stopped OBS streaming.")
            QMessageBox.information(self, "Success", "OBS streaming stopped!")
        except Exception as e:
            logging.error(f"Failed to stop OBS streaming: {e}")
            QMessageBox.critical(self, "Error", f"Failed to stop OBS streaming: {e}")

    def closeEvent(self, event):
        """Gracefully close the application."""
        if self.obs_client:
            try:
                self.obs_client.disconnect()
                logging.info("Disconnected from OBS WebSocket.")
            except Exception as e:
                logging.error(f"Failed to disconnect OBS WebSocket: {e}")
        event.accept()

    def get_default_title(self):
        """Generate a default title with the current date and AM/PM."""
        now = datetime.now()
        return now.strftime(" | %B %d, %Y %A %p")

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
