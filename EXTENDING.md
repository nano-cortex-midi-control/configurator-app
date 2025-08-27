# Proširivanje Configurator aplikacije

Ovaj fajl sadrži instrukcije za proširivanje funkcionalnosti aplikacije.

## Dodavanje novih tipova konfiguracija

### 1. Proširivanje backend modela

U `backend/app.py`, možete dodati nova polja u konfiguracije:

```python
new_config = {
    'id': len(configurations) + 1,
    'name': data['name'],
    'description': data.get('description', ''),
    'type': data.get('type', 'basic'),  # Novi tip
    'category': data.get('category', ''),  # Nova kategorija
    'settings': data.get('settings', {}),
    'metadata': data.get('metadata', {}),  # Nova meta podešavanja
    'created_at': datetime.now().isoformat(),
    'updated_at': datetime.now().isoformat()
}
```

### 2. Proširivanje frontend UI-ja

U `frontend/templates/index.html`, dodajte nova polja:

```html
<div class="form-group">
    <label for="configType">Tip konfiguracije:</label>
    <select id="configType" name="type">
        <option value="basic">Osnovna</option>
        <option value="advanced">Napredna</option>
        <option value="custom">Prilagođena</option>
    </select>
</div>
```

### 3. Ažuriranje JavaScript logike

U `frontend/static/js/app.js`, ažurirajte funkcije:

```javascript
createConfiguration() {
    const configData = {
        name: formData.get('name'),
        description: formData.get('description'),
        type: formData.get('type'),
        category: formData.get('category'),
        settings: {},
        metadata: {}
    };
    // ...ostatak koda
}
```

## Dodavanje novih API endpoint-a

### 1. Kreiranje novog endpoint-a

```python
@app.route('/api/configurations/export', methods=['GET'])
def export_configurations():
    """Izvezi sve konfiguracije u JSON format"""
    try:
        config_file = os.path.join(app.config['DATA_DIR'], 'configurations.json')
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                configurations = json.load(f)
                
            response = make_response(json.dumps(configurations, ensure_ascii=False, indent=2))
            response.headers['Content-Type'] = 'application/json'
            response.headers['Content-Disposition'] = 'attachment; filename=configurations.json'
            return response
        else:
            return jsonify({'error': 'Nema konfiguracija za izvoz'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### 2. Povezivanje sa frontend-om

```javascript
async exportConfigurations() {
    try {
        const response = await fetch('/api/configurations/export');
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = 'configurations.json';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
        }
    } catch (error) {
        this.showToast('Greška pri izvozu konfiguracija', 'error');
    }
}
```

## Dodavanje baze podataka

Za veće aplikacije, preporučuje se korišćenje baze podataka umesto JSON fajlova.

### 1. Instaliranje SQLAlchemy

```bash
pip install flask-sqlalchemy
```

### 2. Kreiranje modela

```python
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)

class Configuration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    settings = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

## Dodavanje autentifikacije

### 1. Instaliranje Flask-Login

```bash
pip install flask-login
```

### 2. Kreiranje User modela

```python
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
```

## Personalizovanje Electron aplikacije

### 1. Promena ikonice

Zamenite fajl u `assets/icon.png` sa vašom ikonom.

### 2. Promena menu-a

U `src/main.js`, ažurirajte `template` varijablu:

```javascript
const template = [
    {
        label: 'Vaš Menu',
        submenu: [
            {
                label: 'Vaša opcija',
                accelerator: 'CmdOrCtrl+Y',
                click: () => {
                    // Vaša logika
                }
            }
        ]
    }
];
```

### 3. Dodavanje novih Electron funkcionalnosti

```javascript
// U src/preload.js
contextBridge.exposeInMainWorld('electronAPI', {
    // Postojeći API...
    
    // Novi API
    saveFile: (data) => ipcRenderer.invoke('save-file', data),
    openFile: () => ipcRenderer.invoke('open-file')
});

// U src/main.js
ipcMain.handle('save-file', async (event, data) => {
    const { dialog } = require('electron');
    const fs = require('fs');
    
    const result = await dialog.showSaveDialog(mainWindow, {
        filters: [{ name: 'JSON fajlovi', extensions: ['json'] }]
    });
    
    if (!result.canceled) {
        fs.writeFileSync(result.filePath, JSON.stringify(data, null, 2));
        return { success: true };
    }
    
    return { success: false };
});
```

## Testiranje

### 1. Backend testiranje

Kreirajte `backend/tests/test_app.py`:

```python
import unittest
import json
from app import app

class ConfigurationTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_health_check(self):
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        
    def test_get_configurations(self):
        response = self.app.get('/api/configurations')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
```

### 2. Frontend testiranje

Za frontend testiranje možete koristiti Jest ili Cypress.

## Deployment

### 1. Kreiranje standalone aplikacije

```bash
npm run dist
```

### 2. Docker kontejner

Kreirajte `Dockerfile`:

```dockerfile
FROM node:16-alpine

WORKDIR /app
COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 5000
CMD ["npm", "start"]
```

Ove instrukcije će vam omogućiti da proširite aplikaciju prema vašim potrebama.
