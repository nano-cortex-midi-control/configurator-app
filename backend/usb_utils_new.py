#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
USB port detection and management utilities with MIDI device verification
"""

import serial
import serial.tools.list_ports
import logging
import json
import time
import platform
from datetime import datetime

logger = logging.getLogger(__name__)

class USBPortDetector:
    """Klasa za detekciju i upravljanje USB portovima sa MIDI verifikacijom."""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.verified_ports = {}  # Cache za verifikovane portove
        self.verification_timeout = 3  # Timeout za verifikaciju u sekundama
    
    def get_available_ports(self):
        """Vrati sve dostupne serijske portove sa verifikacijom."""
        ports = []
        
        try:
            # Dohvati sve dostupne portove
            available_ports = serial.tools.list_ports.comports()
            
            for port in available_ports:
                port_info = self._parse_port_info(port)
                if port_info:
                    # Pokušaj verifikaciju MIDI uređaja
                    verification_result = self.verify_midi_device(port.device)
                    port_info.update(verification_result)
                    
                    ports.append(port_info)
                    logger.debug(f"Port {port.device}: {port_info['status']}")
            
            # Sortiraj portove - MIDI uređaji na vrh, zatim ostali
            ports.sort(key=lambda x: (not x['is_midi_device'], x['id']))
            
            logger.info(f"Pronađeno {len(ports)} portova, {len([p for p in ports if p['is_midi_device']])} MIDI uređaja")
            return ports
            
        except Exception as e:
            logger.error(f"Greška pri detekciji USB portova: {e}")
            return []
    
    def verify_midi_device(self, port):
        """Verifikuj da li je port naš MIDI uređaj."""
        result = {
            'is_midi_device': False,
            'is_verified': False,
            'status': 'not_tested',
            'response_time': None
        }
        
        # Provjeri cache
        if port in self.verified_ports:
            cached = self.verified_ports[port]
            # Cache je valjan 60 sekundi
            if (datetime.now() - cached['timestamp']).seconds < 60:
                return cached['result']
        
        try:
            # Pokušaj konekciju sa portom
            with serial.Serial(port, 115200, timeout=1) as ser:
                # Počisti buffer
                ser.reset_input_buffer()
                ser.reset_output_buffer()
                
                # Pošalji ping poruku
                ping_message = {
                    "type": "ping",
                    "timestamp": datetime.now().isoformat()
                }
                
                ping_json = json.dumps(ping_message) + '\n'
                
                start_time = time.time()
                ser.write(ping_json.encode('utf-8'))
                ser.flush()
                
                # Čekaj odgovor
                timeout_start = time.time()
                
                while (time.time() - timeout_start) < self.verification_timeout:
                    if ser.in_waiting > 0:
                        try:
                            response_line = ser.readline().decode('utf-8').strip()
                            if response_line:
                                response_data = json.loads(response_line)
                                
                                if (response_data.get('type') == 'response'):
                                    response_time = time.time() - start_time
                                    result = {
                                        'is_midi_device': True,
                                        'is_verified': True,
                                        'status': 'midi_verified',
                                        'response_time': round(response_time * 1000, 2)  # ms
                                    }
                                    break
                                    
                        except (json.JSONDecodeError, UnicodeDecodeError):
                            continue
                    
                    time.sleep(0.1)
                
                if not result['is_verified']:
                    result['status'] = 'no_response'
                    
        except Exception as e:
            result['status'] = f'connection_error'
            logger.debug(f"Greška pri verifikaciji porta {port}: {e}")
        
        # Cache rezultat
        self.verified_ports[port] = {
            'result': result,
            'timestamp': datetime.now()
        }
        
        return result
    
    def _parse_port_info(self, port):
        """Parsira informacije o portu."""
        try:
            port_id = port.device
            description = port.description or "Unknown Device"
            manufacturer = port.manufacturer or ""
            product = port.product or ""
            
            # Generiši naziv porta
            name = self._generate_port_name(port_id, description, manufacturer, product)
            
            port_info = {
                'id': port_id,
                'name': name,
                'description': description,
                'manufacturer': manufacturer,
                'product': product,
                'hwid': port.hwid
            }
            
            return port_info
            
        except Exception as e:
            logger.error(f"Greška pri parsiranju port informacija za {port.device}: {e}")
            return None
    
    def _generate_port_name(self, port_id, description, manufacturer, product):
        """Generiši čitljiv naziv porta."""
        name_parts = [port_id]
        
        # Dodaj najkorisniju informaciju
        if product and product.strip():
            name_parts.append(product.strip())
        elif manufacturer and manufacturer.strip():
            name_parts.append(manufacturer.strip())
        elif description and "unknown" not in description.lower():
            # Skrati opis ako je predugačak
            desc = description.strip()
            if len(desc) > 30:
                desc = desc[:30] + "..."
            name_parts.append(desc)
        
        return " - ".join(name_parts)
    
    def get_auto_selected_port(self):
        """Vrati automatski izabrani port (prvi verifikovani MIDI uređaj)."""
        ports = self.get_available_ports()
        
        for port in ports:
            if port.get('is_midi_device') and port.get('is_verified'):
                return port['id']
        
        return None
    
    def clear_verification_cache(self):
        """Obriši cache verifikacije."""
        self.verified_ports.clear()
        logger.info("Cache verifikacije je obrisan")

# Globalna instanca USB detektora
usb_detector = USBPortDetector()
