const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
    // Menu event listeners
    onMenuNewProject: (callback) => {
        ipcRenderer.on('menu-new-project', callback);
    },
    onMenuSave: (callback) => {
        ipcRenderer.on('menu-save', callback);
    },
    onMenuAbout: (callback) => {
        ipcRenderer.on('menu-about', callback);
    },
    
    // Dialog functions
    showMessageBox: (options) => {
        return ipcRenderer.invoke('show-message-box', options);
    },
    showSaveDialog: (options) => {
        return ipcRenderer.invoke('show-save-dialog', options);
    },
    showOpenDialog: (options) => {
        return ipcRenderer.invoke('show-open-dialog', options);
    },
    
    // Platform information
    platform: process.platform,
    
    // Remove listeners
    removeAllListeners: (channel) => {
        ipcRenderer.removeAllListeners(channel);
    }
});

// Log that preload script loaded successfully
console.log('Preload script loaded successfully');
