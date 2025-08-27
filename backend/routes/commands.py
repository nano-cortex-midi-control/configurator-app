#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API routes for commands management
"""

from flask import Blueprint, request, jsonify
import sqlite3
import logging
from database import db_manager

logger = logging.getLogger(__name__)

# Kreiranje Blueprint-a za commands API
commands_bp = Blueprint('commands', __name__)

@commands_bp.route('/api/commands', methods=['GET'])
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

@commands_bp.route('/api/commands', methods=['POST'])
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

@commands_bp.route('/api/commands/<int:command_id>', methods=['PUT'])
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

@commands_bp.route('/api/commands/<int:command_id>', methods=['DELETE'])
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
