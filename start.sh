#!/bin/bash

# Skripta za pokretanje Configurator aplikacije

echo "🚀 Pokretanje Configurator App..."

# Proverava da li su instalirane Node.js dependencies
if [ ! -d "node_modules" ]; then
    echo "📦 Instaliram Node.js dependencies..."
    npm install
fi

# Proverava da li je kreiran Python virtual environment
if [ ! -d ".venv" ]; then
    echo "🐍 Kreiram Python virtual environment..."
    python3 -m venv .venv
fi

# Aktivira virtual environment i instalira Python dependencies
echo "📚 Instaliram Python dependencies..."
source .venv/bin/activate
pip install -r backend/requirements.txt

echo "✅ Sve je spremno!"
echo "🌐 Flask server će biti pokrenut na http://localhost:5000"
echo "🖥️ Electron aplikacija će biti pokrenuta automatski"
echo ""
echo "Za zatvaranje aplikacije koristite Ctrl+C"

# Pokreće aplikaciju
npm run dev
