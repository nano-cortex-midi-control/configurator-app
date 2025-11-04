## Preuzimanje i pokretanje

- Ubuntu/Linux (AppImage): https://github.com/nano-cortex-midi-control/configurator-app/releases/download/linux/MIDI.Configurator-1.0.0.AppImage
- Windows: (bez linka)

Pokretanje na Linuxu (potreban flag):

```bash
./MIDI\ Configurator-1.0.0.AppImage --no-sandbox
```

# MIDI Configurator Desktop App

Desktop aplikacija za konfiguraciju MIDI kontrolera izgrađena sa Electron i Flask backendom.

## Funkcionalnosti

- **Config Tab**: Upravljanje komandama (dodavanje, editovanje, brisanje)
- **Map Tab**: Mapiranje komandi na 6 tastera
- **SQLite baza**: Čuvanje komandi i mapiranja
- **Desktop aplikacija**: Electron wrapper za cross-platform podršku

## Instalacija i pokretanje

### Preduslovi

- Node.js (v14 ili noviji)
- Python 3.7 ili noviji
- pip (Python package manager)

### 1. Kloniraj repozitorijum

```bash
git clone https://github.com/nano-cortex-midi-control/configurator-app.git
cd configurator-app
```

### 2. Instaliraj dependencies

```bash
# Instaliraj Node.js dependencies
npm install

# Instaliraj Python dependencies
cd backend
pip install -r requirements.txt
cd ..
```

Ili koristi skraćenu komandu:

```bash
npm run setup
```

### 3. Pokretanje u development modu

```bash
npm run dev
```

### 4. Pokretanje u production modu

```bash
npm start
```

## Build za distribuciju

### Windows

```bash
npm run build-win
```

### macOS

```bash
npm run build-mac
```

### Linux

```bash
npm run build-linux
```

### Svi platformi

```bash
npm run build
```

Izgrađene aplikacije će se naći u `dist/` direktorijumu.

## Struktura projekta

```
configurator-app/
├── main.js                 # Electron main process
├── preload.js             # Electron preload script
├── package.json           # Node.js dependencies i build config
├── backend/
│   ├── app.py            # Flask backend server
│   ├── requirements.txt  # Python dependencies
│   └── database.db       # SQLite baza (kreirana automatski)
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   └── js/
│   │       └── app.js
│   └── templates/
│       └── index.html
└── assets/               # Ikone za aplikaciju (opciono)
```

## API Dokumentacija

### Komande

- `GET /api/commands` - Dohvati sve komande
- `POST /api/commands` - Kreiraj novu komandu
- `PUT /api/commands/<id>` - Ažuriraj komandu
- `DELETE /api/commands/<id>` - Obriši komandu

### Mapiranje tastera

- `GET /api/button-mappings` - Dohvati mapiranje tastera
- `POST /api/button-mappings` - Ažuriraj mapiranje tastera

### Konfiguracija

- `POST /api/configuration` - Vrati kompletnu konfiguraciju za slanje na uređaj

### USB Portovi

- `GET /api/usb-ports` - Dohvati dostupne USB portove

## Korišćenje

1. **Config tab**:
   - Kliknite "Dodaj komandu" da dodate novu komandu
   - Unesite naziv (string) i vrednost (integer 0-65535)
   - Koristite Edit/Delete dugmad za upravljanje postojećim komandama

2. **Map tab**:
   - Izaberite komandu za svaki od 6 tastera
   - Mapiranje se automatski čuva

3. **Konfiguracija**:
   - Izaberite USB port
   - Kliknite "KONFIGURISI" da pošaljete konfiguraciju na uređaj

## Razvoj

### Backend development

Backend je Flask aplikacija koja:
- Služi frontend fajlove
- Upravlja SQLite bazom
- Pruža REST API endpoints

Za razvoj backenda možete pokrenuti direktno:

```bash
cd backend
python app.py
```

Server će biti dostupan na `http://localhost:5001`

### Frontend development

Frontend koristi vanilla JavaScript i komunicira sa backend API-jem.

### Database schema

```sql
-- Tabela komandi
CREATE TABLE commands (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    value INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela mapiranja tastera
CREATE TABLE button_mappings (
    button_number INTEGER PRIMARY KEY CHECK(button_number >= 1 AND button_number <= 6),
    command_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (command_id) REFERENCES commands (id) ON DELETE SET NULL
);
```

## Troubleshooting

### Backend se ne pokreće

1. Proverite da li je Python instaliran: `python --version`
2. Proverite da li su dependencies instalirani: `pip list`
3. Pokrenite backend ručno: `cd backend && python app.py`

### Electron se ne pokreće

1. Proverite da li je Node.js instaliran: `node --version`
2. Proverite da li su dependencies instalirani: `npm list`
3. Očistite cache: `rm -rf node_modules && npm install`

### Database greške

1. Obriši database.db fajl da se kreira ponovo
2. Restartuj aplikaciju

## Licenca

MIT License - videti LICENSE fajl za detalje.
