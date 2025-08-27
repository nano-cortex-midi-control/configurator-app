const { contextBridge, ipcRenderer } = require('electron');

// Izlaganje API-ja za renderer proces
contextBridge.exposeInMainWorld('electronAPI', {
  // Aplikacijske informacije
  getAppVersion: () => ipcRenderer.invoke('get-app-version'),
  getPlatform: () => ipcRenderer.invoke('get-platform'),
  
  // Menu eventi
  onMenuNewProject: (callback) => ipcRenderer.on('menu-new-project', callback),
  onMenuOpenProject: (callback) => ipcRenderer.on('menu-open-project', callback),
  onMenuSave: (callback) => ipcRenderer.on('menu-save', callback),
  onMenuAbout: (callback) => ipcRenderer.on('menu-about', callback),
  
  // Uklanjanje listener-a
  removeAllListeners: (channel) => ipcRenderer.removeAllListeners(channel)
});
