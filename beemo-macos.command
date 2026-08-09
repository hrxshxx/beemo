#!/bin/bash
# Beemo launcher for macOS. Double-click this file.
# Sets up its own environment on first run, then starts the web UI.

cd "$(dirname "$0")" || exit 1

BOLD=$'\033[1m'; DIM=$'\033[2m'; RESET=$'\033[0m'
GREEN=$'\033[32m'; YELLOW=$'\033[33m'; RED=$'\033[31m'

say()  { printf "%s\n" "$1"; }
ok()   { printf "  ${GREEN}✓${RESET} %s\n" "$1"; }
warn() { printf "  ${YELLOW}!${RESET} %s\n" "$1"; }
die()  { printf "  ${RED}✗${RESET} %s\n\n" "$1"; printf "Press return to close."; read -r _; exit 1; }

clear 2>/dev/null || true
say ""
say "  ${BOLD}beemo${RESET}"
say "  ${DIM}ambient intelligence that lives on your machine${RESET}"
say ""

# ---------- Python ----------
PY=""
for candidate in python3.12 python3.11 python3; do
  if command -v "$candidate" >/dev/null 2>&1; then PY="$candidate"; break; fi
done
[ -z "$PY" ] && die "Python 3 not found. Install it from https://www.python.org/downloads/ and run this again."
ok "python — $($PY --version 2>&1)"

# ---------- Homebrew-installed helpers ----------
if ! command -v mpv >/dev/null 2>&1; then
  warn "mpv not found — music playback will not work."
  say "    ${DIM}install with:  brew install mpv${RESET}"
else
  ok "mpv"
fi

# ---------- virtualenv ----------
if [ ! -d ".venv" ]; then
  say ""
  say "  ${DIM}First run — creating a private environment. This takes a minute.${RESET}"
  "$PY" -m venv .venv || die "Could not create the virtual environment."
fi

VENV_PY=".venv/bin/python"
[ -x "$VENV_PY" ] || die "The environment in .venv looks broken. Delete the .venv folder and run this again."

say "  ${DIM}checking dependencies…${RESET}"
"$VENV_PY" -m pip install --quiet --upgrade pip >/dev/null 2>&1
if ! "$VENV_PY" -m pip install --quiet -r requirements.txt; then
  say ""
  warn "Some dependencies failed to install."
  say "    ${DIM}pyaudio needs portaudio:  brew install portaudio${RESET}"
  die "Fix the above and run this again."
fi
ok "dependencies"

# ---------- API keys ----------
if [ ! -f ".env" ]; then
  say ""
  say "  ${BOLD}One-time setup${RESET} — beemo needs three free API keys."
  say "  ${DIM}They are saved to a local .env file and never leave this machine.${RESET}"
  say ""
  say "    openai        ${DIM}https://platform.openai.com/api-keys${RESET}"
  printf "    ${BOLD}paste key:${RESET} "; read -r OPENAI_KEY
  say ""
  say "    openweathermap ${DIM}https://openweathermap.org/api${RESET}"
  printf "    ${BOLD}paste key:${RESET} "; read -r WEATHER_KEY
  say ""
  say "    newsdata.io   ${DIM}https://newsdata.io/register${RESET}"
  printf "    ${BOLD}paste key:${RESET} "; read -r NEWS_KEY
  say ""
  printf "    ${BOLD}morning briefing time (HH:MM, default 08:00):${RESET} "; read -r BRIEF
  [ -z "$BRIEF" ] && BRIEF="08:00"

  {
    echo "OPENAI_API_KEY=$OPENAI_KEY"
    echo "OPENWEATHERMAP_KEY=$WEATHER_KEY"
    echo "NEWS_API_KEY=$NEWS_KEY"
    echo "BRIEFING_TIME=$BRIEF"
    echo "NEWS_COUNTRY=us"
  } > .env
  chmod 600 .env
  ok "keys saved to .env"
fi

# ---------- Ollama ----------
say ""
if ! command -v ollama >/dev/null 2>&1; then
  warn "Ollama not found — beemo's brain runs on it."
  say "    ${DIM}install from https://ollama.com/download, then run this again${RESET}"
  die "Ollama is required."
fi
ok "ollama"

if ! curl -s --max-time 2 http://localhost:11434/api/tags >/dev/null 2>&1; then
  say "  ${DIM}starting ollama…${RESET}"
  ollama serve >/dev/null 2>&1 &
  for _ in 1 2 3 4 5 6 7 8 9 10; do
    sleep 1
    curl -s --max-time 2 http://localhost:11434/api/tags >/dev/null 2>&1 && break
  done
fi
curl -s --max-time 2 http://localhost:11434/api/tags >/dev/null 2>&1 \
  || die "Ollama would not start. Try running 'ollama serve' in a terminal."
ok "ollama running"

if ! ollama list 2>/dev/null | grep -q "llama3.2"; then
  say ""
  say "  ${DIM}downloading the llama3.2 model (about 2 GB, one time)…${RESET}"
  ollama pull llama3.2 || die "Could not download the model."
fi
ok "llama3.2"

# ---------- go ----------
say ""
say "  ${BOLD}beemo is starting${RESET} — ${DIM}http://127.0.0.1:8000${RESET}"
say "  ${DIM}close this window to stop it${RESET}"
say ""

( sleep 2; open "http://127.0.0.1:8000" ) &
"$VENV_PY" server.py

say ""
printf "Press return to close."
read -r _
