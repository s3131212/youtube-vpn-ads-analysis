# Video Downloader and Transcript Generator
This project is designed to assist in downloading YouTube videos and generating their transcripts using OpenAI Whisper.

## Features
- Retrieve all YouTube videos within a specific date range from specific channels.
- Download YouTube videos.
- Generate transcripts for downloaded videos using OpenAI Whisper.

## How to Use

1. Clone the repository.
2. Install dependencies:
    ```bash
    pip install yt-dlp openai-whisper
    ```
3. Retrieve video URLs from channels:
    ```bash
    python extract_channel_urls
    ```
    - This will create a `video_url_list.json` file containing the URLs of the videos.
    - To modify channels or the date range, update the `CHANNELS` and `WITHIN_N_DAYS` variables in the script.
4. Download videos:
    ```bash
    python download_videos.py
    ```
5. Generate transcripts for the downloaded videos:
    ```bash
    python transcript.py
    ```