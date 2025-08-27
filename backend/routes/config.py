#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API routes for configuration and USB ports management
"""

from flask import Blueprint, request, jsonify
import logging
from datetime import datetime
from database import db_manager
from usb_utils import usb_detector

logger = logging.getLogger(__name__)

# Kreiranje Blueprint-a za configuration API
config_bp = Blueprint('config', __name__)

@config_bp.route('/api/configuration', methods=['POST'])
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

@config_bp.route('/api/usb-ports', methods=['GET'])
def get_usb_ports():
    """Vrati dostupne USB portove."""
    try:
        # Dohvati stvarno dostupne USB/Serial portove
        usb_ports = usb_detector.get_available_ports()
        
        # Ako nema portova, vrati poruku
        if not usb_ports:
            logger.warning("Nema dostupnih USB/Serial portova")
            return jsonify({
                'success': True,
                'data': [],
                'message': 'Nema dostupnih USB/Serial portova. Provjerite da li je uređaj povezan.'
            })
        
        logger.info(f"Vraćeno {len(usb_ports)} USB portova")
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

@config_bp.route('/api/usb-ports/test', methods=['POST'])
def test_usb_port():
    """Testiraj konekciju sa USB portom."""
    try:
        data = request.get_json()
        port_id = data.get('portId')
        
        if not port_id:
            return jsonify({
                'success': False,
                'error': 'Port ID je obavezan'
            }), 400
        
        # Testiraj konekciju
        is_connected = usb_detector.test_port_connection(port_id)
        
        return jsonify({
            'success': True,
            'data': {
                'port_id': port_id,
                'is_connected': is_connected,
                'message': 'Port je dostupan' if is_connected else 'Port nije dostupan ili je zauzet'
            }
        })
    
    except Exception as e:
        logger.error(f"Greška pri testiranju USB porta: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@config_bp.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'success': True,
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })
