@echo off
REM Aetheris launcher for Windows.
setlocal
if not exist ".venv\Scripts\python.exe" (
  echo Creating virtual environment...
  python -m venv .venv || goto :error
)
call ".venv\Scripts\activate.bat"
python -m pip install --quiet --upgrade pip
python -m pip install --quiet -r requirements.txt || goto :error
if "%FLASK_DEBUG%"=="" set FLASK_DEBUG=1
if "%PORT%"=="" set PORT=5000
echo Starting Aetheris on http://127.0.0.1:%PORT%
python app.py
goto :eof

:error
echo Failed to start Aetheris.
exit /b 1
