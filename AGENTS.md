# AGENTS.md (helper-local-transcription)

## Repository Conventions
- Python 3.11 environment; keep the project dependency-free beyond the standard library.
- Format code with `python -m black` if you touch Python files.
- Run `python -m pytest` before committing whenever tests exist or are added.
- Prefer pathlib and type annotations; keep the CLI interface stable unless explicitly requested.
- Keep shell invocations (`ffmpeg`, `whisper`) wrapped via `subprocess.run(..., check=True)` and surface clear error messages.

## Documentation
- Update `README.md` when the CLI behaviour or invocation flags change.
