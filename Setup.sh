#!/usr/bin/env bash
set -e

python3 -m venv .venv

source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "Virtual environment created and dependencies installed."
echo "Run: source .venv/bin/activate"
echo "Then: ./run_demo.sh or ./run_mcp.sh"
