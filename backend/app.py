#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIDI Configurator Backend - Main Application
Flask server sa SQLite bazom za upravljanje komandama i mapiranjima.
"""

from flask import Flask
from flask_cors import CORS

# Import modula
from config import (
    SERVER_HOST, SERVER_PORT, DEBUG_MODE, 
    FRONTEND_STATIC_PATH, FRONTEND_TEMPLATES_PATH,
    DATABASE_PATH, logger
)
from database import db_manager
from error_handlers import register_error_handlers

# Import Blueprint-ova
from routes.commands import commands_bp
from routes.mappings import mappings_bp
from routes.config import config_bp
from routes.frontend import frontend_bp
from routes.presets import presets_bp

def create_app():
    """Factory funkcija za kreiranje Flask aplikacije."""
    
    # Kreiranje Flask aplikacije
    app = Flask(__name__, 
               static_folder=FRONTEND_STATIC_PATH,
               template_folder=FRONTEND_TEMPLATES_PATH)
    
    # Omogući CORS za frontend
    CORS(app)
    
    # Registruj Blueprint-ove
    app.register_blueprint(commands_bp)
    app.register_blueprint(mappings_bp)
    app.register_blueprint(config_bp)
    app.register_blueprint(presets_bp)
    app.register_blueprint(frontend_bp)
    
    # Registruj error handlers
    register_error_handlers(app)
    
    return app

def main():
    """Glavna funkcija za pokretanje servera."""
    logger.info("Pokretanje MIDI Configurator Backend servera...")
    logger.info(f"Baza podataka: {DATABASE_PATH}")
    
    # Kreiraj aplikaciju
    app = create_app()
    
    # Pokretaj server
    app.run(
        host=SERVER_HOST,
        port=SERVER_PORT,
        debug=DEBUG_MODE,
        threaded=True
    )

if __name__ == '__main__':
    main()

if __name__ == '__main__':
    main()
