# MIDI Configurator - Implementacija Serial Komunikacije

## Implementirane funkcionalnosti:

### 1. Backend implementacija (`serial_comm.py`):
- **SerialCommunicator klasa** za upravljanje serial komunikacijom
- Automatska konekcija/diskonekcija sa USB portovima
- Kreiranje MIDI konfiguracije u JSON formatu
- Slanje konfiguracije preko serial porta

### 2. JSON format poruke:
```json
{
  "type": "set_config",
  "switches": [
    {
      "id": 0,           // ID tastera (0-5)
      "name": "Naziv",   // Naziv komande
      "channel": 1,      // MIDI kanal (zakucano na 1)
      "cc": 20,          // Control Change broj (20-25)
      "value": 127,      // Vrednost komande
      "enabled": true    // Da li je taster aktivan
    }
  ],
  "timestamp": "2025-08-27T16:56:35.123456",
  "source": "MIDI Configurator"
}
```

### 3. API endpoints:
- **POST /api/configuration** - Šalje konfiguraciju preko serial porta
- **POST /api/usb-ports/test-serial** - Testira serial komunikaciju

### 4. Frontend ažuriranje:
- Ažuriran `sendConfiguration()` za korišćenje novog API-ja
- Dodana bolja povratna informacija za korisnika
- Dodano testiranje serial komunikacije

### 5. Funkcionalnost:
- **Automatska detekcija USB portova** (real-time)
- **Test konekcije** sa osnovnim i serial testiranjem
- **Slanje MIDI konfiguracije** klikom na "KONFIGURISI"
- **Mapiranje tastera** na CC 20-25
- **Potpora za odgovor uređaja**

### 6. Test simulator (`midi_device_simulator.py`):
- Simulira MIDI uređaj koji prima konfiguraciju
- Prikazuje primljenu konfiguraciju
- Šalje potvrde nazad

## Kako koristiti:

1. **Pokretanje backend-a:**
   ```bash
   cd backend
   python app.py
   ```

2. **Otvaranje aplikacije:**
   - Idi na http://127.0.0.1:5001

3. **Kreiranje komandi:**
   - Dodaj komande sa nazivom i vrednošću (0-65535)

4. **Mapiranje tastera:**
   - Mapiraj komande na tastere 1-6

5. **Slanje konfiguracije:**
   - Izaberi USB port
   - Testiraj konekciju (opcionalno)
   - Klikni "KONFIGURISI"

## JSON poruka koja se šalje:
Kada klikneš "KONFIGURISI", šalje se JSON poruka preko serial porta sa:
- Tipom: "set_config"
- Nizom tastera sa mapiranim komandama
- CC vrednostima 20-25 za tastere 0-5
- Kanal zakucan na 1
- Enabled/disabled status

Implementacija je kompletna i spremna za testiranje sa stvarnim MIDI uređajima!
