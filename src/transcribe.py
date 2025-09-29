#!/usr/bin/env python3
"""Local transcription helper wrapping ffmpeg and the Whisper CLI."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert a media file to normalized WAV and transcribe it with Whisper CLI."
    )
    parser.add_argument(
        "input_path",
        type=Path,
        help="Path to the source audio/video file",
    )
    parser.add_argument(
        "--model",
        default="medium",
        help="Whisper model size to use (default: medium)",
    )
    parser.add_argument(
        "--model-dir",
        type=Path,
        default=None,
        help="Optional path to cache Whisper models",
    )
    parser.add_argument(
        "--language",
        default=None,
        help="Optional language override for Whisper (e.g. 'en')",
    )
    parser.add_argument(
        "--task",
        choices=["transcribe", "translate"],
        default="transcribe",
        help="Whisper task to run",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Directory for Whisper outputs (defaults to input directory)",
    )
    parser.add_argument(
        "--output-format",
        choices=["txt", "json", "srt", "vtt", "tsv"],
        default="txt",
        help="Output transcription format",
    )
    parser.add_argument(
        "--date-prefix",
        default=datetime.now().strftime("%Y-%m-%d"),
        help="Prefix for output filenames (default: today's date)",
    )
    parser.add_argument(
        "--keep-intermediate",
        action="store_true",
        help="Keep the normalized WAV file instead of deleting the temp file",
    )
    parser.add_argument(
        "--sample-rate",
        type=int,
        default=16000,
        help="Sample rate for normalization (default: 16000)",
    )
    parser.add_argument(
        "--channels",
        type=int,
        default=1,
        help="Number of audio channels for normalization (default: 1)",
    )
    return parser.parse_args()


def ensure_dependency(name: str) -> None:
    if shutil.which(name) is None:
        sys.exit(f"Dependency '{name}' not found on PATH. Please install it and retry.")


def normalize_audio(input_path: Path, sample_rate: int, channels: int, dest: Path) -> Path:
    normalized = dest / f"{input_path.stem}_normalized.wav"
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(input_path),
        "-ac",
        str(channels),
        "-ar",
        str(sample_rate),
        str(normalized),
    ]
    subprocess.run(cmd, check=True)
    return normalized


def run_whisper(
    wav_path: Path,
    model: str,
    model_dir: Path | None,
    output_dir: Path,
    output_format: str,
    language: str | None,
    task: str,
) -> None:
    cmd = [
        "whisper",
        str(wav_path),
        "--model",
        model,
        "--output_dir",
        str(output_dir),
        "--output_format",
        output_format,
        "--task",
        task,
    ]
    if model_dir is not None:
        cmd.extend(["--model_dir", str(model_dir)])
    if language is not None:
        cmd.extend(["--language", language])
    subprocess.run(cmd, check=True)


def main() -> None:
    args = parse_args()

    ensure_dependency("ffmpeg")
    ensure_dependency("whisper")

    input_path = args.input_path.expanduser().resolve()
    if not input_path.exists():
        sys.exit(f"Input file not found: {input_path}")

    output_dir = (args.output_dir or input_path.parent).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    temp_dir = tempfile.TemporaryDirectory() if not args.keep_intermediate else None
    work_dir = Path(temp_dir.name) if temp_dir else output_dir

    try:
        wav_path = normalize_audio(input_path, args.sample_rate, args.channels, work_dir)
        run_whisper(
            wav_path=wav_path,
            model=args.model,
            model_dir=args.model_dir,
            output_dir=output_dir,
            output_format=args.output_format,
            language=args.language,
            task=args.task,
        )
        produced_file = output_dir / f"{wav_path.stem}.{args.output_format}"
        target_name = f"{args.date_prefix}-{args.input_path.stem}.{args.output_format}"
        target_file = output_dir / target_name
        if produced_file.exists():
            target_file.parent.mkdir(parents=True, exist_ok=True)
            produced_file.replace(target_file)
            print(f"Transcription saved to: {target_file}")
        else:
            print(
                f"Warning: Expected output not found: {produced_file}",
                file=sys.stderr,
            )
        if temp_dir is None:
            print(f"Normalized audio kept at: {wav_path}")
    except subprocess.CalledProcessError as err:
        sys.exit(f"Command failed with exit code {err.returncode}: {' '.join(err.cmd)}")
    finally:
        if temp_dir is not None:
            temp_dir.cleanup()


if __name__ == "__main__":
    main()
