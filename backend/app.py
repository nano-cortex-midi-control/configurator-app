#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIDI Configurator Backend
Flask server sa SQLite bazom za upravljanje komandama i mapiranjima.
"""

from flask import Flask, request, jsonify, send_from_directory, render_template_string
from flask_cors import CORS
import sqlite3
import os
import logging
from datetime import datetime

# Kreiranje Flask aplikacije
app = Flask(__name__, 
           static_folder='../frontend/static',
           template_folder='../frontend/templates')
CORS(app)  # Omogući CORS za frontend

# Konfiguracija
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database.db')
LOG_LEVEL = logging.INFO

# Logging setup
logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Klasa za upravljanje SQLite bazom podataka."""
    
    def __init__(self, db_path):
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
db_manager = DatabaseManager(DATABASE_PATH)

# Frontend rute

@app.route('/')
def index():
    """Serviraj glavni HTML fajl."""
    try:
        # Definiraj apsolutnu putanju do template fajla
        template_path = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'templates', 'index.html')
        template_path = os.path.abspath(template_path)
        
        with open(template_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Replace Flask template syntax with static paths for Electron
        html_content = html_content.replace(
            "{{ url_for('static', filename='css/style.css') }}", 
            "/static/css/style.css"
        )
        html_content = html_content.replace(
            "{{ url_for('static', filename='js/app.js') }}", 
            "/static/js/app.js"
        )
        
        return render_template_string(html_content)
    except Exception as e:
        logger.error(f"Greška pri učitavanju index.html: {e}")
        return f"Greška pri učitavanju aplikacije: {e}", 500

@app.route('/static/<path:filename>')
def static_files(filename):
    """Serviraj statičke fajlove."""
    static_path = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'static')
    static_path = os.path.abspath(static_path)
    return send_from_directory(static_path, filename)

# API rute za komande

