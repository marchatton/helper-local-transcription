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


def normalize_audio(
    input_path: Path, sample_rate: int, channels: int, dest: Path
) -> Path:
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


def transcribe_file(
    *,
    input_path: Path,
    model: str,
    model_dir: Path | None,
    output_dir: Path,
    output_format: str,
    language: str | None,
    task: str,
    date_prefix: str,
    sample_rate: int,
    channels: int,
    keep_intermediate: bool,
) -> None:
    input_path = input_path.expanduser().resolve()
    if not input_path.exists():
        sys.exit(f"Input file not found: {input_path}")

    resolved_output_dir = output_dir.expanduser().resolve()
    resolved_output_dir.mkdir(parents=True, exist_ok=True)

    model_dir = model_dir.expanduser().resolve() if model_dir else None

    temp_dir: tempfile.TemporaryDirectory[str] | None = None
    if not keep_intermediate:
        temp_dir = tempfile.TemporaryDirectory()
        work_dir = Path(temp_dir.name)
    else:
        work_dir = resolved_output_dir

    try:
        wav_path = normalize_audio(input_path, sample_rate, channels, work_dir)
        run_whisper(
            wav_path=wav_path,
            model=model,
            model_dir=model_dir,
            output_dir=resolved_output_dir,
            output_format=output_format,
            language=language,
            task=task,
        )
        produced_file = resolved_output_dir / f"{wav_path.stem}.{output_format}"
        target_name = f"{date_prefix}-{input_path.stem}.{output_format}"
        target_file = resolved_output_dir / target_name
        if produced_file.exists():
            produced_file.replace(target_file)
            print(f"Transcription saved to: {target_file}")
        else:
            print(
                f"Warning: Expected output not found: {produced_file}",
                file=sys.stderr,
            )
        if keep_intermediate:
            print(f"Normalized audio kept at: {wav_path}")
    except subprocess.CalledProcessError as err:
        sys.exit(f"Command failed with exit code {err.returncode}: {' '.join(err.cmd)}")
    finally:
        if temp_dir is not None:
            temp_dir.cleanup()


def main() -> None:
    args = parse_args()

    ensure_dependency("ffmpeg")
    ensure_dependency("whisper")

    output_dir = args.output_dir or args.input_path.parent

    transcribe_file(
        input_path=args.input_path,
        model=args.model,
        model_dir=args.model_dir,
        output_dir=output_dir,
        output_format=args.output_format,
        language=args.language,
        task=args.task,
        date_prefix=args.date_prefix,
        sample_rate=args.sample_rate,
        channels=args.channels,
        keep_intermediate=args.keep_intermediate,
    )


if __name__ == "__main__":
    main()
