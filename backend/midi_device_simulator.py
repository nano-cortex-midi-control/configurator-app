#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIDI Device Simulator - simulates a device that receives MIDI configuration
"""

import serial
import json
import sys
import time
import threading

class MIDIDeviceSimulator:
    def __init__(self, port, baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.connection = None
        self.running = False
        
    def start(self):
        try:
            self.connection = serial.Serial(self.port, self.baudrate, timeout=1)
            self.running = True
            print(f"MIDI Device Simulator pokrenut na portu {self.port}")
            print("Čekam konfiguraciju...")
            
            while self.running:
                try:
                    # Čitaj liniju sa serial porta
                    line = self.connection.readline()
                    if line:
                        message = line.decode('utf-8').strip()
                        if message:
                            self.process_message(message)
                            
                except serial.SerialTimeoutException:
                    continue
                except Exception as e:
                    print(f"Greška pri čitanju: {e}")
                    break
                    
        except Exception as e:
            print(f"Greška pri pokretanju simulatora: {e}")
        finally:
            if self.connection:
                self.connection.close()
    
    def process_message(self, message):
        try:
            data = json.loads(message)
            print(f"\n--- Primljena poruka ---")
            print(f"Tip: {data.get('type', 'unknown')}")
            
            if data.get('type') == 'set_config':
                self.handle_config(data)
            elif data.get('type') == 'ping':
                self.handle_ping(data)
            else:
                print(f"Nepoznat tip poruke: {data}")
                
        except json.JSONDecodeError:
            print(f"Neispravna JSON poruka: {message}")
    
    def handle_config(self, data):
        print(f"Konfiguracija za {len(data.get('switches', []))} tastera:")
        
        for switch in data.get('switches', []):
            status = "AKTIVNO" if switch.get('enabled') else "NEAKTIVNO"
            print(f"  Taster {switch.get('id', '?')+1}: {switch.get('name', 'N/A')} "
                  f"(CC{switch.get('cc', '?')}, vrednost: {switch.get('value', '?')}) - {status}")
        
        # Pošalji potvrdu
        response = {
            "type": "config_ack",
            "status": "success",
            "message": f"Konfiguracija primljena za {len(data.get('switches', []))} tastera"
        }
        self.send_response(response)
    
    def handle_ping(self, data):
        print(f"Ping poruka: {data.get('message', 'N/A')}")
        
        # Pošalji pong odgovor
        response = {
            "type": "pong",
            "status": "ok",
            "message": "MIDI Device aktivan"
        }
        self.send_response(response)
    
    def send_response(self, response):
        try:
            json_response = json.dumps(response, ensure_ascii=False)
            self.connection.write((json_response + '\n').encode('utf-8'))
            self.connection.flush()
            print(f"Poslat odgovor: {response.get('message', 'N/A')}")
        except Exception as e:
            print(f"Greška pri slanju odgovora: {e}")
    
    def stop(self):
        self.running = False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Upotreba: python midi_device_simulator.py <serial_port>")
        print("Primjer: python midi_device_simulator.py /dev/ttyUSB0")
        sys.exit(1)
    
    port = sys.argv[1]
    simulator = MIDIDeviceSimulator(port)
    
    try:
        simulator.start()
    except KeyboardInterrupt:
        print("\nZaustavljanje simulatora...")
        simulator.stop()
