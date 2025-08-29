#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API routes for preset configurations management
"""

from flask import Blueprint, request, jsonify
import logging
import json
from datetime import datetime
from database import db_manager

logger = logging.getLogger(__name__)

# Kreiranje Blueprint-a za presets API
presets_bp = Blueprint('presets', __name__)

@presets_bp.route('/api/presets', methods=['GET'])
def get_presets():
    """Vrati sve sačuvane preset konfiguracije."""
    try:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, description, created_at, updated_at
                FROM presets 
                ORDER BY updated_at DESC
            ''')
            
            presets = []
            for row in cursor.fetchall():
                presets.append({
                    'id': row['id'],
                    'name': row['name'],
                    'description': row['description'],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                })
            
            logger.info(f"Vraćeno {len(presets)} preset konfiguracija")
            return jsonify({
                'success': True,
                'data': presets
            })
    
    except Exception as e:
        logger.error(f"Greška pri dohvatanju preset-ova: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@presets_bp.route('/api/presets', methods=['POST'])
def save_preset():
    """Sačuvaj trenutnu konfiguraciju kao preset."""
    try:
        data = request.get_json()
        name = data.get('name')
        description = data.get('description', '')
        
        if not name:
            return jsonify({
                'success': False,
                'error': 'Naziv preset-a je obavezan'
            }), 400
        
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get current button mappings with colors
            cursor.execute('''
                SELECT 
                    bm.button_number,
                    bm.command_id,
                    c.name as command_name,
                    c.value as command_value,
                    bm.color,
                    bm.is_preset_color
                FROM button_mappings bm
                LEFT JOIN commands c ON bm.command_id = c.id
                ORDER BY bm.button_number ASC
            ''')
            
            # Build configuration data
            config_data = {}
            for row in cursor.fetchall():
                if row['command_id']:  # Only include mapped buttons
                    config_data[str(row['button_number'])] = {
                        'command_id': row['command_id'],
                        'command_name': row['command_name'],
                        'command_value': row['command_value'],
                        'color': row['color'],
                        'is_preset_color': bool(row['is_preset_color']) if row['is_preset_color'] is not None else True
                    }
            
            # Save preset
            cursor.execute('''
                INSERT INTO presets (name, description, config_data)
                VALUES (?, ?, ?)
            ''', (name, description, json.dumps(config_data)))
            
            preset_id = cursor.lastrowid
            conn.commit()
            
            logger.info(f"Sačuvan preset '{name}' sa ID {preset_id}")
            return jsonify({
                'success': True,
                'message': f'Preset "{name}" je uspješno sačuvan',
                'preset_id': preset_id
            })
    
    except Exception as e:
        logger.error(f"Greška pri čuvanju preset-a: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@presets_bp.route('/api/presets/<int:preset_id>', methods=['GET'])
def load_preset(preset_id):
    """Učitaj preset konfiguraciju."""
    try:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT name, description, config_data
                FROM presets 
                WHERE id = ?
            ''', (preset_id,))
            
            row = cursor.fetchone()
            if not row:
                return jsonify({
                    'success': False,
                    'error': 'Preset nije pronađen'
                }), 404
            
            config_data = json.loads(row['config_data'])
            
            # Clear current mappings
            cursor.execute('UPDATE button_mappings SET command_id = NULL, color = NULL, is_preset_color = TRUE')
            
            # Apply preset configuration
            for button_number, mapping in config_data.items():
                cursor.execute('''
                    INSERT OR REPLACE INTO button_mappings 
                    (button_number, command_id, color, is_preset_color)
                    VALUES (?, ?, ?, ?)
                ''', (
                    int(button_number),
                    mapping['command_id'],
                    mapping.get('color'),
                    mapping.get('is_preset_color', True)
                ))
            
            conn.commit()
            
            logger.info(f"Učitan preset '{row['name']}' sa ID {preset_id}")
            return jsonify({
                'success': True,
                'message': f'Preset "{row["name"]}" je uspješno učitan',
                'data': {
                    'name': row['name'],
                    'description': row['description'],
                    'config': config_data
                }
            })
    
    except Exception as e:
        logger.error(f"Greška pri učitavanju preset-a: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@presets_bp.route('/api/presets/<int:preset_id>', methods=['DELETE'])
def delete_preset(preset_id):
    """Obriši preset konfiguraciju."""
    try:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if preset exists
            cursor.execute('SELECT name FROM presets WHERE id = ?', (preset_id,))
            row = cursor.fetchone()
            if not row:
                return jsonify({
                    'success': False,
                    'error': 'Preset nije pronađen'
                }), 404
            
            # Delete preset
            cursor.execute('DELETE FROM presets WHERE id = ?', (preset_id,))
            conn.commit()
            
            logger.info(f"Obrisan preset '{row['name']}' sa ID {preset_id}")
            return jsonify({
                'success': True,
                'message': f'Preset "{row["name"]}" je uspješno obrisan'
            })
    
    except Exception as e:
        logger.error(f"Greška pri brisanju preset-a: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
