import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QPushButton,
    QLineEdit, QLabel, QVBoxLayout, QWidget, QComboBox, QTimeEdit, QMessageBox
)
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from datetime import datetime, timezone, timedelta


class YouTubeLiveStreamApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("YouTube Live Stream Manager")
        self.setGeometry(300, 300, 500, 500)

        self.api_service = None  # Holds the authenticated API service
        self.thumbnail_path = None  # Path to the selected thumbnail image
        self.current_broadcast_id = None  # Holds the ID of the current broadcast

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
        self.input_start_time.setDisplayFormat("HH:mm")
        self.input_start_time.setTime(datetime.now().time())  # Default to the current time
        self.layout.addWidget(self.input_start_time)

        self.label_end_time = QLabel("End Time (Local Time):")
        self.layout.addWidget(self.label_end_time)

        self.input_end_time = QTimeEdit()
        self.input_end_time.setDisplayFormat("HH:mm")
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
        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                "client_secrets.json", scopes=["https://www.googleapis.com/auth/youtube.force-ssl"]
            )
            credentials = flow.run_local_server(port=0)
            self.api_service = build("youtube", "v3", credentials=credentials)
            QMessageBox.information(self, "Success", "Authentication successful!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Authentication failed: {e}")

    def upload_thumbnail(self):
        """Select a thumbnail image."""
        thumbnail_path, _ = QFileDialog.getOpenFileName(self, "Select Thumbnail", "", "Images (*.png *.jpg *.jpeg)")
        if thumbnail_path:
            self.thumbnail_path = thumbnail_path
            QMessageBox.information(self, "Thumbnail Selected", f"Thumbnail path: {self.thumbnail_path}")

    def create_live_stream(self):
        """Create a new YouTube live stream."""
        if not self.api_service:
            QMessageBox.critical(self, "Error", "Please authenticate first!")
            return

        title = self.input_title.text().strip()
        now = datetime.now()
        start_time = datetime.combine(now.date(), self.input_start_time.time()).astimezone().isoformat()
        end_time = datetime.combine(now.date(), self.input_end_time.time()).astimezone().isoformat()
        privacy_status = self.combo_privacy.currentText().lower()

        if not title or not start_time or not end_time:
            QMessageBox.critical(self, "Error", "Please fill in all fields!")
            return

        try:
            # Create broadcast
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
                        "enableAutoStop": True,
                    },
                },
            )
            broadcast_response = broadcast_request.execute()
            self.current_broadcast_id = broadcast_response["id"]

            # Upload thumbnail
            if self.thumbnail_path:
                self.api_service.thumbnails().set(
                    videoId=self.current_broadcast_id,
                    media_body=self.thumbnail_path,
                ).execute()

            QMessageBox.information(self, "Success", "Live stream created successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create live stream: {e}")

    def start_live_stream(self):
        """Start the live stream."""
        if not self.current_broadcast_id:
            QMessageBox.critical(self, "Error", "No live stream available to start.")
            return

        try:
            self.api_service.liveBroadcasts().transition(
                broadcastStatus="live", id=self.current_broadcast_id, part="id,status"
            ).execute()
            QMessageBox.information(self, "Success", "Live stream started successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start live stream: {e}")

    def stop_live_stream(self):
        """Stop the live stream."""
        if not self.current_broadcast_id:
            QMessageBox.critical(self, "Error", "No live stream available to stop.")
            return

        try:
            self.api_service.liveBroadcasts().transition(
                broadcastStatus="complete", id=self.current_broadcast_id, part="id,status"
            ).execute()
            QMessageBox.information(self, "Success", "Live stream stopped successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to stop live stream: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = YouTubeLiveStreamApp()
    window.show()
    sys.exit(app.exec())
