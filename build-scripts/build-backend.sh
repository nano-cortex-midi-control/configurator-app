#!/usr/bin/env bash
set -euo pipefail

# Build PyInstaller onefile backend binary that can run from AppImage (extracts to /tmp)

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

VENV_DIR="$ROOT_DIR/.pyi-venv"

python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

python -m pip install --upgrade pip setuptools wheel
python -m pip install pyinstaller
python -m pip install -r backend/requirements.txt

# Clean previous outputs
rm -rf build dist bundled-backend/build/app

# Build onefile (default extraction to /tmp, suitable for read-only AppImage)
pyinstaller \
  --clean \
  --noconfirm \
  --onefile \
  --name app \
  backend/app.py

mkdir -p bundled-backend/build/app
cp dist/app bundled-backend/build/app/app
chmod +x bundled-backend/build/app/app

echo "Backend binary created at bundled-backend/build/app/app"
