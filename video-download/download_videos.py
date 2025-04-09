import yt_dlp
from pprint import pprint
import json
from pathlib import Path
from multiprocessing import Pool, Manager

NUM_WORKERS = 12

def download_video(data):
    channel_name, video_url = data

    channel_dir = Path('videos/' + channel_name)
    channel_dir.mkdir(parents=True, exist_ok=True)

    ydl_opts = {
        'format': 'mp3/bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }],
        'outtmpl': f'{channel_dir}/%(title)s.%(ext)s'
        # 'daterange': yt_dlp.utils.DateRange('20240815', '99991231')
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            # Save video information to a JSON file
            info = ydl.extract_info(video_url, download=True)
            video_title = info.get('title')
            info_path = channel_dir / f'{video_title}.json'
            info_path.write_text(json.dumps(info, indent=4, ensure_ascii=False))

            # Download video
            ydl.download(video_url)

        print(f"Downloaded and saved: {video_title} ({video_url}) in {channel_name}")

    except Exception as e:
        print(f"Error downloading video {video_url} from channel {channel_name}: {e}")
        return False

    return True

def main():
    with open('video_url_list.json', 'r', encoding='utf-8') as f:
        video_url_list = json.load(f)

    download_tasks = [(channel, url) for channel, urls in video_url_list.items() for url in urls]

    with Pool(processes=NUM_WORKERS) as pool:
        pool.map(download_video, download_tasks)


    print("All videos downloaded successfully.")

if __name__ == "__main__":
    main()
