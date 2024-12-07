
# **Project Outline: YouTube Live Stream Manager**

## **Project Name**:
YouTube Live Stream Manager

## **Objective**:
Create a user-friendly desktop application to manage YouTube live streams, including features to create, schedule, start, and stop live streams, as well as upload thumbnails and manage stream settings.

---

## **Features**:
1. **Authentication**:
   - OAuth 2.0 authentication to securely access a user's YouTube account.

2. **Stream Management**:
   - Create a live stream with:
     - Title (prepopulated with the current date and AM/PM).
     - Start and end times (time selectable; date defaults to the current date).
     - Privacy settings (Public, Unlisted, Private).
     - Thumbnail upload.

3. **Stream Controls**:
   - Start and stop the live stream via buttons.

4. **Error Handling**:
   - Informative error messages for failed operations.

---

## **Technologies Used**:
- **Language**: Python
- **Libraries**:
  - `PyQt6`: For GUI design.
  - `google-api-python-client`: To interact with YouTube Data API v3.
  - `google-auth-oauthlib`: For OAuth 2.0 authentication.
- **YouTube API**: YouTube Data API v3.

---

## **Workflow**:
1. **Google Cloud Setup**:
   - Enable the YouTube Data API v3.
   - Create OAuth 2.0 credentials and download the `client_secrets.json` file.

2. **Application Development**:
   - Develop the GUI using `PyQt6`.
   - Integrate YouTube API features to create, start, stop, and manage live streams.

3. **Testing**:
   - Test the application with real YouTube accounts and various stream configurations.

4. **Deployment**:
   - Distribute the application as a Python script or bundled executable (e.g., with PyInstaller).

---

# **Installation Setup**

## **Prerequisites**:
- Python 3.7 or higher
- Google account with a YouTube channel
- `client_secrets.json` file (obtained from Google Cloud Console)

---

## **Installation Instructions**:
1. **Clone or Download the Repository**:
   ```bash
   git clone <repository_url>
   cd <repository_folder>
   ```

2. **Install Dependencies**:
   Run the following command to install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

3. **Add `client_secrets.json`**:
   - Download the `client_secrets.json` file from Google Cloud Console.
   - Place the file in the project directory.

4. **Run the Application**:
   Start the application using:
   ```bash
   python youtube_live_stream_manager.py
   ```

---

## **File Structure**:
```
YouTubeLiveStreamManager/
├── client_secrets.json    # OAuth credentials for authentication
├── requirements.txt       # List of Python dependencies
├── youtube_live_stream_manager.py  # Main Python script
├── README.md              # Project documentation
└── LICENSE                # Project license
```

---

## **Dependencies**:
The `requirements.txt` file should include:
```
google-auth-oauthlib
google-api-python-client
PyQt6
```

---

## **Build as an Executable (Optional)**:
If you'd like to package the script as a standalone executable:
1. Install **PyInstaller**:
   ```bash
   pip install pyinstaller
   ```

2. Build the executable:
   ```bash
   pyinstaller --onefile youtube_live_stream_manager.py
   ```

3. The executable will be located in the `dist` folder.

---

## **Usage Instructions**:
1. **Authenticate**:
   - Log in with your Google account when prompted.
   - Grant the required permissions to the app.

2. **Create a Live Stream**:
   - Enter the stream details, select start and end times, and upload a thumbnail.
   - Click **"Create Live Stream"** to schedule the stream.

3. **Start/Stop Stream**:
   - Use the **Start Live Stream** and **Stop Live Stream** buttons to control the stream.

---
