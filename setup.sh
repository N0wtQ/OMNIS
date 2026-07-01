#!/usr/bin/env bash
# OMNIS — Tool installation script
set -euo pipefail

echo "═══════════════════════════════════════════════"
echo "  OMNIS — Installing open-source tools"
echo "═══════════════════════════════════════════════"

TOOLS_DIR="$(cd "$(dirname "$0")" && pwd)/tools"
mkdir -p "$TOOLS_DIR"

# Python dependencies
echo "[*] Installing Python dependencies..."
pip install -r requirements.txt --quiet

# theHarvester
if [ ! -d "$TOOLS_DIR/theHarvester" ]; then
  echo "[*] Cloning theHarvester..."
  git clone --depth 1 https://github.com/laramies/theHarvester "$TOOLS_DIR/theHarvester"
  pip install -r "$TOOLS_DIR/theHarvester/requirements/base.txt" --quiet
fi

# SpiderFoot
if [ ! -d "$TOOLS_DIR/spiderfoot" ]; then
  echo "[*] Cloning SpiderFoot..."
  git clone --depth 1 https://github.com/smicallef/spiderfoot "$TOOLS_DIR/spiderfoot"
  pip install -r "$TOOLS_DIR/spiderfoot/requirements.txt" --quiet
fi

# Sherlock
if ! command -v sherlock &>/dev/null; then
  echo "[*] Installing Sherlock..."
  pip install sherlock-project --quiet
fi

# Maigret
if ! command -v maigret &>/dev/null; then
  echo "[*] Installing Maigret..."
  pip install maigret --quiet
fi

# osint-mcp-server
if [ ! -d "$TOOLS_DIR/osint-mcp-server" ]; then
  echo "[*] Cloning osint-mcp-server..."
  git clone --depth 1 https://github.com/badchars/osint-mcp-server "$TOOLS_DIR/osint-mcp-server" || true
fi

# shohei
if [ ! -d "$TOOLS_DIR/shohei" ]; then
  echo "[*] Cloning shohei..."
  git clone --depth 1 https://github.com/kent-tokyo/shohei "$TOOLS_DIR/shohei" || true
fi

# awesome-osint-arsenal
if [ ! -d "$TOOLS_DIR/awesome-osint-arsenal" ]; then
  echo "[*] Cloning awesome-osint-arsenal..."
  git clone --depth 1 https://github.com/cipher387/awesome-osint-arsenal "$TOOLS_DIR/awesome-osint-arsenal" || true
fi

echo ""
echo "═══════════════════════════════════════════════"
echo "  OMNIS tools installation complete."
echo "  Run: python omnis.py <target>"
echo "═══════════════════════════════════════════════"
