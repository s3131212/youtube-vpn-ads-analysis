import yt_dlp
from pprint import pprint
import json
from pathlib import Path
from datetime import datetime, timedelta
from multiprocessing import Pool, Manager
import traceback

CHANNELS = {
    '叉雞': 'https://www.youtube.com/@bbqporkchicken/videos',
    '波特王好帥': 'https://www.youtube.com/channel/UCsBP1dmKYfcorJ17kfOUTvg/videos',
    '啾啾鞋': 'https://www.youtube.com/@chuchushoeTW/videos',
    'Joeman': 'https://www.youtube.com/@joeman/videos',
    '77老大': 'https://www.youtube.com/@77boss/videos',
    '阿滴英文': 'https://www.youtube.com/@rayduenglish/videos',
    '蔡阿嘎': 'https://www.youtube.com/@TsaiAGa/videos',
    '木曜4超玩': 'https://www.youtube.com/@Muyao4/videos',
    '黃氏兄弟': 'https://www.youtube.com/@%E9%BB%83%E6%B0%8F%E5%85%84%E5%BC%9F/videos',
    'Ku\'s dream酷的夢': 'https://www.youtube.com/@Kusdream/videos'
}

WITHIN_N_DAYS = 180

def fetch_videos(channel_data):
    channel_name, channel_url = channel_data
    video_counter = 1
    eariliest_video_time = datetime.now()
    videos = []

    while eariliest_video_time > datetime.now() - timedelta(days=WITHIN_N_DAYS):
        try:
            with yt_dlp.YoutubeDL({'playlist_items': str(video_counter)}) as ydl:
                infos = ydl.extract_info(channel_url, download=False)
                infos = ydl.sanitize_info(infos)

            video_info = infos['entries'][0]
            video_url = video_info.get('webpage_url')
            video_title = video_info.get('title')
            upload_date = video_info.get('upload_date')

            print(f"[{channel_name}] - {video_title} ({upload_date}) - {video_url}")

            eariliest_video_time = datetime.strptime(upload_date, '%Y%m%d')

            if eariliest_video_time > datetime.now() - timedelta(days=WITHIN_N_DAYS):
                videos.append(video_url)

            video_counter += 1

        except Exception as e:
            print(f"Error processing {channel_name}: {str(e)}")
            traceback.print_exc()
            break  # Exit loop on error

    return channel_name, videos

def main():
    with Manager() as manager:
        video_url_list = manager.dict()

        with Pool(processes=len(CHANNELS)) as pool:
            results = pool.map(fetch_videos, CHANNELS.items())

        video_url_list.update(dict(results))

        # Save the results to a JSON file
        Path('./video_url_list.json').write_text(json.dumps(dict(video_url_list), indent=4, ensure_ascii=False))

if __name__ == "__main__":
    main()