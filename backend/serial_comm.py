#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Serial communication module for MIDI Configurator Backend
"""

import serial
import json
import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)

# Predefined color mappings to hex codes
PRESET_COLORS = {
    'red': '#dc3545',
    'blue': '#007bff', 
    'green': '#28a745',
    'yellow': '#ffc107',
    'purple': '#6f42c1',
    'orange': '#fd7e14',
    'teal': '#20c997',
    'pink': '#e83e8c',
    'indigo': '#6610f2',
    'cyan': '#17a2b8'
}

class SerialCommunicator:
    """Klasa za komunikaciju preko serial porta."""
    
    def __init__(self):
        self.connection = None
        self.port = None
        self.baudrate = 115200  # ESP32 standard baudrate
        self.timeout = 2
    
    def connect(self, port, baudrate=115200, timeout=2):
        """Povezuje se sa serial portom."""
        try:
            if self.connection and self.connection.is_open:
                self.disconnect()
            
            self.port = port
            self.baudrate = baudrate
            self.timeout = timeout
            
            self.connection = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=timeout,
                write_timeout=timeout
            )
            
            logger.info(f"Uspješno povezan sa portom {port}")
            return True
            
        except Exception as e:
            logger.error(f"Greška pri povezivanju sa portom {port}: {e}")
            self.connection = None
            return False
    
    def disconnect(self):
        """Prekida konekciju sa serial portom."""
        try:
            if self.connection and self.connection.is_open:
                self.connection.close()
                logger.info(f"Prekinuta konekcija sa portom {self.port}")
            self.connection = None
            self.port = None
        except Exception as e:
            logger.error(f"Greška pri prekidanju konekcije: {e}")
    
    def is_connected(self):
        """Provjeri da li je konekcija aktivna."""
        return self.connection and self.connection.is_open
    
    def send_configuration(self, button_mappings):
        """Šalje MIDI konfiguraciju preko serial porta."""
        try:
            if not self.is_connected():
                raise Exception("Nema aktivne konekcije sa serial portom")
            
            # Kreiraj MIDI konfiguraciju
            config_message = self._create_midi_config(button_mappings)
            
            # Konvertuj u JSON string - u jednoj liniji
            json_message = json.dumps(config_message)
            
            # Isprintaj poruku koja se šalje
            print("\n" + "=" * 80)
            print("🚀 SLANJE MIDI KONFIGURACIJE NA PORT:", self.port)
            print("=" * 80)
            print(json_message)
            print("=" * 80)
            
            # Dodaj newline i konvertuj u bytes
            message_bytes = (json_message + '\n').encode()
            
            # Pošalji poruku
            bytes_written = self.connection.write(message_bytes)
            self.connection.flush()  # Osiguraj da se poruka pošalje odmah
            
            print(f"✅ USPJEŠNO POSLANO {bytes_written} bytes na port {self.port}")
            print("=" * 80 + "\n")
            
            logger.info(f"✅ Uspješno poslano {bytes_written} bytes na port {self.port}")
            
            return True
            
        except Exception as e:
            print(f"❌ GREŠKA PRI SLANJU: {e}")
            logger.error(f"❌ Greška pri slanju konfiguracije: {e}")
            return False
    
    def _get_hex_color(self, color, is_preset_color=True):
        """Convert color to hex code."""
        if not color:
            return '#667eea'  # Default color
            
        if is_preset_color and color in PRESET_COLORS:
            return PRESET_COLORS[color]
        elif color.startswith('#') and len(color) == 7:
            # Already a valid hex color
            return color
        else:
            # Fallback to default color
            return '#667eea'
    
    def _create_midi_config(self, all_button_data):
        """Kreira MIDI konfiguraciju na osnovu mapiranja tastera."""
        # Kreiraj osnovni template za svih 6 tastera
        switches = []
        
        # Create a dictionary for easy lookup
        button_dict = {data['button']: data for data in all_button_data}
        
        # Kreiraj konfiguraciju za svih 6 tastera
        for i in range(6):
            button_num = i + 1  # Convert to 1-based numbering
            button_data = button_dict.get(button_num, {})
            
            # Get color information
            hex_color = self._get_hex_color(
                button_data.get('color'), 
                button_data.get('is_preset_color', True)
            )
            
            # Check if button has a command mapped
            has_command = button_data.get('command_name') is not None
            
            switch_config = {
                "id": i,
                "name": button_data.get('command_name', f"Neaktivan_{button_num}"),
                "channel": 1,
                "cc": button_data.get('command_value', 0),
                "value": button_data.get('command_value', 0),
                "enabled": has_command,
                "color": hex_color
            }
            
            switches.append(switch_config)
        
        # Kreiraj konačnu konfiguraciju
        config = {
            "type": "set_config",
            "switches": switches
        }
        
        enabled_count = len([s for s in switches if s['enabled']])
        print(f"🔧 Kreirana MIDI konfiguracija sa {enabled_count} aktivnih tastera i bojama za svih 6 tastera")
        
        return config
    
    def send_test_message(self):
        """Šalje test poruku."""
        try:
            if not self.is_connected():
                raise Exception("Nema aktivne konekcije sa serial portom")
            
            test_message = {
                "type": "ping",
                "timestamp": datetime.now().isoformat(),
                "message": "Test konekcije"
            }
            
            json_message = json.dumps(test_message, ensure_ascii=False, separators=(',', ':'))
            
            # Isprintaj test poruku
            print("\n" + "-" * 60)
            print("🔍 SLANJE TEST PORUKE NA PORT:", self.port)
            print("-" * 60)
            print(json_message)
            print("-" * 60)
            
            message_bytes = (json_message + '\n').encode('utf-8')
            
            bytes_written = self.connection.write(message_bytes)
            self.connection.flush()
            
            print(f"✅ TEST PORUKA POSLANA ({bytes_written} bytes)")
            print("-" * 60 + "\n")
            
            logger.info(f"✅ Test poruka poslana ({bytes_written} bytes)")
            return True
            
        except Exception as e:
            print(f"❌ GREŠKA PRI SLANJU TEST PORUKE: {e}")
            logger.error(f"❌ Greška pri slanju test poruke: {e}")
            return False
    
    def read_response(self, timeout=None):
        """Čita odgovor sa serial porta."""
        try:
            if not self.is_connected():
                return None
            
            original_timeout = self.connection.timeout
            if timeout is not None:
                self.connection.timeout = timeout
            
            line = self.connection.readline()
            
            # Vrati originalni timeout
            self.connection.timeout = original_timeout
            
            if line:
                response = line.decode('utf-8').strip()
                logger.debug(f"Primljen odgovor: {response}")
                return response
            
            return None
            
        except Exception as e:
            logger.warning(f"Greška pri čitanju odgovora: {e}")
            return None

# Globalna instanca serial komunikatora
serial_comm = SerialCommunicator()
