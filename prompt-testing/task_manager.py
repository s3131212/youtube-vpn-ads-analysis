import threading
import time
from oracle import oracle, oracle_return_text
from pathlib import Path
from collections import defaultdict
from sklearn.metrics import accuracy_score, f1_score, classification_report
import pandas as pd
import json
import os

def build_task_list(base_dir: Path, df: pd.DataFrame):

    # Extract the video IDs from the video link column
    df['video_id'] = df['影片連結'].apply(lambda x: x.split('=')[-1])

    # Initialize task list to hold mappings of video_id -> (subtitle_file_path, has_vpn_ad, has_explicit_ad)
    task_list = []
    missing_videos = defaultdict(lambda: list())

    # Iterate over the videos listed in the CSV
    for _, row in df.iterrows():
        video_id = row['video_id']
        channel_name = row['頻道名稱']
        has_vpn_ad = row['是否有 VPN 業配']
        has_explicit_ad = row['是否有明顯的業配']

        channel_dir = base_dir / 'transcript'
        subtitle_found = False
        if channel_dir.is_dir():
            json_file_path = channel_dir / (video_id + ".json")
            if json_file_path.exists():
                # Read the corresponding json metadata
                with json_file_path.open('r', encoding='utf-8') as json_file:
                    metadata = json.load(json_file)

                if video_id == metadata.get("id"):
                    subtitle_file = json_file_path.with_suffix('.txt')
                    if subtitle_file.exists():
                        task_list.append((video_id, subtitle_file, has_vpn_ad, has_explicit_ad))
                        subtitle_found = True

        # If no subtitle file was found, mark this video as missing subtitles
        if not subtitle_found:
            missing_videos[channel_name].append("https://www.youtube.com/watch?v=" + video_id)

    return task_list, missing_videos

def calculate_scores(results):
    # Calculate the accuracy, F1 scores, and classification reports
    results_df = pd.DataFrame(results)

    # Calculate metrics
    vpn_ad_accuracy = accuracy_score(results_df['expected_vpn_ad'], results_df['oracle_vpn_ad'])
    vpn_ad_f1 = f1_score(results_df['expected_vpn_ad'], results_df['oracle_vpn_ad'])
    explicit_ad_accuracy = accuracy_score(results_df['expected_explicit_ad'], results_df['oracle_explicit_ad'])
    explicit_ad_f1 = f1_score(results_df['expected_explicit_ad'], results_df['oracle_explicit_ad'])
    
    vpn_ad_report = classification_report(results_df['expected_vpn_ad'], results_df['oracle_vpn_ad'], target_names=["No VPN Ad", "VPN Ad"])
    explicit_ad_report = classification_report(results_df['expected_explicit_ad'], results_df['oracle_explicit_ad'], target_names=["No Explicit Ad", "Explicit Ad"])

    return {
        'vpn_ad_accuracy': vpn_ad_accuracy,
        'vpn_ad_f1': vpn_ad_f1,
        'explicit_ad_accuracy': explicit_ad_accuracy,
        'explicit_ad_f1': explicit_ad_f1,
        'vpn_ad_report': vpn_ad_report,
        'explicit_ad_report': explicit_ad_report
    }

class TaskManager:
    def __init__(self):
        self.prompts = []
        self.lock = threading.Lock()  # To ensure thread-safe operations

        csv_file_path = './YT VPN Dataset.csv'
        df = pd.read_csv(csv_file_path)
        base_dir = Path('./')
        self.task_list, self.missing_videos = build_task_list(base_dir, df)
        self.record_file_name = "prompt_record.txt"
        if os.path.exists(self.record_file_name):
            with open(self.record_file_name, 'r') as file:
                self.prompts = json.load(file)


    def add_prompt(self, author, single, prompt):
        # Add new prompt to the list (untested)
        with self.lock:
            self.prompts.append({
                'id': len(self.prompts),
                'single': single,
                'prompt': prompt,
                'result': 0,
                'scores': '',
                'author': author
            })
            with open(self.record_file_name, 'w') as json_file:
                json.dump(self.prompts, json_file)

    def get_all_tasks(self):
        # Get the list of all tasks
        # with self.lock:
        prompts = list()
        for prompt in self.prompts:
            prompts.append({
                'id': prompt['id'],
                'prompt_ad': prompt['prompt'][0][:20],
                'prompt_vpn': prompt['prompt'][1][:20],
                'result': prompt['result'] if not isinstance(prompt['result'], dict) else 150,
                'scores': "NA" if not isinstance(prompt['scores'], dict) else prompt['scores']['vpn_ad_accuracy'],
                'author': prompt['author'],
                'single': prompt['single'],
            })
        return prompts

    def get_task_by_id(self, task_id):
        # Fetch a task by its ID
        # with self.lock:
        for prompt in self.prompts:
            if str(prompt['id']) == task_id:
                return prompt
        return None

    def _assign_and_run_oracle(self):
        # This function runs in the background to process untested prompts
        while True:
            with self.lock:
                untested_prompts = [prompt for prompt in self.prompts if not isinstance(prompt['result'], dict)]

            for prompt in untested_prompts:
                # Iterate over the tasks and process each subtitle file
                results = {
                    'video_id': [],
                    'expected_vpn_ad': [],
                    'expected_explicit_ad': [],
                    'oracle_vpn_ad': [],
                    'oracle_explicit_ad': []
                }
                for idx, task in enumerate(self.task_list):
                    prompt['result'] = idx + 1
                    video_id, subtitle_file, expected_vpn_ad, expected_explicit_ad = task
                    subtitle_text = subtitle_file.read_text(encoding='utf-8')

                    # Send the subtitle to the oracle function (assuming it returns two boolean values: has_vpn_ad, has_explicit_ad)
                    if not prompt['single']:
                        if prompt['prompt'][0][:25] == "[AnJ Testing New Feature]":
                            return_text = oracle_return_text(subtitle_text, prompt['prompt'][0][25:])
                            oracle_result_explicit_ad = return_text.strip(" \n") not in ["無。", "无。"]
                            # print(oracle_result_explicit_ad, return_text.strip(" \n"))
                            if oracle_result_explicit_ad:
                                oracle_result_vpn_ad = oracle(return_text, prompt['prompt'][1])
                            else:
                                oracle_result_vpn_ad = False
                        else:    
                            oracle_result_explicit_ad = oracle(subtitle_text, prompt['prompt'][0])
                            if oracle_result_explicit_ad:
                                oracle_result_vpn_ad = oracle(subtitle_text, prompt['prompt'][1])
                            else:
                                oracle_result_vpn_ad = False
                    else:
                        oracle_result_explicit_ad = False
                        oracle_result_vpn_ad = oracle(subtitle_text, prompt['prompt'][1])

                    # Append the results to the results dictionary
                    results['video_id'].append(video_id)
                    results['expected_vpn_ad'].append(expected_vpn_ad)
                    results['expected_explicit_ad'].append(expected_explicit_ad)
                    results['oracle_vpn_ad'].append(oracle_result_vpn_ad)
                    results['oracle_explicit_ad'].append(oracle_result_explicit_ad)

                prompt['result'] = results
                prompt['scores'] = calculate_scores(results)

                with self.lock:
                    with open(self.record_file_name, 'w') as json_file:
                        json.dump(self.prompts, json_file)


    def start_worker(self):
        # Start the background worker thread
        worker_thread = threading.Thread(target=self._assign_and_run_oracle, daemon=False)
        worker_thread.start()

