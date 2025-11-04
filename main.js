const { app, BrowserWindow, Menu, ipcMain, dialog } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

// Keep a global reference of the window object
let mainWindow;
let backendProcess;

// Backend server process
function startBackendServer() {
    const fs = require('fs');
    const isWindows = process.platform === 'win32';

    console.log('Starting backend server...');

    if (app.isPackaged) {
        // In production, run bundled backend binary from resources
        const backendDir = path.join(process.resourcesPath, 'backend-bin');
        const backendExecutable = path.join(
            backendDir,
            isWindows ? 'app.exe' : 'app'
        );

        if (!fs.existsSync(backendExecutable)) {
            console.error('Bundled backend binary not found at:', backendExecutable);
            return;
        }

        try {
            // Ensure executable permission on Unix-like systems
            if (!isWindows) {
                fs.chmodSync(backendExecutable, 0o755);
            }
        } catch (e) {
            console.warn('Could not set executable permissions for backend binary:', e.message);
        }

        // Persistent DB under Electron userData
        const userDataDir = app.getPath('userData');
        const dbPath = path.join(userDataDir, 'database.db');
        try {
            const dbDir = path.dirname(dbPath);
            require('fs').mkdirSync(dbDir, { recursive: true });
        } catch (e) {
            console.warn('Could not ensure userData directory exists:', e.message);
        }

        console.log('Running packaged backend:', backendExecutable);
        backendProcess = spawn(backendExecutable, [], {
            cwd: backendDir,
            stdio: 'pipe',
            env: {
                ...process.env,
                FRONTEND_DIR: path.join(process.resourcesPath, 'frontend'),
                BACKEND_HOST: '127.0.0.1',
                BACKEND_PORT: '5001',
                BACKEND_DEBUG: '0',
                DB_PATH: dbPath
            }
        });
    } else {
        // In development, run Python from local venv
        const venvPath = path.join(__dirname, 'venv');
        const pythonExecutable = isWindows
            ? path.join(venvPath, 'Scripts', 'python.exe')
            : path.join(venvPath, 'bin', 'python');
        const backendPath = path.join(__dirname, 'backend', 'app.py');

        if (!fs.existsSync(pythonExecutable)) {
            console.error('Virtual environment not found. Please run:');
            console.error('python3 -m venv venv && source venv/bin/activate && pip install -r backend/requirements.txt');
            return;
        }

        console.log('Python executable:', pythonExecutable);
        console.log('Backend path:', backendPath);

        backendProcess = spawn(pythonExecutable, [backendPath], {
            cwd: __dirname,
            stdio: 'pipe'
        });
    }

    backendProcess.stdout.on('data', (data) => {
        console.log(`Backend: ${data}`);
    });

    backendProcess.stderr.on('data', (data) => {
        console.error(`Backend Error: ${data}`);
    });

    backendProcess.on('close', (code) => {
        console.log(`Backend process exited with code ${code}`);
    });
}

function createWindow() {
    // Create the browser window
    mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        minWidth: 800,
        minHeight: 600,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            enableRemoteModule: false,
            preload: path.join(__dirname, 'preload.js')
        },
        icon: path.join(__dirname, 'assets', 'icon.png'), // Dodajte ikonu ako je imate
        show: false, // Ne prikazuj prozor dok se potpuno ne učita
        titleBarStyle: 'default'
    });

    // Wait for backend to start before loading the page
    setTimeout(() => {
        // Load the frontend
        mainWindow.loadURL('http://localhost:5001');
        
        // Show window when ready
        mainWindow.once('ready-to-show', () => {
            mainWindow.show();
            
            // Focus on the window
            if (process.platform === 'darwin') {
                app.focus();
            }
        });
    }, 3000); // Wait 3 seconds for backend to start

    // Handle window events
    mainWindow.on('closed', () => {
        mainWindow = null;
    });

    // Handle external links
    mainWindow.webContents.setWindowOpenHandler(({ url }) => {
        require('electron').shell.openExternal(url);
        return { action: 'deny' };
    });

    // Development tools in development mode
    if (process.env.NODE_ENV === 'development') {
        mainWindow.webContents.openDevTools();
    }
}

