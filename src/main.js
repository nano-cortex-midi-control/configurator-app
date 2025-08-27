const { app, BrowserWindow, Menu, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const axios = require('axios');

let mainWindow;
let flaskProcess;

// Pokretanje Flask servera
function startFlaskServer() {
  const pythonExecutable = process.platform === 'win32' ? 'python' : 'python3';
  const flaskScript = path.join(__dirname, '..', 'backend', 'app.py');
  
  flaskProcess = spawn(pythonExecutable, [flaskScript], {
    cwd: path.join(__dirname, '..', 'backend')
  });

  flaskProcess.stdout.on('data', (data) => {
    console.log(`Flask stdout: ${data}`);
  });

  flaskProcess.stderr.on('data', (data) => {
    console.error(`Flask stderr: ${data}`);
  });
}

// Provera da li je Flask server spreman
async function waitForFlask() {
  const maxAttempts = 30;
  let attempts = 0;
  
  while (attempts < maxAttempts) {
    try {
      await axios.get('http://localhost:5000/health');
      console.log('Flask server je spreman!');
      return true;
    } catch (error) {
      attempts++;
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
  }
  
  console.error('Flask server se nije pokrenuo na vreme');
  return false;
}

function createWindow() {
  // Kreiranje browser window-a
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
      preload: path.join(__dirname, 'preload.js')
    },
    icon: path.join(__dirname, '..', 'assets', 'icon.png'), // Dodajte ikonicu
    show: false
  });

  // Menu
  const template = [
    {
      label: 'Fajl',
      submenu: [
        {
          label: 'Novi projekt',
          accelerator: 'CmdOrCtrl+N',
          click: () => {
            mainWindow.webContents.send('menu-new-project');
          }
        },
        {
          label: 'Otvori projekt',
          accelerator: 'CmdOrCtrl+O',
          click: () => {
            mainWindow.webContents.send('menu-open-project');
          }
        },
        {
          label: 'Sačuvaj',
          accelerator: 'CmdOrCtrl+S',
          click: () => {
            mainWindow.webContents.send('menu-save');
          }
        },
        { type: 'separator' },
        {
          label: 'Izađi',
          accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
          click: () => {
            app.quit();
          }
        }
      ]
    },
    {
      label: 'Uredi',
      submenu: [
        { role: 'undo', label: 'Poništi' },
        { role: 'redo', label: 'Ponovi' },
        { type: 'separator' },
        { role: 'cut', label: 'Iseci' },
        { role: 'copy', label: 'Kopiraj' },
        { role: 'paste', label: 'Nalepi' }
      ]
    },
    {
      label: 'Prikaži',
      submenu: [
        { role: 'reload', label: 'Ponovno učitaj' },
        { role: 'forceReload', label: 'Prisilno ponovno učitaj' },
        { role: 'toggleDevTools', label: 'Developer Tools' },
        { type: 'separator' },
        { role: 'resetZoom', label: 'Resetuj zoom' },
        { role: 'zoomIn', label: 'Uvećaj' },
        { role: 'zoomOut', label: 'Umanji' },
        { type: 'separator' },
        { role: 'togglefullscreen', label: 'Pun ekran' }
      ]
    },
    {
      label: 'Pomoć',
      submenu: [
        {
          label: 'O aplikaciji',
          click: () => {
            mainWindow.webContents.send('menu-about');
          }
        }
      ]
    }
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);

  // Učitavanje aplikacije
  mainWindow.loadURL('http://localhost:5000');

  // Prikaži prozor kada je spreman
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  // Otvori DevTools u development modu
  if (process.env.NODE_ENV === 'development') {
    mainWindow.webContents.openDevTools();
  }
}

// IPC komunikacija
ipcMain.handle('get-app-version', () => {
  return app.getVersion();
});

ipcMain.handle('get-platform', () => {
  return process.platform;
});

// App event listeners
app.whenReady().then(async () => {
  console.log('Electron app je spreman, pokretanje Flask servera...');
  
  // Pokretanje Flask servera
  startFlaskServer();
  
  // Čekanje da se Flask server pokrene
  const flaskReady = await waitForFlask();
  
  if (flaskReady) {
    createWindow();
  } else {
    console.error('Ne mogu da pokretam Flask server');
    app.quit();
  }

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', () => {
  // Zatvaranje Flask procesa
  if (flaskProcess) {
    flaskProcess.kill();
  }
});

// Graceful shutdown
process.on('SIGTERM', () => {
  if (flaskProcess) {
    flaskProcess.kill();
  }
  app.quit();
});

process.on('SIGINT', () => {
  if (flaskProcess) {
    flaskProcess.kill();
  }
  app.quit();
});
