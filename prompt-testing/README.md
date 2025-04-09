# Advertisement Detection Prompt Testing

Welcome to the Advertisement Detection Prompt Testing project! Follow the steps below to set up and run the application.

## Setup Instructions

1. **Install Dependencies**
    Run the following command to install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

2. **Configure API Keys**
    Open the `oracle.py` file and fill in Gemini's API keys.

3. **Update IP Range and Password Hash**
    Open the `app.py` file.
    - Line 27 contains the allowed IP range.
    - Line 100 contains the SHA-256 hash of the password, which is currently set to `test`.