// Application menu
function createMenu() {
    const template = [
        {
            label: 'File',
            submenu: [
                {
                    label: 'Nova konfiguracija',
                    accelerator: 'CmdOrCtrl+N',
                    click: () => {
                        mainWindow.webContents.send('menu-new-project');
                    }
                },
                {
                    label: 'Sačuvaj konfiguraciju',
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
            label: 'Edit',
            submenu: [
                { role: 'undo', label: 'Poništi' },
                { role: 'redo', label: 'Ponovi' },
                { type: 'separator' },
                { role: 'cut', label: 'Iseci' },
                { role: 'copy', label: 'Kopiraj' },
                { role: 'paste', label: 'Nalepi' },
                { role: 'selectall', label: 'Izaberi sve' }
            ]
        },
        {
            label: 'View',
            submenu: [
                { role: 'reload', label: 'Osvezi' },
                { role: 'forceReload', label: 'Forsiraj osvežavanje' },
                { role: 'toggleDevTools', label: 'Developer Tools' },
                { type: 'separator' },
                { role: 'resetZoom', label: 'Reset Zoom' },
                { role: 'zoomIn', label: 'Uvećaj' },
                { role: 'zoomOut', label: 'Umanji' },
                { type: 'separator' },
                { role: 'togglefullscreen', label: 'Ceo ekran' }
            ]
        },
        {
            label: 'Help',
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

    // macOS specific menu adjustments
    if (process.platform === 'darwin') {
        template.unshift({
            label: app.getName(),
            submenu: [
                { role: 'about', label: 'O aplikaciji' },
                { type: 'separator' },
                { role: 'services', label: 'Servisi' },
                { type: 'separator' },
                { role: 'hide', label: 'Sakrij' },
                { role: 'hideothers', label: 'Sakrij ostale' },
                { role: 'unhide', label: 'Prikaži sve' },
                { type: 'separator' },
                { role: 'quit', label: 'Izađi' }
            ]
        });

        // Window menu
        template[4].submenu = [
            { role: 'close', label: 'Zatvori' },
            { role: 'minimize', label: 'Minimiziraj' },
            { role: 'zoom', label: 'Zoom' },
            { type: 'separator' },
            { role: 'front', label: 'Dovedi u prvi plan' }
        ];
    }

    const menu = Menu.buildFromTemplate(template);
    Menu.setApplicationMenu(menu);
}

// IPC handlers for communication with renderer process
ipcMain.handle('show-message-box', async (event, options) => {
    const result = await dialog.showMessageBox(mainWindow, options);
    return result;
});

ipcMain.handle('show-save-dialog', async (event, options) => {
    const result = await dialog.showSaveDialog(mainWindow, options);
    return result;
});

ipcMain.handle('show-open-dialog', async (event, options) => {
    const result = await dialog.showOpenDialog(mainWindow, options);
    return result;
});

// App event handlers
app.whenReady().then(() => {
    // Start backend server
    startBackendServer();
    
    // Create window and menu
    createWindow();
    createMenu();

    app.on('activate', () => {
        // On macOS re-create window when dock icon is clicked
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow();
        }
    });
});

app.on('window-all-closed', () => {
    // Quit when all windows are closed, except on macOS
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('before-quit', () => {
    // Kill backend process when app is quitting
    if (backendProcess) {
        backendProcess.kill();
    }
});

// Security: Prevent new window creation
app.on('web-contents-created', (event, contents) => {
    contents.on('new-window', (event, navigationUrl) => {
        event.preventDefault();
        require('electron').shell.openExternal(navigationUrl);
    });
});

// Handle certificate errors
app.on('certificate-error', (event, webContents, url, error, certificate, callback) => {
    if (url.startsWith('http://localhost:')) {
        // Allow localhost connections
        event.preventDefault();
        callback(true);
    } else {
        callback(false);
    }
});

console.log('MIDI Configurator Electron App Started');
