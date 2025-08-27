@echo off
echo 🚀 Pokretanje Configurator App...

REM Proverava da li su instalirane Node.js dependencies
if not exist "node_modules" (
    echo 📦 Instaliram Node.js dependencies...
    npm install
)

REM Proverava da li je kreiran Python virtual environment
if not exist ".venv" (
    echo 🐍 Kreiram Python virtual environment...
    python -m venv .venv
)

REM Aktivira virtual environment i instalira Python dependencies
echo 📚 Instaliram Python dependencies...
call .venv\Scripts\activate.bat
pip install -r backend\requirements.txt

echo ✅ Sve je spremno!
echo 🌐 Flask server će biti pokrenut na http://localhost:5000
echo 🖥️ Electron aplikacija će biti pokrenuta automatski
echo.
echo Za zatvaranje aplikacije koristite Ctrl+C

REM Pokreće aplikaciju
npm run dev

pause
