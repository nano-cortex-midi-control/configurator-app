# MIDI Configurator - Setup Instrukcije

## ✅ ŠTA JE URAĐENO

### Frontend (Kompletno implementiran)
- **HTML**: Moderna UI sa tabovima Config i Map
- **CSS**: Responzivni dizajn sa button grid layoutom
- **JavaScript**: Kompletna logika za MIDI konfiguraciju
- **Electron integracija**: Desktop app funkcionalnost

### Layout karakteristike:
- **Header**: Tab navigacija (Config/Map) + USB port selekcija + KONFIGURISI dugme
- **Config tab**: Lista komandi sa dodavanjem/editovanjem/brisanjem
- **Map tab**: 6 tastera u 2x3 grid-u sa dropdown selekcijama
- **Status bar**: Prikaz konekcije, broja komandi i mapiranih tastera

## 🔧 ŠTA TREBA DA IMPLEMENTIRATE

### Backend API (SQLite + Flask)

Trebate implementirati sledeće endpoint-ove u `backend/app.py`:

#### 1. Commands API
```python
GET /api/commands          # Lista komandi
POST /api/commands         # Nova komanda  
PUT /api/commands/{id}     # Ažuriranje komande
DELETE /api/commands/{id}  # Brisanje komande
```

#### 2. USB Ports API
```python
GET /api/usb-ports         # Dostupni USB portovi
```

#### 3. Button Mappings API
```python
GET /api/button-mappings   # Trenutno mapiranje
POST /api/button-mappings  # Ažuriranje mapiranja
```

#### 4. Device Configuration API
```python
POST /api/configure        # Slanje na uređaj
```

### SQLite tabele (već kreiran skeleton):
- `commands` - (id, name, value, timestamps)
- `button_mappings` - (button_number, command_id, timestamps)

## 📖 KAKO POČETI

### 1. Instaliraj potrebne pakete
```bash
cd backend
pip install pyserial  # Za USB komunikaciju
```

### 2. Implementiraj API endpoint-ove
Pogledajte `BACKEND_API.md` za detaljnu specifikaciju i `backend/app.py` za skeleton kod.

### 3. Testiranje
```bash
# Pokreni backend
python backend/app.py

# Ili pokreni celu aplikaciju
npm run dev
```

### 4. USB/MIDI komunikacija
Implementirajte `configure_device()` funkciju za slanje podataka na hardware preko serijskog porta.

## 📁 STRUKTURA FAJLOVA

```
configurator-app/
├── frontend/              # ✅ GOTOVO
│   ├── templates/index.html
│   └── static/
│       ├── css/style.css
│       └── js/app.js
├── backend/               # ❌ ZA IMPLEMENTACIJU
│   ├── app.py            # Skeleton sa TODO komentarima
│   └── requirements.txt  # Dependencies
├── src/                  # ✅ GOTOVO - Electron
├── BACKEND_API.md        # 📖 API dokumentacija
└── README.md
```

## 🎯 PRIORITETI

1. **Visoko**: Commands CRUD API (potrebno za osnovnu funkcionalnost)
2. **Srednje**: Button mappings API (za mapiranje tastera) 
3. **Srednje**: USB ports detection (za hardware komunikaciju)
4. **Nisko**: Device configuration (zavisi od hardware protokola)

## 🚀 POKRETANJE

Kada implementirate backend:

```bash
# Development mode
npm run dev

# Production mode  
npm start
```

Frontend je potpuno funkcionalan i čeka samo backend API-je!

## 🔍 DEBUGGING

- **Frontend greške**: DevTools u Electron aplikaciji
- **Backend greške**: Flask debug mode je uključen
- **API pozivi**: Network tab u DevTools

---

**Napomena**: Frontend je dizajniran tako da elegantno rukuje situacijama kada backend nije implementiran, prikazujući odgovarajuće poruke korisniku.