@app.route('/api/commands', methods=['GET'])
def get_commands():
    """Vrati sve komande iz baze."""
    try:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, value, created_at, updated_at 
                FROM commands 
                ORDER BY name ASC
            ''')
            commands = [dict(row) for row in cursor.fetchall()]
            
            logger.info(f"Vraćeno {len(commands)} komandi")
            return jsonify({
                'success': True,
                'data': commands
            })
    
    except Exception as e:
        logger.error(f"Greška pri dohvatanju komandi: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/commands', methods=['POST'])
def create_command():
    """Kreiraj novu komandu."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Nedostaju podaci'
            }), 400
        
        name = data.get('name', '').strip()
        value = data.get('value')
        
        # Validacija
        if not name:
            return jsonify({
                'success': False,
                'error': 'Naziv komande je obavezan'
            }), 400
        
        if not isinstance(value, int) or value < 0 or value > 65535:
            return jsonify({
                'success': False,
                'error': 'Vrednost mora biti broj između 0 i 65535'
            }), 400
        
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO commands (name, value) 
                VALUES (?, ?)
            ''', (name, value))
            
            command_id = cursor.lastrowid
            conn.commit()
            
            logger.info(f"Kreirana nova komanda: {name} (ID: {command_id})")
            return jsonify({
                'success': True,
                'data': {
                    'id': command_id,
                    'name': name,
                    'value': value
                }
            })
    
    except sqlite3.IntegrityError:
        return jsonify({
            'success': False,
            'error': 'Komanda sa tim nazivom već postoji'
        }), 400
    
    except Exception as e:
        logger.error(f"Greška pri kreiranju komande: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/commands/<int:command_id>', methods=['PUT'])
def update_command(command_id):
    """Ažuriraj postojeću komandu."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Nedostaju podaci'
            }), 400
        
        name = data.get('name', '').strip()
        value = data.get('value')
        
        # Validacija
        if not name:
            return jsonify({
                'success': False,
                'error': 'Naziv komande je obavezan'
            }), 400
        
        if not isinstance(value, int) or value < 0 or value > 65535:
            return jsonify({
                'success': False,
                'error': 'Vrednost mora biti broj između 0 i 65535'
            }), 400
        
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE commands 
                SET name = ?, value = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (name, value, command_id))
            
            if cursor.rowcount == 0:
                return jsonify({
                    'success': False,
                    'error': 'Komanda nije pronađena'
                }), 404
            
            conn.commit()
            
            logger.info(f"Ažurirana komanda: {name} (ID: {command_id})")
            return jsonify({
                'success': True,
                'data': {
                    'id': command_id,
                    'name': name,
                    'value': value
                }
            })
    
    except sqlite3.IntegrityError:
        return jsonify({
            'success': False,
            'error': 'Komanda sa tim nazivom već postoji'
        }), 400
    
    except Exception as e:
        logger.error(f"Greška pri ažuriranju komande: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/commands/<int:command_id>', methods=['DELETE'])
def delete_command(command_id):
    """Obriši komandu iz baze."""
    try:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM commands WHERE id = ?', (command_id,))
            
            if cursor.rowcount == 0:
                return jsonify({
                    'success': False,
                    'error': 'Komanda nije pronađena'
                }), 404
            
            conn.commit()
            
            logger.info(f"Obrisana komanda sa ID: {command_id}")
            return jsonify({
                'success': True,
                'message': 'Komanda je obrisana'
            })
    
    except Exception as e:
        logger.error(f"Greška pri brisanju komande: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# API rute za mapiranje tastera

@app.route('/api/button-mappings', methods=['GET'])
def get_button_mappings():
    """Vrati mapiranje tastera."""
    try:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT button_number, command_id 
                FROM button_mappings 
                WHERE command_id IS NOT NULL
                ORDER BY button_number ASC
            ''')
            mappings = {str(row['button_number']): row['command_id'] for row in cursor.fetchall()}
            
            logger.info(f"Vraćeno mapiranje za {len(mappings)} tastera")
            return jsonify({
                'success': True,
                'data': mappings
            })
    
    except Exception as e:
        logger.error(f"Greška pri dohvatanju mapiranja: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/button-mappings', methods=['POST'])
def update_button_mappings():
    """Ažuriraj mapiranje tastera."""
    try:
        data = request.get_json()
        
        if not isinstance(data, dict):
            return jsonify({
                'success': False,
                'error': 'Neispravni podaci'
            }), 400
        
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            # Resetuj sva mapiranja
            cursor.execute('UPDATE button_mappings SET command_id = NULL')
            
            # Postaviti nova mapiranja
            for button_num, command_id in data.items():
                try:
                    button_num = int(button_num)
                    command_id = int(command_id) if command_id else None
                    
                    if 1 <= button_num <= 6:
                        cursor.execute('''
                            UPDATE button_mappings 
                            SET command_id = ?, updated_at = CURRENT_TIMESTAMP
                            WHERE button_number = ?
                        ''', (command_id, button_num))
                except (ValueError, TypeError):
                    continue
            
            conn.commit()
            
            logger.info("Mapiranje tastera je ažurirano")
            return jsonify({
                'success': True,
                'message': 'Mapiranje tastera je ažurirano'
            })
    
    except Exception as e:
        logger.error(f"Greška pri ažuriranju mapiranja: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/configuration', methods=['POST'])
def send_configuration():
    """Vrati konfiguraciju za slanje na uređaj."""
    try:
        data = request.get_json()
        usb_port = data.get('usbPort')
        
        if not usb_port:
            return jsonify({
                'success': False,
                'error': 'USB port je obavezan'
            }), 400
        
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    bm.button_number,
                    c.name as command_name,
                    c.value as command_value
                FROM button_mappings bm
                LEFT JOIN commands c ON bm.command_id = c.id
                WHERE bm.command_id IS NOT NULL
                ORDER BY bm.button_number ASC
            ''')
            
            configuration = []
            for row in cursor.fetchall():
                configuration.append({
                    'button': row['button_number'],
                    'command_name': row['command_name'],
                    'command_value': row['command_value']
                })
            
            result = {
                'usb_port': usb_port,
                'button_mappings': configuration,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Konfiguracija poslana za USB port: {usb_port}")
            return jsonify({
                'success': True,
                'data': result
            })
    
    except Exception as e:
        logger.error(f"Greška pri slanju konfiguracije: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# API rute za USB portove

@app.route('/api/usb-ports', methods=['GET'])
def get_usb_ports():
    """Vrati dostupne USB portove."""
    try:
        # Mock podaci za USB portove - možete proširiti sa stvarnim detekcijama
        usb_ports = [
            {'id': 'COM1', 'name': 'COM1 - Arduino Uno'},
            {'id': 'COM3', 'name': 'COM3 - MIDI Controller'},
            {'id': '/dev/ttyUSB0', 'name': '/dev/ttyUSB0 - USB Serial'},
            {'id': '/dev/ttyACM0', 'name': '/dev/ttyACM0 - Arduino'}
        ]
        
        return jsonify({
            'success': True,
            'data': usb_ports
        })
    
    except Exception as e:
        logger.error(f"Greška pri dohvatanju USB portova: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Health check endpoint

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'success': True,
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

# Error handlers

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    logger.info("Pokretanje MIDI Configurator Backend servera...")
    logger.info(f"Baza podataka: {DATABASE_PATH}")
    
    # Pokretaj server
    app.run(
        host='127.0.0.1',
        port=5001,
        debug=True,
        threaded=True
    )
