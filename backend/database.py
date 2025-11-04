#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database management module for MIDI Configurator Backend
"""

import sqlite3
import os
import logging
from config import DATABASE_PATH

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Klasa za upravljanje SQLite bazom podataka."""
    
    def __init__(self, db_path=DATABASE_PATH):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inicijalizuj tabele u bazi podataka."""
        # Ensure parent directory exists for persistent DB locations
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Tabela za komande
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS commands (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    value INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Kreacija tabele za mapiranje tastera
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS button_mappings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    button_number INTEGER UNIQUE NOT NULL,
                    command_id INTEGER,
                    color TEXT DEFAULT NULL,
                    is_preset_color BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (command_id) REFERENCES commands (id) ON DELETE SET NULL
                )
            ''')
            
            # Dodaj kolone za boju ako ne postoje (migration)
            try:
                cursor.execute('ALTER TABLE button_mappings ADD COLUMN color TEXT DEFAULT NULL')
            except sqlite3.OperationalError:
                pass  # Kolona već postoji
            
            try:
                cursor.execute('ALTER TABLE button_mappings ADD COLUMN is_preset_color BOOLEAN DEFAULT TRUE')
            except sqlite3.OperationalError:
                pass  # Kolona već postoji
            
            # Inicijalizuj mapiranje tastera ako ne postoji
            for i in range(1, 7):
                cursor.execute('''
                    INSERT OR IGNORE INTO button_mappings (button_number, command_id) 
                    VALUES (?, NULL)
                ''', (i,))
            
            # Tabela za preset konfiguracije
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS presets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT DEFAULT '',
                    config_data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            logger.info("Baza podataka je inicijalizovana")
    
    def get_connection(self):
        """Vrati konekciju ka bazi podataka."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Omogući pristup kolonama po imenu
        return conn

# Globalna instanca database managera
db_manager = DatabaseManager()
