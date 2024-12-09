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

## Prerequisites
1. **Python 3.9 or higher**.
2. **OBS Studio** with the WebSocket plugin enabled.
3. **YouTube API Credentials**:
   - Download `client_secrets.json` from your [Google Cloud Console](https://console.cloud.google.com/).


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


usage_content = """
# Usage Guide

## Authenticate:
1. Click **"Authenticate"** to log in with your YouTube account.
2. Cached credentials will be used on subsequent runs for convenience.

---

## Create a Live Stream:
1. Fill out the required fields:
   - **Stream Title**: Enter the title for your stream.
   - **Start/End Time**: Set the schedule for the stream.
   - **Stream Key**: Select a stream key from the dropdown.
2. Click **"Create Live Stream"** to create the stream.

---

## Upload Thumbnail:
1. Click the **"Upload Thumbnail"** button.
2. Select an image file from your system to set as the thumbnail for the selected stream.

---

## OBS Integration:
1. Use the **"Connect to OBS"** button to establish a WebSocket connection with OBS Studio.
2. Start/stop streaming directly in OBS:
   - Click **"Start OBS Streaming"** to begin streaming.
   - Click **"Stop OBS Streaming"** to end the OBS stream.
3. Manage OBS scenes (optional, if scene management is enabled in the app).

# OBS Configuration File Format (`obs_config.json`)

The OBS configuration file (`obs_config.json`) is used to store connection details for the OBS WebSocket server. This file is essential for enabling the application to connect to OBS Studio.

---

## **File Format**
The configuration file must be a JSON file with the following structure:

```json
{
    "host": "localhost",
    "port": 4455,
    "password": "your_password"
}
---

For additional information, refer to the [README](README.md) or contact the support team.
"""

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
