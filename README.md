# Helper: Local Transcription CLI

A tiny terminal helper that cleans up audio/video with `ffmpeg` and transcribes it locally using the Whisper CLI (small model by default).

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt  # currently empty, kept for future deps
```
Install `ffmpeg` and the Whisper CLI (`pip install git+https://github.com/openai/whisper.git`), then cache the model once: `whisper --model small --download-only`.

## Usage
```bash
python src/transcribe.py path/to/recording.mp3 --output-dir transcripts/
```
Key flags: `--model`, `--language`, `--output-format`, `--keep-intermediate`. Run `python src/transcribe.py --help` for details.

### Batch a folder
Transcribe everything inside `inputs/` (or any folder) with a simple shell loop:
```bash
for file in inputs/*; do
  python src/transcribe.py "$file" --output-dir output --date-prefix $(date +%F)
done
```
Adjust the glob (`inputs/*.mp3`, etc.) and flags as needed.

## Ideas
- Batch mode for entire folders
- Richer CLI (Typer/Click)
- Timestamped summaries
