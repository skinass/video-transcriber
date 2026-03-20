<!--
Sync Impact Report
- Version change: 0.0.0 → 1.0.0
- Added principles: Simplicity, Zero-Config Start, Transcription Quality, Hardware Adaptability
- Added sections: Technical Constraints, Development Workflow
- Templates requiring updates: ✅ plan-template.md (no changes needed), ✅ spec-template.md (no changes needed), ✅ tasks-template.md (no changes needed)
- Follow-up TODOs: none
-->

# Video Transcriber Constitution

## Core Principles

### I. Simplicity

The project MUST remain a single-script utility. All transcription logic lives in `transcribe.py`.
New features MUST NOT introduce frameworks, class hierarchies, or multi-module architectures
unless the single-file approach becomes genuinely unmaintainable.
Rationale: this is a personal tool, not a library or service. Complexity kills usability.

### II. Zero-Config Start

A user MUST be able to clone the repo, drop video files into `raw/`, and run `run.bat` with
no prior setup. The batch file MUST handle venv creation, dependency installation, and script
execution automatically. No manual `pip install`, no environment variables, no external
toolchain required beyond Python itself.

### III. Transcription Quality

Transcription output MUST be as accurate and faithful as possible:
- Uncensored output: profanity MUST NOT be masked or filtered.
- Context-aware prompts: when the filename signals a specific domain (e.g. CS:GO),
  the `initial_prompt` MUST include domain-specific vocabulary to guide Whisper.
- One segment per line: output files MUST contain one Whisper segment per line,
  not a single block of text.
- New domain prompts SHOULD be added when a recurring content type benefits from
  specialized vocabulary.

### IV. Hardware Adaptability

The tool MUST auto-detect available hardware and use the fastest option:
- NVIDIA GPU with CUDA → load model on `cuda`.
- No GPU → fall back to CPU transparently.
- The user MUST NOT need to configure hardware manually.
  `run.bat` installs the CUDA-enabled PyTorch build; the script detects the device at runtime.

## Technical Constraints

- **Language**: Python 3.8+
- **Dependencies**: openai-whisper, torch (cu128), imageio-ffmpeg, pyyaml.
  All installed into a local `venv/` by `run.bat`.
- **Config**: `transcribe.yaml` — YAML with `source`, `destination`, `model`, `language`.
- **Platform**: Windows primary (batch file entrypoint). Script itself is cross-platform.
- **ffmpeg**: Bundled via `imageio-ffmpeg` with a monkey-patch in `transcribe.py`
  because Whisper expects a bare `ffmpeg` binary on PATH.

## Development Workflow

- All changes MUST be tested by running `transcribe.py` against real video files before commit.
- Commits and pushes MUST only happen when the user explicitly requests them.
- The `raw/` and `subtitles/` directories are tracked via `.gitkeep` but their contents
  are gitignored. Never commit media or transcription output files.
- CLAUDE.md and README.md MUST be kept in sync with actual project behavior.

## Governance

This constitution defines the non-negotiable principles for the Video Transcriber project.
Amendments require updating this file and incrementing the version. Any change that removes
or redefines an existing principle is a MAJOR version bump. Adding a new principle or
expanding guidance is MINOR. Wording fixes are PATCH.

**Version**: 1.0.0 | **Ratified**: 2026-03-20 | **Last Amended**: 2026-03-20
