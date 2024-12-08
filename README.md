# YouTube Live Stream Manager with OBS Control

## Overview
The **YouTube Live Stream Manager with OBS Control** is a Python-based GUI application that allows users to:
- Manage YouTube live streams (authentication, scheduling, uploading thumbnails, starting/stopping streams).
- Control OBS Studio (connect, start/stop streaming, and select scenes) via WebSocket integration.

---

## Features
### YouTube Features
- **Authenticate**: OAuth2-based authentication with YouTube.
- **Stream Management**: Create, view, and manage live streams.
- **Thumbnail Upload**: Upload a custom thumbnail for a scheduled live stream.
- **Dynamic Stream Key Selection**: Populate stream keys directly from the user's YouTube account.
- **Privacy Defaults**: Default privacy set to "Unlisted".

### OBS Features
- **Connect to OBS**: Establish a WebSocket connection with OBS Studio.
- **OBS Streaming**: Start/stop streaming directly from the application.
- **Scene Management**: (Optional enhancement: Switch between scenes in OBS).

## Installation

### Prerequisites
- Python 3.7 or higher.
- Google account with a YouTube channel.
- `client_secrets.json` file (downloaded from the Google Cloud Console).

### Steps
1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd <repository_folder>
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Add the `client_secrets.json` file to the project directory.

4. Run the application:
   ```bash
   python youtube_live_stream_manager.py
   ```

---

## Usage
1. **Authenticate**:
   - Log in with your Google account and grant the necessary permissions.

2. **Create a Live Stream**:
   - Fill in the stream details, select start and end times, and upload a thumbnail.
   - Click **"Create Live Stream"** to schedule the stream.

3. **Start/Stop Live Stream**:
   - Use the **Start Live Stream** and **Stop Live Stream** buttons to control the stream.

---

## File Structure
```
YouTubeLiveStreamManager/
├── client_secrets.json    # OAuth credentials for authentication
├── requirements.txt       # List of Python dependencies
├── youtube_live_stream_manager.py  # Main Python script
├── README.md              # Project documentation
└── LICENSE                # Project license
```

---

## License
This project is licensed under the MIT License. See the LICENSE file for details.

---

## Contributing
This was created 100% with openai and im not well versed in programming. 

---
