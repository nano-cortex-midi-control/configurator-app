# Backend API Specifikacija za MIDI Configurator

Ovaj dokument definiše API endpoint-ove koje backend treba da implementira.

## Baza podataka (SQLite)

### Tabele:

#### `commands` tabela
```sql
CREATE TABLE commands (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    value INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### `button_mappings` tabela
```sql
CREATE TABLE button_mappings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    button_number INTEGER NOT NULL UNIQUE CHECK (button_number >= 1 AND button_number <= 6),
    command_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (command_id) REFERENCES commands(id) ON DELETE SET NULL
);
```

#### `usb_ports` tabela (opciono - može se generisati dinamički)
```sql
CREATE TABLE usb_ports (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    is_available BOOLEAN DEFAULT TRUE,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## API Endpoints

### 1. Komande (Commands)

#### GET /api/commands
Vraća sve komande.

**Response:**
```json
{
    "success": true,
    "data": [
        {
            "id": 1,
            "name": "Start Recording",
            "value": 100,
            "created_at": "2024-01-01T10:00:00Z",
            "updated_at": "2024-01-01T10:00:00Z"
        }
    ]
}
```

#### POST /api/commands
Kreira novu komandu.

**Request Body:**
```json
{
    "name": "Start Recording",
    "value": 100
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "id": 1,
        "name": "Start Recording",
        "value": 100,
        "created_at": "2024-01-01T10:00:00Z",
        "updated_at": "2024-01-01T10:00:00Z"
    }
}
```

#### PUT /api/commands/{id}
Ažurira postojeću komandu.

**Request Body:**
```json
{
    "name": "Stop Recording",
    "value": 101
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "id": 1,
        "name": "Stop Recording",
        "value": 101,
        "created_at": "2024-01-01T10:00:00Z",
        "updated_at": "2024-01-01T10:30:00Z"
    }
}
```

#### DELETE /api/commands/{id}
Briše komandu.

**Response:**
```json
{
    "success": true,
    "message": "Command deleted successfully"
}
```

### 2. USB Portovi

#### GET /api/usb-ports
Vraća dostupne USB portove.

**Response:**
```json
{
    "success": true,
    "data": [
        {
            "id": "COM1",
            "name": "COM1 - Arduino Uno",
            "description": "Arduino Uno on COM1",
            "is_available": true
        },
        {
            "id": "COM3",
            "name": "COM3 - Generic Serial",
            "description": "Generic Serial Device",
            "is_available": true
        }
    ]
}
```

### 3. Mapiranje dugmića

#### GET /api/button-mappings
Vraća trenutno mapiranje dugmića.

**Response:**
```json
{
    "success": true,
    "data": {
        "1": 1,
        "2": 3,
        "4": 2
    }
}
```

#### POST /api/button-mappings
Ažurira mapiranje dugmića (može se slati parcijalno).

**Request Body:**
```json
{
    "1": 1,
    "2": 3,
    "3": null,
    "4": 2
}
```

**Response:**
```json
{
    "success": true,
    "message": "Button mappings updated successfully"
}
```

### 4. Konfiguracija uređaja

#### POST /api/configure
Šalje konfiguraciju na uređaj preko USB porta.

**Request Body:**
```json
{
    "usb_port": "COM1",
    "button_mappings": {
        "1": 1,
        "2": 3,
        "4": 2
    }
}
```

**Response (uspeh):**
```json
{
    "success": true,
    "message": "Configuration sent successfully to device",
    "device_response": "OK"
}
```

**Response (greška):**
```json
{
    "success": false,
    "error": "Failed to connect to device on COM1"
}
```

## Implementacijske napomene

### 1. Validacija podataka
- Naziv komande: obavezno, maksimalno 100 karaktera
- Vrednost komande: obavezno, broj između 0 i 65535
- Button number: mora biti između 1 i 6

### 2. USB komunikacija
Backend treba da implementira komunikaciju sa uređajem preko serijskog porta. Protokol komunikacije zavisi od hardware-a.

Primer slanja konfiguracije:
```python
import serial

def send_configuration(port, mappings):
    try:
        ser = serial.Serial(port, 9600, timeout=2)
        
        # Format poruke zavisi od protokola uređaja
        for button, command_id in mappings.items():
            command = get_command_by_id(command_id)
            message = f"SET_BUTTON:{button}:{command.value}\n"
            ser.write(message.encode())
            
        ser.close()
        return True, "Configuration sent"
    except Exception as e:
        return False, str(e)
```

### 3. Automatsko otkrivanje USB uređaja
```python
import serial.tools.list_ports

def get_available_ports():
    ports = []
    for port in serial.tools.list_ports.comports():
        ports.append({
            'id': port.device,
            'name': f"{port.device} - {port.description}",
            'description': port.description,
            'is_available': True
        })
    return ports
```

### 4. Greške i HTTP status kodovi
- 200: Uspešna operacija
- 400: Greška u podacima (validacija)
- 404: Resurs nije pronađen
- 500: Greška servera

### 5. CORS konfiguracija
Backend treba da dozvoli CORS zahteve od Electron aplikacije:
```python
from flask_cors import CORS
CORS(app)
```

## Primer osnovne implementacije (Flask)

```python
from flask import Flask, request, jsonify
import sqlite3
import serial.tools.list_ports

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('midi_config.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS commands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            value INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
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

@app.route('/api/commands', methods=['GET'])
def get_commands():
    # Implementacija
    pass

@app.route('/api/commands', methods=['POST'])
def create_command():
    # Implementacija
    pass

# Ostali endpoint-ovi...

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
```

## Testiranje

Za testiranje endpoint-ova možete koristiti curl komande:

```bash
# Dodavanje komande
curl -X POST http://localhost:5000/api/commands \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Command", "value": 123}'

# Dobijanje komandi
curl http://localhost:5000/api/commands

# Slanje konfiguracije
curl -X POST http://localhost:5000/api/configure \
  -H "Content-Type: application/json" \
  -d '{"usb_port": "COM1", "button_mappings": {"1": 1, "2": 2}}'
```
