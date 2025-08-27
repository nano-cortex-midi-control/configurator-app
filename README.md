# MIDI Configurator App

Desktop aplikacija za konfiguraciju MIDI kontrolera napravljena sa Electron frontend-om i Flask backend-om.

## Karakteristike

- 🖥️ **Desktop aplikacija** - Koristi Electron za native desktop interfejs
- 🎵 **MIDI kontrola** - Mapiranje tastera na MIDI komande
- 🐍 **Flask backend** - Python Flask server za API i komunikaciju sa uređajem
- 💾 **SQLite baza** - Lokalna baza podataka za komande i mapiranja
- 🎨 **Moderni UI** - Responzivni dizajn sa tab navigacijom
- 🔌 **USB komunikacija** - Direktna komunikacija sa MIDI uređajem
- ⚡ **Real-time konfiguracija** - Trenutno slanje konfiguracije na uređaj

## Funkcionalnosti

### Config Tab
- **Upravljanje komandama**: Dodavanje, editovanje i brisanje MIDI komandi
- **Komande se sastoje od**: Naziv (string) i Vrednost (INT 0-65535)
- **Lista komandi**: Pregled svih dostupnih komandi

### Map Tab
- **6 tastera** - Mapiranje komandi na 6 fizičkih tastera
- **Vizuelni prikaz** - Krugovi predstavljaju tastere sa brojevima
- **Dropdown selekcija** - Izbor komande za svaki taster
- **Real-time preview** - Prikaz mapirane komande ispod svakog tastera

### USB Management
- **Auto-detekcija portova** - Automatsko otkrivanje dostupnih USB portova
- **Port selekcija** - Dropdown meni za izbor USB porta
- **Konfiguracija** - Slanje trenutnog mapiranja na uređaj klikom na KONFIGURISI

## Struktura projekta

```
configurator-app/
├── src/                    # Electron main proces
│   ├── main.js            # Glavna Electron aplikacija
│   └── preload.js         # Preload script za bezbednu komunikaciju
├── frontend/              # Web frontend  
│   ├── templates/
│   │   └── index.html     # MIDI Configurator UI
│   └── static/
│       ├── css/
│       │   └── style.css  # Stilovi za tabove i button grid
│       └── js/
│           └── app.js     # MIDI Configurator logika
├── backend/               # Flask backend (ZA IMPLEMENTACIJU)
│   ├── app.py            # Flask server sa MIDI API
│   └── requirements.txt  # Python dependencies
├── BACKEND_API.md        # API specifikacija za implementaciju
├── package.json          # Node.js konfiguracija
└── README.md
```

## Instalacija

### Preduslovi

- Node.js (v16 ili noviji)
- Python 3.8+
- npm ili yarn

### Korak 1: Kloniraj ili download projekat

```bash
git clone <repository-url>
cd configurator-app
```

### Korak 2: Instaliraj Node.js dependencies

```bash
npm install
```

### Korak 3: Implementiraj backend

Backend API trenutno nije implementiran. Sledite instrukcije u `BACKEND_API.md` fajlu da implementirate:

1. SQLite bazu podataka
2. API endpoint-ove za komande
3. USB port detekciju
4. MIDI komunikaciju sa uređajem

```bash
cd backend
pip install -r requirements.txt
# Implementiraj API endpoint-ove prema BACKEND_API.md
cd ..
```

## Pokretanje

### Development mode

```bash
npm run dev
```

### Production mode

```bash
npm start
```

## Frontend API Pozivi

Frontend pravi sledeće API pozive koje backend treba da implementira:

### Komande
- `GET /api/commands` - Lista svih komandi
- `POST /api/commands` - Kreiranje nove komande
- `PUT /api/commands/{id}` - Ažuriranje komande
- `DELETE /api/commands/{id}` - Brisanje komande

### USB Portovi
- `GET /api/usb-ports` - Lista dostupnih USB portova

### Mapiranje tastera
- `GET /api/button-mappings` - Trenutno mapiranje tastera
- `POST /api/button-mappings` - Ažuriranje mapiranja

### Konfiguracija uređaja
- `POST /api/configure` - Slanje konfiguracije na uređaj

Detaljnu specifikaciju API-ja pogledajte u `BACKEND_API.md`.

## UI Komponente

### Header
- **Tab navigacija**: Config i Map tabovi
- **USB port selekcija**: Dropdown za izbor porta
- **KONFIGURISI dugme**: Slanje konfiguracije na uređaj

### Config Tab
- **Lista komandi**: Tabela sa naziv/vrednost/akcije
- **Dodaj komandu**: Modal dialog za novu komandu
- **Edit/Delete**: Akcije za postojeće komande

### Map Tab
- **6 tastera**: Vizuelni prikaz u 2x3 grid-u
- **Krugovi sa brojevima**: Predstavljaju fizičke tastere
- **Dropdown ispod**: Selekcija komande za svaki taster
- **Live preview**: Prikaz naziva mapirane komande

### Status Bar
- **Connection status**: Indikator veze sa uređajem
- **Command count**: Broj definisanih komandi  
- **Mapped buttons**: Broj mapiranih tastera (X/6)

## Izgradnja za distribuciju

```bash
npm run build
```

ili

```bash
npm run dist
```

Ovo će kreirati distribuciju u `dist/` folderu.

## Konfiguracija

### Electron

Electron konfiguracija se nalazi u `src/main.js`. Možete prilagoditi:
- Veličinu prozora
- Menu opcije
- Ikonce
- Bezbednosne postavke

### Flask

Flask konfiguracija se nalazi u `backend/app.py`. Možete prilagoditi:
- Port servera
- CORS postavke
- Lokaciju data fajlova
- Secret key

## Dodavanje novih funkcionalnosti

### Backend (Flask)

1. Dodaj novi endpoint u `backend/app.py`
2. Implementiraj logiku
3. Testiraj preko `/health` endpoint-a

### Frontend (Electron)

1. Dodaj novi UI u `frontend/templates/index.html`
2. Dodaj stilove u `frontend/static/css/style.css`
3. Implementiraj logiku u `frontend/static/js/app.js`
4. Integriši sa Electron API-jem preko `src/preload.js`

## Troubleshooting

### Flask server se ne pokreće

- Proverite da li je Python instaliran
- Proverite da li su instalirane sve dependencies iz `requirements.txt`
- Proverite da li je port 5000 slobodan

### Electron aplikacija se ne pokreće

- Proverite da li je Node.js instaliran
- Instalirajte dependencies sa `npm install`
- Proverite da li Flask server radi na portu 5000

### Podaci se ne čuvaju

- Proverite da li postoji `backend/data/` direktorijum
- Proverite dozvole za pisanje u direktorijum

## Razvoj

Za doprinošenje projektu:

1. Fork repository
2. Kreiraj feature branch
3. Implementiraj promene
4. Testiraj
5. Pošalji pull request

## Licenca

MIT License - pogledaj LICENSE fajl za detalje.