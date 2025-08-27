#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script za testiranje ispisa MIDI konfiguracije
"""

import requests
import json

def test_midi_configuration():
    """Testiraj slanje MIDI konfiguracije."""
    print("🧪 Testiranje MIDI konfiguracije...")
    
    # Test podaci - simuliramo konfiguraciju
    config_data = {
        "usbPort": "/dev/ttyUSB0"
    }
    
    try:
        # Pošalji zahtjev na API
        response = requests.post(
            'http://localhost:5001/api/configuration',
            json=config_data,
            headers={'Content-Type': 'application/json'}
        )
        
        result = response.json()
        
        print(f"📊 Odgovor API-ja:")
        print(f"   Status: {response.status_code}")
        print(f"   Success: {result.get('success')}")
        print(f"   Message: {result.get('message', 'N/A')}")
        print(f"   Error: {result.get('error', 'N/A')}")
        
        if result.get('success'):
            print("✅ Konfiguracija uspješno poslana!")
        else:
            print("❌ Greška pri slanju konfiguracije")
            
    except Exception as e:
        print(f"❌ Greška pri API pozivu: {e}")

def test_usb_ports():
    """Testiraj listu USB portova."""
    print("\n🔌 Testiranje USB portova...")
    
    try:
        response = requests.get('http://localhost:5001/api/usb-ports')
        result = response.json()
        
        print(f"📊 Dostupni portovi:")
        for port in result.get('data', []):
            print(f"   - {port.get('id')}: {port.get('name')}")
            
    except Exception as e:
        print(f"❌ Greška pri dohvatanju portova: {e}")

if __name__ == "__main__":
    test_usb_ports()
    test_midi_configuration()
