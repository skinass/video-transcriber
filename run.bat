@echo off
echo Installing dependencies...
python -m pip install openai-whisper pyyaml imageio-ffmpeg

echo.
echo Starting transcription...
python transcribe.py

echo.
pause
