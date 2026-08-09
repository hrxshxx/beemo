@echo off
REM Beemo launcher for Windows. Double-click this file.
REM Sets up its own environment on first run, then starts the web UI.

setlocal enabledelayedexpansion
cd /d "%~dp0"

cls
echo.
echo   beemo
echo   ambient intelligence that lives on your machine
echo.

REM ---------- Python ----------
set "PY="
where py >nul 2>&1 && set "PY=py -3"
if not defined PY (
  where python >nul 2>&1 && set "PY=python"
)
if not defined PY (
  echo   [X] Python 3 not found.
  echo       Install it from https://www.python.org/downloads/
  echo       Tick "Add Python to PATH" during setup, then run this again.
  echo.
  pause
  exit /b 1
)
for /f "delims=" %%v in ('%PY% --version 2^>^&1') do echo   [ok] python - %%v

REM ---------- mpv ----------
where mpv >nul 2>&1
if errorlevel 1 (
  echo   [!] mpv not found - music playback will not work.
  echo       install with:  winget install mpv
) else (
  echo   [ok] mpv
)

REM ---------- virtualenv ----------
if not exist ".venv" (
  echo.
  echo   First run - creating a private environment. This takes a minute.
  %PY% -m venv .venv
  if errorlevel 1 (
    echo   [X] Could not create the virtual environment.
    echo.
    pause
    exit /b 1
  )
)

set "VENV_PY=.venv\Scripts\python.exe"
if not exist "%VENV_PY%" (
  echo   [X] The environment in .venv looks broken.
  echo       Delete the .venv folder and run this again.
  echo.
  pause
  exit /b 1
)

echo   checking dependencies...
"%VENV_PY%" -m pip install --quiet --upgrade pip >nul 2>&1
"%VENV_PY%" -m pip install --quiet -r requirements.txt
if errorlevel 1 (
  echo.
  echo   [!] Some dependencies failed to install.
  echo       pyaudio often needs a prebuilt wheel on Windows:
  echo       "%VENV_PY%" -m pip install pipwin ^&^& pipwin install pyaudio
  echo.
  pause
  exit /b 1
)
echo   [ok] dependencies

REM ---------- API keys ----------
if not exist ".env" (
  echo.
  echo   One-time setup - beemo needs three free API keys.
  echo   They are saved to a local .env file and never leave this machine.
  echo.
  echo     openai          https://platform.openai.com/api-keys
  set /p OPENAI_KEY=    paste key:
  echo.
  echo     openweathermap  https://openweathermap.org/api
  set /p WEATHER_KEY=    paste key:
  echo.
  echo     newsdata.io     https://newsdata.io/register
  set /p NEWS_KEY=    paste key:
  echo.
  set /p BRIEF=    morning briefing time (HH:MM, default 08:00):
  if "!BRIEF!"=="" set "BRIEF=08:00"

  (
    echo OPENAI_API_KEY=!OPENAI_KEY!
    echo OPENWEATHERMAP_KEY=!WEATHER_KEY!
    echo NEWS_API_KEY=!NEWS_KEY!
    echo BRIEFING_TIME=!BRIEF!
    echo NEWS_COUNTRY=us
  ) > .env
  echo   [ok] keys saved to .env
)

REM ---------- Ollama ----------
echo.
where ollama >nul 2>&1
if errorlevel 1 (
  echo   [X] Ollama not found - beemo's brain runs on it.
  echo       Install from https://ollama.com/download, then run this again.
  echo.
  pause
  exit /b 1
)
echo   [ok] ollama

curl -s --max-time 2 http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
  echo   starting ollama...
  start "" /b ollama serve >nul 2>&1
  for /l %%i in (1,1,10) do (
    timeout /t 1 /nobreak >nul
    curl -s --max-time 2 http://localhost:11434/api/tags >nul 2>&1
    if not errorlevel 1 goto ollama_up
  )
)
:ollama_up
curl -s --max-time 2 http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
  echo   [X] Ollama would not start. Try running "ollama serve" in a terminal.
  echo.
  pause
  exit /b 1
)
echo   [ok] ollama running

ollama list 2>nul | findstr /c:"llama3.2" >nul
if errorlevel 1 (
  echo.
  echo   downloading the llama3.2 model ^(about 2 GB, one time^)...
  ollama pull llama3.2
  if errorlevel 1 (
    echo   [X] Could not download the model.
    echo.
    pause
    exit /b 1
  )
)
echo   [ok] llama3.2

REM ---------- go ----------
echo.
echo   beemo is starting - http://127.0.0.1:8000
echo   close this window to stop it
echo.

start "" http://127.0.0.1:8000
"%VENV_PY%" server.py

echo.
pause
