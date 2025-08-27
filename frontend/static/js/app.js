// MIDI Configurator aplikacija
class MIDIConfiguratorApp {
    constructor() {
        this.commands = [];
        this.buttonMappings = {};
        this.selectedUSBPort = null;
        this.currentEditingCommand = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadCommands();
        this.loadUSBPorts();
        this.loadButtonMappings();
        this.updateStatusBar();
        
        // Electron API setup ako je dostupan
        if (window.electronAPI) {
            this.setupElectronListeners();
        }
    }

    setupEventListeners() {
        // Tab navigation
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchTab(e.target.dataset.tab);
            });
        });

        // USB Port selection
        document.getElementById('usbPortSelect').addEventListener('change', (e) => {
            this.selectedUSBPort = e.target.value;
            this.updateConfigureButton();
            this.updateStatusBar();
            
            // Enable/disable test button
            const testBtn = document.getElementById('testUSBBtn');
            testBtn.disabled = !e.target.value;
        });

        // USB refresh button
        document.getElementById('refreshUSBBtn').addEventListener('click', () => {
            this.loadUSBPorts();
        });

        // USB test button
        document.getElementById('testUSBBtn').addEventListener('click', () => {
            if (this.selectedUSBPort) {
                this.testUSBPort(this.selectedUSBPort);
            }
        });

        // Configure button
        document.getElementById('configureBtn').addEventListener('click', () => {
            this.sendConfiguration();
        });

        // Command management
        document.getElementById('addCommandBtn').addEventListener('click', () => {
            this.showCommandModal();
        });

        document.getElementById('saveCommandBtn').addEventListener('click', () => {
            this.saveCommand();
        });

        // Modal events
        document.querySelectorAll('.modal-close').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.closeModal(e.target.closest('.modal'));
            });
        });

        // Button mapping selects
        for (let i = 1; i <= 6; i++) {
            document.getElementById(`buttonSelect${i}`).addEventListener('change', (e) => {
                this.updateButtonMapping(i, e.target.value);
            });
        }

        // Click outside modal to close
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                this.closeModal(e.target);
            }
        });

        // Form submission
        document.getElementById('commandForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveCommand();
        });
    }

    setupElectronListeners() {
        // Menu eventi
        window.electronAPI.onMenuNewProject(() => {
            this.showCommandModal();
        });

        window.electronAPI.onMenuSave(() => {
            this.sendConfiguration();
        });

        window.electronAPI.onMenuAbout(() => {
            this.showToast('MIDI Configurator v1.0.0 - Desktop aplikacija za MIDI kontrolu', 'info');
        });
    }

    // Tab Management
    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // Update tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tabName}Content`).classList.add('active');
    }

    // USB Port Management
    async loadUSBPorts() {
        try {
            const response = await fetch('http://localhost:5001/api/usb-ports');
            const result = await response.json();
            
            if (result.success) {
                this.renderUSBPorts(result.data);
                
                // Prikaži poruku ako nema portova
                if (result.message) {
                    this.showToast(result.message, 'warning');
                }
                
                // Automatski refresh USB portova svakih 5 sekundi
                if (!this.usbRefreshInterval) {
                    this.usbRefreshInterval = setInterval(() => {
                        this.refreshUSBPorts();
                    }, 5000);
                }
            } else {
                this.showToast('Greška pri učitavanju USB portova: ' + result.error, 'error');
            }
        } catch (error) {
            this.showToast('Greška pri komunikaciji sa serverom', 'error');
            console.error('Greška:', error);
            
            // Fallback - dodaj test portove
            this.renderUSBPorts([
                { id: 'COM1', name: 'COM1 - Test Port 1' },
                { id: 'COM2', name: 'COM2 - Test Port 2' }
            ]);
        }
    }

    async refreshUSBPorts() {
        try {
            const response = await fetch('http://localhost:5001/api/usb-ports');
            const result = await response.json();
            
            if (result.success) {
                const currentSelection = document.getElementById('usbPortSelect').value;
                this.renderUSBPorts(result.data);
                
                // Pokušaj da zadržiš trenutnu selekciju
                if (currentSelection) {
                    const select = document.getElementById('usbPortSelect');
                    const option = Array.from(select.options).find(opt => opt.value === currentSelection);
                    if (option) {
                        select.value = currentSelection;
                    } else {
                        // Port je nestao, resetuj selekciju
                        this.selectedUSBPort = null;
                        this.updateConfigureButton();
                        this.updateStatusBar();
                        this.showToast(`USB port ${currentSelection} više nije dostupan`, 'warning');
                    }
                }
            }
        } catch (error) {
            // Tiho ignorišemo greške pri refresh-u
            console.warn('USB port refresh failed:', error);
        }
    }

    async testUSBPort(portId) {
        try {
            this.showToast('Testiranje USB porta...', 'info');
            
            // Prvo testiraj osnovnu dostupnost
            const basicResponse = await fetch('http://localhost:5001/api/usb-ports/test', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ portId })
            });
            
            const basicResult = await basicResponse.json();
            
            if (basicResult.success && basicResult.data.is_connected) {
                // Ako je osnovno testiranje uspješno, testiraj serial komunikaciju
                const serialResponse = await fetch('http://localhost:5001/api/usb-ports/test-serial', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ portId })
                });
                
                const serialResult = await serialResponse.json();
                
                if (serialResult.success) {
                    let message = `Port ${portId} je dostupan i spreman za korišćenje`;
                    if (serialResult.data.device_response) {
                        message += ` ✓ Uređaj odgovara: ${serialResult.data.device_response}`;
                    } else {
                        message += ` ✓ Serial komunikacija radi`;
                    }
                    this.showToast(message, 'success');
                    return true;
                } else {
                    this.showToast(`Port ${portId} je dostupan ali serial komunikacija ne radi: ${serialResult.error}`, 'warning');
                    return false;
                }
            } else {
                const message = `Port ${portId} nije dostupan ili je zauzet`;
                this.showToast(message, 'warning');
                return false;
            }
        } catch (error) {
            this.showToast('Greška pri komunikaciji sa serverom', 'error');
            console.error('Greška:', error);
            return false;
        }
    }

    renderUSBPorts(ports) {
        const select = document.getElementById('usbPortSelect');
        select.innerHTML = '<option value="">Izaberite USB port...</option>';
        
        if (ports.length === 0) {
            const option = document.createElement('option');
            option.value = '';
            option.textContent = 'Nema dostupnih portova';
            option.disabled = true;
            select.appendChild(option);
            return;
        }
        
        ports.forEach(port => {
            const option = document.createElement('option');
            option.value = port.id;
            option.textContent = port.name;
            select.appendChild(option);
        });
    }

    // Command Management
    async loadCommands() {
        try {
            this.showLoading(true);
            const response = await fetch('http://localhost:5001/api/commands');
            const result = await response.json();
            
            if (result.success) {
                this.commands = result.data;
                this.renderCommands();
                this.updateCommandSelects();
                this.updateStatusBar();
            } else {
                this.showToast('Greška pri učitavanju komandi: ' + result.error, 'error');
            }
        } catch (error) {
            this.showToast('Greška pri komunikaciji sa serverom', 'error');
            console.error('Greška:', error);
            
            // Fallback - dodaj test komande
            this.commands = [
                { id: 1, name: 'Start Recording', value: 100 },
                { id: 2, name: 'Stop Recording', value: 101 },
                { id: 3, name: 'Play/Pause', value: 102 }
            ];
            this.renderCommands();
            this.updateCommandSelects();
            this.updateStatusBar();
        } finally {
            this.showLoading(false);
        }
    }

    renderCommands() {
        console.log('🎨 Rendering commands:', this.commands);
        const container = document.getElementById('commandsList');
        
        if (this.commands.length === 0) {
            console.log('📭 No commands to render');
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-list"></i>
                    <h3>Nema komandi</h3>
                    <p>Dodajte prvu komandu da biste počeli</p>
                    <button class="btn btn-primary" onclick="app.showCommandModal()">
                        <i class="fas fa-plus"></i> Dodaj komandu
                    </button>
                </div>
            `;
            return;
        }

        console.log('📝 Rendering', this.commands.length, 'commands');
        container.innerHTML = this.commands.map(command => `
            <div class="command-item">
                <div class="command-name">${this.escapeHtml(command.name)}</div>
                <div class="command-value">${command.value}</div>
                <div class="command-actions">
                    <button class="btn btn-small btn-secondary" onclick="app.editCommand(${command.id})">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-small btn-danger" onclick="app.deleteCommand(${command.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `).join('');
    }

    updateCommandSelects() {
        for (let i = 1; i <= 6; i++) {
            const select = document.getElementById(`buttonSelect${i}`);
            const currentValue = select.value;
            
            select.innerHTML = '<option value="">Izaberite komandu...</option>';
            
            this.commands.forEach(command => {
                const option = document.createElement('option');
                option.value = command.id;
                option.textContent = `${command.name} (${command.value})`;
                select.appendChild(option);
            });
            
            // Vrati prethodnu vrednost ako postoji
            if (currentValue) {
                select.value = currentValue;
            }
        }
    }

    showCommandModal(commandId = null) {
        this.currentEditingCommand = commandId;
        const modal = document.getElementById('commandModal');
        const title = document.getElementById('commandModalTitle');
        
        if (commandId) {
            const command = this.commands.find(c => c.id === commandId);
            title.textContent = 'Uredi komandu';
            document.getElementById('commandName').value = command.name;
            document.getElementById('commandValue').value = command.value;
        } else {
            title.textContent = 'Dodaj komandu';
            document.getElementById('commandForm').reset();
        }
        
        modal.style.display = 'flex';
        document.getElementById('commandName').focus();
    }

    async saveCommand() {
        const form = document.getElementById('commandForm');
        const formData = new FormData(form);
        
        const commandData = {
            name: formData.get('name').trim(),
            value: parseInt(formData.get('value'))
        };

        if (!commandData.name) {
            this.showToast('Naziv komande je obavezan', 'error');
            return;
        }

        if (isNaN(commandData.value) || commandData.value < 0 || commandData.value > 65535) {
            this.showToast('Vrednost mora biti broj između 0 i 65535', 'error');
            return;
        }

        try {
            this.showLoading(true);
            
            const url = this.currentEditingCommand 
                ? `http://localhost:5001/api/commands/${this.currentEditingCommand}`
                : 'http://localhost:5001/api/commands';
            const method = this.currentEditingCommand ? 'PUT' : 'POST';

            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(commandData)
            });

            const result = await response.json();

            if (result.success) {
                console.log('✅ Command saved successfully:', result);
                this.showToast(
                    this.currentEditingCommand ? 'Komanda je ažurirana' : 'Komanda je dodana',
                    'success'
                );
                this.closeModal(document.getElementById('commandModal'));
                console.log('🔄 Reloading commands after save...');
                this.loadCommands();
            } else {
                console.error('❌ Error saving command:', result.error);
                this.showToast('Greška pri čuvanju komande: ' + result.error, 'error');
            }
        } catch (error) {
            this.showToast('Greška pri komunikaciji sa serverom', 'error');
            console.error('Greška:', error);
        } finally {
            this.showLoading(false);
        }
    }

    editCommand(commandId) {
        this.showCommandModal(commandId);
    }

    async deleteCommand(commandId) {
        const command = this.commands.find(c => c.id === commandId);
        if (!confirm(`Da li ste sigurni da želite da obrišete komandu "${command.name}"?`)) {
            return;
        }

        try {
            this.showLoading(true);
            const response = await fetch(`http://localhost:5001/api/commands/${commandId}`, {
                method: 'DELETE'
            });

            const result = await response.json();

            if (result.success) {
                this.showToast('Komanda je obrisana', 'success');
                this.loadCommands();
                
                // Ukloni iz mapiranja dugmića
                Object.keys(this.buttonMappings).forEach(button => {
                    if (this.buttonMappings[button] === commandId) {
                        this.updateButtonMapping(button, '');
                    }
                });
            } else {
                this.showToast('Greška pri brisanju komande: ' + result.error, 'error');
            }
        } catch (error) {
            this.showToast('Greška pri komunikaciji sa serverom', 'error');
            console.error('Greška:', error);
        } finally {
            this.showLoading(false);
        }
    }

    // Button Mapping Management
    async loadButtonMappings() {
        try {
            const response = await fetch('http://localhost:5001/api/button-mappings');
            const result = await response.json();
            
            if (result.success) {
                this.buttonMappings = result.data || {};
                this.renderButtonMappings();
            } else {
                this.showToast('Greška pri učitavanju mapiranja: ' + result.error, 'error');
            }
        } catch (error) {
            console.error('Greška pri učitavanju mapiranja:', error);
            // Ne prikazuj grešku korisniku, možda backend još nije implementiran
        }
    }

    renderButtonMappings() {
        for (let i = 1; i <= 6; i++) {
            const commandId = this.buttonMappings[i];
            const select = document.getElementById(`buttonSelect${i}`);
            const label = document.getElementById(`buttonLabel${i}`);
            
            if (commandId && select) {
                select.value = commandId;
                const command = this.commands.find(c => c.id == commandId);
                if (command) {
                    label.textContent = command.name;
                } else {
                    label.textContent = 'Nepoznata komanda';
                }
            } else {
                if (select) select.value = '';
                if (label) label.textContent = 'Nije mapiran';
            }
        }
        this.updateStatusBar();
    }

    updateButtonMapping(buttonNumber, commandId) {
        if (commandId) {
            this.buttonMappings[buttonNumber] = parseInt(commandId);
            const command = this.commands.find(c => c.id == commandId);
            if (command) {
                document.getElementById(`buttonLabel${buttonNumber}`).textContent = command.name;
            }
        } else {
            delete this.buttonMappings[buttonNumber];
            document.getElementById(`buttonLabel${buttonNumber}`).textContent = 'Nije mapiran';
        }
        
        this.updateStatusBar();
        this.updateConfigureButton();
        
        // Sačuvaj mappings na backend
        this.saveButtonMappings();
    }

    async saveButtonMappings() {
        try {
            const response = await fetch('http://localhost:5001/api/button-mappings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(this.buttonMappings)
            });

            const result = await response.json();
            
            if (!result.success) {
                console.error('Greška pri čuvanju mapiranja:', result.error);
            }
        } catch (error) {
            console.error('Greška pri komunikaciji sa serverom:', error);
        }
    }

    // Configuration Management
    updateConfigureButton() {
        const btn = document.getElementById('configureBtn');
        const hasPort = this.selectedUSBPort;
        const hasMappings = Object.keys(this.buttonMappings).length > 0;
        
        btn.disabled = !hasPort || !hasMappings;
    }

    async sendConfiguration() {
        if (!this.selectedUSBPort) {
            this.showToast('Morate izabrati USB port', 'warning');
            return;
        }

        if (Object.keys(this.buttonMappings).length === 0) {
            this.showToast('Morate mapirati barem jedan taster', 'warning');
            return;
        }

        const configData = {
            usbPort: this.selectedUSBPort
        };

        try {
            this.showLoading(true);
            this.showToast('Slanje konfiguracije na uređaj...', 'info');
            
            const response = await fetch('http://localhost:5001/api/configuration', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(configData)
            });

            const result = await response.json();

            if (result.success) {
                let message = result.message || 'Konfiguracija je uspješno poslana na uređaj!';
                
                // Dodaj informaciju o odgovoru uređaja ako postoji
                if (result.data && result.data.device_response) {
                    message += ` Odgovor uređaja: ${result.data.device_response}`;
                }
                
                this.showToast(message, 'success');
                this.updateConnectionStatus(true);
                
                // Log detalje konfiguracije
                console.log('Konfiguracija poslana:', result.data);
            } else {
                this.showToast('Greška pri slanju konfiguracije: ' + result.error, 'error');
                this.updateConnectionStatus(false);
            }
        } catch (error) {
            this.showToast('Greška pri komunikaciji sa serverom', 'error');
            this.updateConnectionStatus(false);
            console.error('Greška:', error);
        } finally {
            this.showLoading(false);
        }
    }

    // UI Helper Methods
    updateStatusBar() {
        const mappedCount = Object.keys(this.buttonMappings).length;
        document.getElementById('commandCount').innerHTML = `Komande: ${this.commands.length}`;
        document.getElementById('mappedButtons').innerHTML = `Mapirano: ${mappedCount}/6`;
    }

    updateConnectionStatus(connected) {
        const statusElement = document.getElementById('connectionStatus');
        if (connected) {
            statusElement.innerHTML = '<i class="fas fa-circle text-success"></i> Povezano';
        } else {
            statusElement.innerHTML = '<i class="fas fa-circle text-danger"></i> Nije povezano';
        }
    }

    closeModal(modal) {
        modal.style.display = 'none';
        modal.querySelectorAll('form').forEach(form => form.reset());
        this.currentEditingCommand = null;
    }

    showLoading(show) {
        document.getElementById('loadingOverlay').style.display = show ? 'flex' : 'none';
    }

    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <i class="fas fa-${this.getToastIcon(type)}"></i>
                <span>${this.escapeHtml(message)}</span>
            </div>
        `;

        document.getElementById('toastContainer').appendChild(toast);

        // Auto remove after 5 seconds
        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease forwards';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }, 5000);
    }

    getToastIcon(type) {
        switch (type) {
            case 'success': return 'check-circle';
            case 'error': return 'exclamation-circle';
            case 'warning': return 'exclamation-triangle';
            default: return 'info-circle';
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize application
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new MIDIConfiguratorApp();
});

// Global functions for inline event handlers
window.app = app;
