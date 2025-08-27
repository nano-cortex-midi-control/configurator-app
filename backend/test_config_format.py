#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify MIDI configuration format
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from serial_comm import SerialCommunicator
import json

def test_config_format():
    """Test da li se kreira ispravni format konfiguracije."""
    
    # Test podaci - simuliramo button mappings iz baze
    test_button_mappings = [
        {'button': 1, 'command_name': 'Distortion', 'command_value': 127},
        {'button': 2, 'command_name': 'Chorus', 'command_value': 100},
        {'button': 3, 'command_name': 'Reverb', 'command_value': 80},
        {'button': 4, 'command_name': 'Delay', 'command_value': 90},
        {'button': 6, 'command_name': 'Boost', 'command_value': 127},
        # Taster 5 namjerno preskačemo da vidimo da li se popuni kao neaktivan
    ]
    
    # Kreiraj SerialCommunicator i testiraj
    comm = SerialCommunicator()
    config = comm._create_midi_config(test_button_mappings)
    
    # Isprintaj rezultat
    print("=== Generisana MIDI konfiguracija ===")
    print(json.dumps(config, indent=2, ensure_ascii=False))
    
    # Provjeri format
    print("\n=== Provjera formata ===")
    assert config['type'] == 'set_config', "Tip mora biti 'set_config'"
    assert 'switches' in config, "Mora sadržavati 'switches'"
    assert len(config['switches']) == 6, "Mora imati tačno 6 tastera"
    
    # Provjeri da nema dodatnih polja
    expected_keys = {'type', 'switches'}
    actual_keys = set(config.keys())
    assert actual_keys == expected_keys, f"Sadrži dodatna polja: {actual_keys - expected_keys}"
    
    # Provjeri format svakog tastera
    for i, switch in enumerate(config['switches']):
        expected_switch_keys = {'id', 'name', 'channel', 'cc', 'value', 'enabled'}
        actual_switch_keys = set(switch.keys())
        assert actual_switch_keys == expected_switch_keys, f"Taster {i} ima neispravne ključeve: {actual_switch_keys}"
        
        assert switch['id'] == i, f"ID tastera {i} nije ispravan"
        assert switch['channel'] == 1, f"Kanal tastera {i} mora biti 1"
        assert switch['cc'] == 20 + i, f"CC tastera {i} mora biti {20 + i}"
    
    print("✅ Format je potpuno ispravan!")
    
    # Prikaži mapirana i nemapirana
    print("\n=== Status tastera ===")
    for switch in config['switches']:
        status = "AKTIVAN" if switch['enabled'] else "NEAKTIVAN"
        print(f"Taster {switch['id']+1}: {switch['name']} (CC{switch['cc']}, vrednost: {switch['value']}) - {status}")

if __name__ == "__main__":
    test_config_format()
