# Helper: Local Transcription CLI

A tiny terminal helper that cleans up audio/video with `ffmpeg` and transcribes it locally using the Whisper CLI (small model by default).

## Setup
Install `ffmpeg` and [uv](https://github.com/astral-sh/uv) (e.g. `pip install uv` or `brew install uv`). Then create a virtualenv and sync dependencies:
```bash
uv venv
source .venv/bin/activate
uv pip sync requirements.txt
whisper --model small --download-only
```
Prefer pip? You can swap the sync step with `pip install -r requirements.txt`, but `uv` keeps the git dependency reproducible.

## Usage
```bash
uv run python src/transcribe.py path/to/recording.mp3 --output-dir transcripts/
```
Key flags: `--model`, `--language`, `--output-format`, `--keep-intermediate`. Run `python src/transcribe.py --help` for details.

### Batch a folder
Transcribe everything inside `inputs/` (or any folder) with a simple shell loop:
```bash
for file in inputs/*; do
  uv run python src/transcribe.py "$file" --output-dir output --date-prefix $(date +%F)
done
```
Adjust the glob (`inputs/*.mp3`, etc.) and flags as needed.

## Ideas
- Batch mode for entire folders
- Richer CLI (Typer/Click)
- Timestamped summaries
