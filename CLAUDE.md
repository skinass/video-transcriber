# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

A video transcription tool that processes video files and generates subtitle files.

## Directory Structure

- `raw/` — input video files to be transcribed
- `subtitles/` — output subtitle files produced by transcription

## Setup

```bash
pip install openai-whisper pyyaml
```

## Running

```bash
python transcribe.py
```

## Configuration (`transcribe.yaml`)

| Key | Default | Description |
|-----|---------|-------------|
| `source` | `raw` | Folder with input video files |
| `destination` | `subtitles` | Folder for output `.txt` files |
| `model` | `base` | Whisper model: `tiny`, `base`, `small`, `medium`, `large` |
| `language` | `null` | Force language (e.g. `"ru"`), or `null` for auto-detect |

## How It Works

1. Reads `transcribe.yaml` for config
2. Scans `source/` for video files; skips any that already have a `.txt` in `destination/`
3. Loads the Whisper model once, then transcribes all pending files
4. Writes `destination/<stem>.txt` for each video
