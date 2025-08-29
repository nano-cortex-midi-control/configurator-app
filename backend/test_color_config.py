#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for color configuration in serial communication
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from serial_comm import SerialCommunicator
import json

def test_color_configuration():
    """Test the color configuration functionality."""
    
    # Create test data with different color scenarios
    test_button_data = [
        {
            'button': 1,
            'command_name': 'Start Recording',
            'command_value': 100,
            'color': 'red',
            'is_preset_color': True
        },
        {
            'button': 2,
            'command_name': 'Stop Recording',
            'command_value': 101,
            'color': '#ff5733',  # Custom orange color
            'is_preset_color': False
        },
        {
            'button': 3,
            'command_name': 'Play',
            'command_value': 102,
            'color': 'green',
            'is_preset_color': True
        },
        {
            'button': 4,
            'command_name': None,  # Unmapped button
            'command_value': None,
            'color': 'blue',
            'is_preset_color': True
        },
        {
            'button': 5,
            'command_name': None,  # Unmapped button with custom color
            'command_value': None,
            'color': '#9c27b0',  # Custom purple
            'is_preset_color': False
        },
        {
            'button': 6,
            'command_name': 'Mute',
            'command_value': 103,
            'color': None,  # No color set (should use default)
            'is_preset_color': True
        }
    ]
    
    # Create serial communicator instance
    serial_comm = SerialCommunicator()
    
    # Test color conversion
    print("🧪 Testing color conversion:")
    print("-" * 50)
    
    for button_data in test_button_data:
        color = button_data['color']
        is_preset = button_data['is_preset_color']
        hex_color = serial_comm._get_hex_color(color, is_preset)
        print(f"Button {button_data['button']}: {color} ({'preset' if is_preset else 'custom'}) -> {hex_color}")
    
    print("-" * 50)
    
    # Test configuration creation
    print("\n🔧 Testing MIDI configuration creation:")
    print("=" * 60)
    
    config = serial_comm._create_midi_config(test_button_data)
    
    # Pretty print the configuration
    config_json = json.dumps(config, indent=2, ensure_ascii=False)
    print(config_json)
    
    print("=" * 60)
    
    # Verify that all buttons have colors
    print("\n✅ Color verification:")
    for switch in config['switches']:
        button_id = switch['id'] + 1
        print(f"Button {button_id}: {switch['color']} ({'enabled' if switch['enabled'] else 'disabled'})")

if __name__ == "__main__":
    test_color_configuration()
