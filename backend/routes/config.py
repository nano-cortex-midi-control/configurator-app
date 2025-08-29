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
from serial_comm import serial_comm

logger = logging.getLogger(__name__)

# Kreiranje Blueprint-a za configuration API
config_bp = Blueprint('config', __name__)

@config_bp.route('/api/configuration', methods=['POST'])
def send_configuration():
    """Pošalji konfiguraciju na uređaj preko serial porta."""
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
            
            # Get all button mappings with their colors (including unmapped buttons)
            cursor.execute('''
                SELECT 
                    bm.button_number,
                    c.name as command_name,
                    c.value as command_value,
                    bm.color,
                    bm.is_preset_color
                FROM button_mappings bm
                LEFT JOIN commands c ON bm.command_id = c.id
                ORDER BY bm.button_number ASC
            ''')
            
            all_button_data = {}
            for row in cursor.fetchall():
                all_button_data[row['button_number']] = {
                    'button': row['button_number'],
                    'command_name': row['command_name'],
                    'command_value': row['command_value'],
                    'color': row['color'],
                    'is_preset_color': bool(row['is_preset_color']) if row['is_preset_color'] is not None else True
                }
            
            # Ensure we have data for all 6 buttons
            for i in range(1, 7):
                if i not in all_button_data:
                    all_button_data[i] = {
                        'button': i,
                        'command_name': None,
                        'command_value': None,
                        'color': None,
                        'is_preset_color': True
                    }
            
            # Get only mapped buttons for the old logic compatibility
            button_mappings = [data for data in all_button_data.values() if data['command_name'] is not None]
            
            if not button_mappings:
                return jsonify({
                    'success': False,
                    'error': 'Nema mapiranih tastera za slanje'
                }), 400
            
                        # Connect to the specified USB port
            if not serial_comm.connect(usb_port):
                return jsonify({
                    'success': False,
                    'error': f'Nije moguće povezati se sa portom {usb_port}'
                }), 400
            
            # Send configuration with all button data (including colors)
            success = serial_comm.send_configuration(list(all_button_data.values()))
            
            if success:
                # Pokušaj da pročitaš odgovor (neobavezno)
                response = serial_comm.read_response(timeout=1)
                
                result = {
                    'usb_port': usb_port,
                    'button_mappings': button_mappings,
                    'timestamp': datetime.now().isoformat(),
                    'status': 'sent'
                }
                
                if response:
                    result['device_response'] = response
                
                logger.info(f"Konfiguracija uspješno poslana na port: {usb_port}")
                return jsonify({
                    'success': True,
                    'data': result,
                    'message': f'Konfiguracija uspješno poslana na {usb_port}'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Greška pri slanju konfiguracije na uređaj'
                }), 500
    
    except Exception as e:
        logger.error(f"Greška pri slanju konfiguracije: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    
    finally:
        # Uvijek prekini konekciju
        serial_comm.disconnect()

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

@config_bp.route('/api/usb-ports/test-serial', methods=['POST'])
def test_serial_connection():
    """Testiraj serial komunikaciju sa portom."""
    try:
        data = request.get_json()
        port_id = data.get('portId')
        
        if not port_id:
            return jsonify({
                'success': False,
                'error': 'Port ID je obavezan'
            }), 400
        
        # Poveži se sa serial portom
        if not serial_comm.connect(port_id):
            return jsonify({
                'success': False,
                'error': f'Greška pri povezivanju sa portom {port_id}'
            }), 500
        
        try:
            # Pošalji test poruku
            success = serial_comm.send_test_message()
            
            if success:
                # Pokušaj da pročitaš odgovor
                response = serial_comm.read_response(timeout=2)
                
                return jsonify({
                    'success': True,
                    'data': {
                        'port_id': port_id,
                        'connected': True,
                        'test_sent': success,
                        'device_response': response,
                        'message': 'Serial komunikacija uspješna' if response else 'Test poruka poslana (nema odgovora)'
                    }
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Greška pri slanju test poruke'
                }), 500
                
        finally:
            serial_comm.disconnect()
    
    except Exception as e:
        logger.error(f"Greška pri testiranju serial komunikacije: {e}")
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
