import whisper
from pathlib import Path
import os
from tqdm import tqdm

# Load the Whisper model (large version)
model = whisper.load_model("large")

def transcribe_audio(audio_path):
    result = model.transcribe(str(audio_path), fp16=False)
    transcript = " ".join([segment['text'] for segment in result['segments']])

    transcript_file = audio_path.with_suffix('.txt')
    with open(transcript_file, "w", encoding="utf-8") as f:
        f.write(transcript)

    print(f"Transcript saved to {transcript_file}")

def main():
    base_dir = Path("./videos")

    audio_files = list(base_dir.rglob("*.mp3"))

    if not audio_files:
        print("No audio files found.")
        return

    for audio_file in tqdm(audio_files):
        transcribe_audio(audio_file)

    print("All transcripts generated successfully.")

if __name__ == "__main__":
    main()
