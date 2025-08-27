#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database management module for MIDI Configurator Backend
"""

import sqlite3
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
            
            # Tabela za mapiranje tastera
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS button_mappings (
                    button_number INTEGER PRIMARY KEY CHECK(button_number >= 1 AND button_number <= 6),
                    command_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (command_id) REFERENCES commands (id) ON DELETE SET NULL
                )
            ''')
            
            # Inicijalizuj mapiranje tastera ako ne postoji
            for i in range(1, 7):
                cursor.execute('''
                    INSERT OR IGNORE INTO button_mappings (button_number, command_id) 
                    VALUES (?, NULL)
                ''', (i,))
            
            conn.commit()
            logger.info("Baza podataka je inicijalizovana")
    
    def get_connection(self):
        """Vrati konekciju ka bazi podataka."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Omogući pristup kolonama po imenu
        return conn

# Globalna instanca database managera
db_manager = DatabaseManager()
