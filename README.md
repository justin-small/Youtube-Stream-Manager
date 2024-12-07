
# YouTube Live Stream Manager

## Overview
The YouTube Live Stream Manager is a Python-based desktop application that simplifies the management of YouTube live streams. It provides a user-friendly interface for creating, scheduling, starting, stopping live streams, and uploading thumbnails.

---

## Features
- OAuth 2.0 authentication to securely connect to YouTube.
- Create live streams with:
  - Title (prepopulated with the current date and AM/PM).
  - Start and end times (time selectable; date defaults to the current date).
  - Privacy settings (Public, Unlisted, Private).
  - Thumbnail upload.
- Start and stop live streams with a single click.
- Informative error handling for failed operations.

---

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
