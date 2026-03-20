#!/usr/bin/env python3
import sys
import numpy as np
from pathlib import Path
from subprocess import run as _run
import yaml
import imageio_ffmpeg
import whisper
import whisper.audio as _whisper_audio

# Whisper calls "ffmpeg" by name, but imageio_ffmpeg ships it under a versioned name.
# Monkey-patch load_audio to use the full binary path instead.
_FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()

def _load_audio(file: str, sr: int = _whisper_audio.SAMPLE_RATE) -> np.ndarray:
    cmd = [_FFMPEG_EXE, "-nostdin", "-threads", "0", "-i", file,
           "-f", "s16le", "-ac", "1", "-acodec", "pcm_s16le", "-ar", str(sr), "-"]
    out = _run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(out, np.int16).flatten().astype(np.float32) / 32768.0

_whisper_audio.load_audio = _load_audio

VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".webm", ".flv", ".m4v", ".wmv"}
CONFIG_FILE = Path(__file__).parent / "transcribe.yaml"


def load_config():
    with open(CONFIG_FILE, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    base = Path(__file__).parent
    source = base / cfg.get("source", "raw")
    destination = base / cfg.get("destination", "subtitles")
    model_name = cfg.get("model", "base")
    language = cfg.get("language") or None
    return source, destination, model_name, language


def find_pending(source: Path, destination: Path):
    pending = []
    for video in sorted(source.iterdir()):
        if video.suffix.lower() in VIDEO_EXTENSIONS:
            out = destination / (video.stem + ".txt")
            if not out.exists():
                pending.append(video)
    return pending


INITIAL_PROMPT = (
    "Транскрибируй дословно, включая ненормативную лексику без цензуры. "
    "блять, пиздец, хуй, пизда, ёбаный, сука, мразь, пидор"
)

CSGO_PROMPT = (
    "Это запись игры в CS:GO. Транскрибируй дословно, включая ненормативную лексику без цензуры. "
    "блять, пиздец, хуй, пизда, ёбаный, сука, мразь, пидор. "
    "Игровой сленг: авп, АВП, AWP, петух, раш, смоук, смок, флэш, дроп, кит, пуш, хол, холд, "
    "пик, пикнуть, ротация, эко, форс, сейв, клатч, эйс, тимкилл, кемпер, ваншот, хедшот, "
    "Т-сайд, КТ-сайд, бомба, плант, дифьюз, тиммейт, ботан, нуб, про, скилл, рейтинг."
)


def transcribe(video: Path, destination: Path, model, language):
    print(f"  Transcribing: {video.name}")
    prompt = CSGO_PROMPT if "csgo" in video.stem.lower() else INITIAL_PROMPT
    result = model.transcribe(
        str(video),
        language=language,
        verbose=False,
        initial_prompt=prompt,
    )
    lines = [seg["text"].strip() for seg in result["segments"] if seg["text"].strip()]
    out = destination / (video.stem + ".txt")
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"  Saved: {out.name}")


def main():
    source, destination, model_name, language = load_config()

    if not source.exists():
        print(f"Source folder not found: {source}")
        sys.exit(1)

    destination.mkdir(parents=True, exist_ok=True)

    pending = find_pending(source, destination)
    if not pending:
        print("Nothing to transcribe — all files already have transcriptions.")
        return

    import torch
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Loading Whisper model '{model_name}' on {device.upper()}...")
    model = whisper.load_model(model_name, device=device)

    print(f"\nFound {len(pending)} file(s) to transcribe:\n")
    for video in pending:
        transcribe(video, destination, model, language)

    print("\nDone.")


if __name__ == "__main__":
    main()
