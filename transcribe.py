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

VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".webm", ".flv", ".m4v", ".wmv", ".mpg", ".mpeg"}
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
            out = destination / (video.stem + ".srt")
            if not out.exists():
                pending.append(video)
    return pending


def format_srt_time(seconds: float) -> str:
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1_000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


INITIAL_PROMPT = (
    "Транскрибируй дословно, включая ненормативную лексику без цензуры. "
    "блять, пиздец, хуй, пизда, ёбаный, сука, мразь, пидор"
)

CSGO_PROMPT = (
    "Это запись игры в CS:GO. Транскрибируй дословно, включая ненормативную лексику без цензуры. "
    "блять, пиздец, хуй, пизда, ёбаный, сука, мразь, пидор. "
    "Оружие: AWP, АВП, AK-47, калаш, MP7, глок, дигл, дробовик, нож. "
    "Гранаты: флешка, дым, молотов, граната, зажигалка. "
    "Механики: раш, рашить, сейв, сейвить, форс, форс-байлаут, эко, буст, дроп, "
    "плант, дефуз, дефузить, пик, пикать, холд, пуш, кемп, клатч, эйс, хедшот, ваншот, тимкилл. "
    "Callouts карты Cache: мид, вент, мэйн, токсик, А-сайт, Б-сайт, КТ-спаун, форклифт, гараж, ящики. "
    "Общее: КТ, тиммейт, респ, спаун, репорт, вак-бан, читы, рейтинг, скилл, нуб, про."
)


HALLUCINATION_PATTERNS = [
    "субтитры сделал",
    "субтитры делал",
    "субтитры создал",
    "titulky",
    "amara.org",
    "подписывайтесь на канал",
    "не забудьте подписаться",
]


def is_hallucination(text: str) -> bool:
    lower = text.lower()
    return any(p in lower for p in HALLUCINATION_PATTERNS)


def transcribe(video: Path, destination: Path, model, language):
    print(f"  Transcribing: {video.name}")
    prompt = CSGO_PROMPT if "csgo" in video.stem.lower() else INITIAL_PROMPT
    result = model.transcribe(
        str(video),
        language=language,
        verbose=False,
        initial_prompt=prompt,
    )
    blocks = []
    for i, seg in enumerate(result["segments"], start=1):
        text = seg["text"].strip()
        if not text or is_hallucination(text):
            continue
        start = format_srt_time(seg["start"])
        end = format_srt_time(seg["end"])
        blocks.append(f"{i}\n{start} --> {end}\n{text}")
    out = destination / (video.stem + ".srt")
    out.write_text("\n\n".join(blocks) + "\n", encoding="utf-8")
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
