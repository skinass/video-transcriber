# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

A video transcription tool that processes video files and generates subtitle files using OpenAI Whisper.

## Directory Structure

- `raw/` — input video files to be transcribed
- `subtitles/` — output `.srt` subtitle files (one block per Whisper segment, with timecodes)

## Running

```bash
# Windows — sets up venv, installs deps, runs transcription
run.bat

# Or directly inside the venv
venv/Scripts/python transcribe.py
```

## Configuration (`transcribe.yaml`)

| Key | Default | Description |
|-----|---------|-------------|
| `source` | `raw` | Folder with input video files |
| `destination` | `subtitles` | Folder for output `.srt` files |
| `model` | `small` | Whisper model: `tiny`, `base`, `small`, `medium`, `large` |
| `language` | `ru` | Force language (e.g. `"en"`), or `null` for auto-detect |

## How It Works

1. Reads `transcribe.yaml` for config
2. Scans `source/` for video files; skips any that already have a `.srt` in `destination/`
3. Auto-detects CUDA GPU — loads Whisper model on GPU if available, falls back to CPU
4. Transcribes all pending files; writes SRT with timecodes to `destination/<stem>.srt`

## Prompting Logic

Two `initial_prompt` constants in `transcribe.py`:
- `INITIAL_PROMPT` — default; instructs uncensored transcription
- `CSGO_PROMPT` — used when `"csgo"` appears in the filename (case-insensitive); extends the default with CS:GO game slang

## Dependencies

Installed automatically by `run.bat` into a local `venv/`:
- `openai-whisper` — transcription
- `torch` (cu128) — PyTorch with CUDA 12.8 for GPU acceleration
- `imageio-ffmpeg` — bundles ffmpeg, used via monkey-patch in `transcribe.py` since Whisper calls `ffmpeg` by name
- `pyyaml` — config parsing
