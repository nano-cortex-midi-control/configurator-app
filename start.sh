#!/bin/bash

# MIDI Configurator Startup Script
# Ovaj script pokreće backend i frontend

echo "=== MIDI Configurator ==="
echo "Pokretanje aplikacije..."

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

# Aktivira virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Pokretajte ./setup.sh da instalirate dependencies!"
    exit 1
fi

echo "🚀 Pokretanje Electron aplikacije..."

# Pokreni Electron aplikaciju (koja će pokrenuti i backend)
npm start
