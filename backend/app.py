from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime

app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')
CORS(app)  # Omogućava CORS za Electron

# Konfiguracija
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['DATABASE'] = os.path.join(os.path.dirname(__file__), 'midi_config.db')

def init_db():
    """Inicijalizuje SQLite bazu podataka"""
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    
    # Commands tabela
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS commands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            value INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Button mappings tabela
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS button_mappings (
            button_number INTEGER PRIMARY KEY CHECK (button_number >= 1 AND button_number <= 6),
            command_id INTEGER,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (command_id) REFERENCES commands(id) ON DELETE SET NULL
        )
    ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Kreira konekciju sa bazom podataka"""
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

# Health check endpoint
@app.route('/health')
def health_check():
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

# Glavna stranica
@app.route('/')
def index():
    return render_template('index.html')

# =============================================================================
# COMMANDS API - Implementirajte ove endpoint-ove
# =============================================================================

@app.route('/api/commands', methods=['GET'])
def get_commands():
    """
    TODO: Implementiraj - Vraća sve komande iz baze
    
    Trebate:
    1. Napraviti konekciju sa bazom
    2. Izvršiti SELECT query
    3. Vratiti JSON odgovor
    
    Format odgovora: {"success": True, "data": [...]}
    """
    # VAŠA IMPLEMENTACIJA OVDE
    return jsonify({
        'success': False,
        'error': 'Endpoint nije implementiran'
    }), 501

@app.route('/api/commands', methods=['POST'])
def create_command():
    """
    TODO: Implementiraj - Kreira novu komandu
    
    Request body: {"name": "Command Name", "value": 123}
    
    Trebate:
    1. Validirati podatke
    2. Proveriti da li komanda već postoji
    3. Dodati u bazu
    4. Vratiti kreiran objekat
    """
    # VAŠA IMPLEMENTACIJA OVDE
    return jsonify({
        'success': False,
        'error': 'Endpoint nije implementiran'
    }), 501

@app.route('/api/commands/<int:command_id>', methods=['PUT'])
def update_command(command_id):
    """
    TODO: Implementiraj - Ažurira postojeću komandu
    """
    # VAŠA IMPLEMENTACIJA OVDE
    return jsonify({
        'success': False,
        'error': 'Endpoint nije implementiran'
    }), 501

@app.route('/api/commands/<int:command_id>', methods=['DELETE'])
def delete_command(command_id):
    """
    TODO: Implementiraj - Briše komandu
    """
    # VAŠA IMPLEMENTACIJA OVDE
    return jsonify({
        'success': False,
        'error': 'Endpoint nije implementiran'
    }), 501

# =============================================================================
# USB PORTS API - Implementirajte ove endpoint-ove
# =============================================================================

@app.route('/api/usb-ports', methods=['GET'])
def get_usb_ports():
    """
    TODO: Implementiraj - Vraća dostupne USB portove
    
    Trebate:
    1. Koristiti serial.tools.list_ports za otkrivanje portova
    2. Filtrirati relevantne portove
    3. Vratiti listu portova
    
    Format: {"success": True, "data": [{"id": "COM1", "name": "..."}]}
    """
    # PRIMER IMPLEMENTACIJE:
    # import serial.tools.list_ports
    # ports = []
    # for port in serial.tools.list_ports.comports():
    #     ports.append({
    #         'id': port.device,
    #         'name': f"{port.device} - {port.description}",
    #         'description': port.description,
    #         'is_available': True
    #     })
    # return jsonify({'success': True, 'data': ports})
    
    # FALLBACK ZA TESTIRANJE:
    return jsonify({
        'success': True,
        'data': [
            {'id': 'COM1', 'name': 'COM1 - Test MIDI Device'},
            {'id': 'COM3', 'name': 'COM3 - Arduino Uno'},
            {'id': '/dev/ttyUSB0', 'name': '/dev/ttyUSB0 - USB Serial Device'}
        ]
    })

# =============================================================================
# BUTTON MAPPINGS API - Implementirajte ove endpoint-ove
# =============================================================================

@app.route('/api/button-mappings', methods=['GET'])
def get_button_mappings():
    """
    TODO: Implementiraj - Vraća trenutno mapiranje dugmića
    
    Format: {"success": True, "data": {"1": 1, "2": 3, "4": 2}}
    """
    # VAŠA IMPLEMENTACIJA OVDE
    return jsonify({
        'success': True,
        'data': {}  # Prazno mapiranje za početak
    })

@app.route('/api/button-mappings', methods=['POST'])
def update_button_mappings():
    """
    TODO: Implementiraj - Ažurira mapiranje dugmića
    
    Request body: {"1": 1, "2": 3, "3": null, "4": 2}
    null vrednost znači da se mapiranje uklanja
    """
    # VAŠA IMPLEMENTACIJA OVDE
    return jsonify({
        'success': False,
        'error': 'Endpoint nije implementiran'
    }), 501

# =============================================================================
# DEVICE CONFIGURATION API - Implementirajte ovaj endpoint
# =============================================================================

@app.route('/api/configure', methods=['POST'])
def configure_device():
    """
    TODO: Implementiraj - Šalje konfiguraciju na MIDI uređaj
    
    Request body: {
        "usb_port": "COM1",
        "button_mappings": {"1": 1, "2": 3, "4": 2}
    }
    
    Trebate:
    1. Validirati podatke
    2. Dobiti komande iz baze na osnovu mapping-a
    3. Uspostaviti serijsku konekciju
    4. Poslati komande na uređaj
    5. Vratiti rezultat
    
    PRIMER IMPLEMENTACIJE:
    import serial
    
    try:
        ser = serial.Serial(data['usb_port'], 9600, timeout=2)
        
        for button, command_id in data['button_mappings'].items():
            # Dobij komandu iz baze
            command = get_command_by_id(command_id)
            if command:
                # Pošalji komandu na uređaj (format zavisi od protokola)
                message = f"SET_BUTTON:{button}:{command['value']}\n"
                ser.write(message.encode())
                
        ser.close()
        return jsonify({'success': True, 'message': 'Configuration sent'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    """
    data = request.get_json()
    
    if not data or 'usb_port' not in data or 'button_mappings' not in data:
        return jsonify({
            'success': False,
            'error': 'Nedostaju obavezni podaci'
        }), 400
    
    # SIMULACIJA SLANJA - zameniti sa pravom implementacijom
    print(f"Simulacija slanja konfiguracije na {data['usb_port']}")
    print(f"Button mappings: {data['button_mappings']}")
    
    return jsonify({
        'success': True,
        'message': 'Konfiguracija je uspešno poslata (simulacija)',
        'device_response': 'OK'
    })

# =============================================================================
# HELPER FUNKCIJE - Možete koristiti ove kao pomoć
# =============================================================================

def get_command_by_id(command_id):
    """
    Helper funkcija za dobijanje komande po ID-u
    TODO: Implementiraj
    """
    conn = get_db_connection()
    # Implementiraj query
    conn.close()
    return None

def validate_command_data(data):
    """
    Helper funkcija za validaciju podataka komande
    """
    if not data:
        return False, 'Nema podataka'
    
    if not data.get('name', '').strip():
        return False, 'Naziv komande je obavezan'
    
    try:
        value = int(data.get('value', 0))
        if value < 0 or value > 65535:
            return False, 'Vrednost mora biti između 0 i 65535'
    except (TypeError, ValueError):
        return False, 'Vrednost mora biti broj'
    
    return True, None

if __name__ == '__main__':
    # Inicijalizuj bazu podataka pri pokretanju
    init_db()
    print("=" * 60)
    print("MIDI Configurator Backend")
    print("=" * 60)
    print("NAPOMENA: Backend API endpoint-ovi nisu implementirani!")
    print("Pogledajte BACKEND_API.md za detaljne instrukcije.")
    print("=" * 60)
    app.run(host='localhost', port=5000, debug=True)
