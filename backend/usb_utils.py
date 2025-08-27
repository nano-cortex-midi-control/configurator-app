#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
USB port detection utility for MIDI Configurator Backend
"""

import serial.tools.list_ports
import logging
import platform
import re

logger = logging.getLogger(__name__)

class USBPortDetector:
    """Klasa za detekciju USB portova."""
    
    def __init__(self):
        self.system = platform.system().lower()
    
    def get_available_ports(self):
        """Vrati listu dostupnih USB/Serial portova."""
        try:
            ports = []
            available_ports = serial.tools.list_ports.comports()
            
            for port in available_ports:
                port_info = self._parse_port_info(port)
                if port_info:
                    ports.append(port_info)
            
            # Sortirati portove po imenu
            ports.sort(key=lambda x: x['id'])
            
            logger.info(f"Pronađeno {len(ports)} USB/Serial portova")
            return ports
            
        except Exception as e:
            logger.error(f"Greška pri detekciji USB portova: {e}")
            return []
    
    def _parse_port_info(self, port):
        """Parsira informacije o portu."""
        try:
            port_id = port.device
            description = port.description or "Unknown Device"
            manufacturer = port.manufacturer or ""
            product = port.product or ""
            vid_pid = ""
            
            # Pokušaj da dohvatiš VID:PID informacije
            if hasattr(port, 'vid') and hasattr(port, 'pid') and port.vid and port.pid:
                vid_pid = f" (VID:PID {port.vid:04X}:{port.pid:04X})"
            
            # Kreiranje user-friendly naziva
            name = self._create_friendly_name(port_id, description, manufacturer, product, vid_pid)
            
            # Filtriranje portova - samo oni koji mogu biti relevantni
            if self._is_relevant_port(description, manufacturer, product):
                return {
                    'id': port_id,
                    'name': name,
                    'description': description,
                    'manufacturer': manufacturer,
                    'product': product
                }
            
            return None
            
        except Exception as e:
            logger.warning(f"Greška pri parsiranju port info: {e}")
            return None
    
    def _create_friendly_name(self, port_id, description, manufacturer, product, vid_pid):
        """Kreiraj user-friendly naziv za port."""
        name_parts = [port_id]
        
        # Dodaj opis ili proizvođač/proizvod
        if product and product != "USB Serial Device":
            name_parts.append(product)
        elif manufacturer and manufacturer not in ["FTDI", "Prolific Technology Inc."]:
            name_parts.append(manufacturer)
        elif description and description != port_id:
            # Očisti opis od osnovnih termina
            clean_desc = description.replace("USB Serial Port", "").replace("Serial Port", "").strip()
            if clean_desc and clean_desc != port_id:
                name_parts.append(clean_desc)
        
        # Dodaj VID:PID ako je dostupno
        if vid_pid:
            name_parts.append(vid_pid)
        
        return " - ".join(name_parts)
    
    def _is_relevant_port(self, description, manufacturer, product):
        """Provjeri da li je port relevantan za MIDI/Arduino uređaje."""
        # Lista ključnih riječi koja ukazuje na relevantne uređaje
        relevant_keywords = [
            'arduino', 'midi', 'usb', 'serial', 'ch340', 'cp210', 'ftdi', 
            'prolific', 'silicon labs', 'atmel', 'microchip', 'stm32',
            'esp32', 'esp8266', 'teensy', 'leonardo', 'uno', 'nano', 'mega'
        ]
        
        # Kombiniraj sve tekst informacije
        combined_text = f"{description} {manufacturer} {product}".lower()
        
        # Provjeri da li sadrži bilo koju relevantnu ključnu riječ
        for keyword in relevant_keywords:
            if keyword in combined_text:
                return True
        
        # Na Linux sistemima, prihvati ttyUSB* i ttyACM* portove
        if self.system == 'linux':
            if any(pattern in description.lower() for pattern in ['ttyusb', 'ttyacm']):
                return True
        
        # Na Windows sistemima, prihvati COM portove
        if self.system == 'windows':
            if 'com' in combined_text:
                return True
        
        # Ako nema specifične indikacije, vrati False da se izbjegnu sistemski portovi
        return False
    
    def test_port_connection(self, port_id, timeout=2):
        """Testiraj konekciju sa portom."""
        try:
            with serial.Serial(port_id, 9600, timeout=timeout) as ser:
                return True
        except Exception as e:
            logger.debug(f"Test konekcije za port {port_id} neuspješan: {e}")
            return False

# Globalna instanca USB port detector-a
usb_detector = USBPortDetector()
