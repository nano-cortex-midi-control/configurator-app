#!/bin/bash

# Setup Script for MIDI Configurator
echo "=== MIDI Configurator Setup ==="

# Proverava da li je python/node instalirano
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 nije instaliran!"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ Node.js nije instaliran!"
    exit 1
fi

# Prelazi u direktorijum aplikacije
cd "$(dirname "$0")"

echo "📦 Kreiranje Python virtual environment..."
python3 -m venv venv

echo "🐍 Aktiviranje virtual environment i instaliranje Python dependencies..."
source venv/bin/activate
pip install -r backend/requirements.txt

echo "📦 Instaliranje Node.js dependencies..."
npm install

echo "✅ Setup completed successfully!"
echo ""
echo "Da pokrenete aplikaciju:"
echo "  npm start"
echo ""
echo "ili:"
echo "  ./start.sh"
