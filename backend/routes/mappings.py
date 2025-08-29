#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API routes for button mappings management
"""

from flask import Blueprint, request, jsonify
import logging
from database import db_manager

logger = logging.getLogger(__name__)

# Kreiranje Blueprint-a za button mappings API
mappings_bp = Blueprint('mappings', __name__)

@mappings_bp.route('/api/button-mappings', methods=['GET'])
def get_button_mappings():
    """Vrati mapiranje tastera."""
    try:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT button_number, command_id, color, is_preset_color 
                FROM button_mappings 
                ORDER BY button_number ASC
            ''')
            
            mappings = {}
            for row in cursor.fetchall():
                button_num = str(row['button_number'])
                mappings[button_num] = {
                    'command_id': row['command_id'],
                    'color': row['color'],
                    'is_preset': bool(row['is_preset_color']) if row['is_preset_color'] is not None else True
                }
            
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

@mappings_bp.route('/api/button-mappings', methods=['POST'])
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

@mappings_bp.route('/api/button-mappings/color', methods=['POST'])
def update_button_color():
    """Ažuriraj boju tastera."""
    try:
        data = request.get_json()
        
        button_number = data.get('button_number')
        color = data.get('color')
        is_preset = data.get('is_preset', False)
        
        if not button_number or not color:
            return jsonify({
                'success': False,
                'error': 'button_number i color su obavezni'
            }), 400
        
        if not (1 <= button_number <= 6):
            return jsonify({
                'success': False,
                'error': 'button_number mora biti između 1 i 6'
            }), 400
        
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if button mapping exists, if not create it
            cursor.execute('''
                SELECT button_number FROM button_mappings 
                WHERE button_number = ?
            ''', (button_number,))
            
            if not cursor.fetchone():
                cursor.execute('''
                    INSERT INTO button_mappings (button_number) 
                    VALUES (?)
                ''', (button_number,))
            
            # Update button color
            cursor.execute('''
                UPDATE button_mappings 
                SET color = ?, is_preset_color = ?, updated_at = CURRENT_TIMESTAMP
                WHERE button_number = ?
            ''', (color, is_preset, button_number))
            
            conn.commit()
            
            logger.info(f"Boja tastera {button_number} je ažurirana na {color}")
            return jsonify({
                'success': True,
                'message': f'Boja tastera {button_number} je ažurirana'
            })
    
    except Exception as e:
        logger.error(f"Greška pri ažuriranju boje tastera: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
