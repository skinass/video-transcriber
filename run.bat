@echo off
setlocal

set VENV_DIR=%~dp0venv

if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv "%VENV_DIR%"
)

call "%VENV_DIR%\Scripts\activate.bat"

echo Installing dependencies...
python -m pip install --quiet torch --index-url https://download.pytorch.org/whl/cu128
python -m pip install --quiet openai-whisper pyyaml imageio-ffmpeg

echo.
echo Starting transcription...
python "%~dp0transcribe.py"

echo.
pause
