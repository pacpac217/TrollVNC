// Configuration
const API_BASE = window.location.origin.replace(/:\d+$/, ':3000');
const WS_BASE = window.location.origin.replace(/:\d+$/, ':8080');

// State
let devices = [];
let currentViewer = null;
let viewerWS = null;
let autoRefreshInterval = null;
let refreshInterval = 5000; // 5 seconds

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupNavigation();
    setupSettings();
    loadDevices();
    startAutoRefresh();
});

// Navigation
function setupNavigation() {
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const page = item.dataset.page;
            switchPage(page);
            
            // Update active state
            document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');
        });
    });
}

function switchPage(page) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.getElementById(`${page}-page`).classList.add('active');
    
    if (page === 'devices') {
        renderDevicesTable();
    }
}

// Settings
function setupSettings() {
    const autoRefreshCheckbox = document.getElementById('autoRefresh');
    const refreshIntervalInput = document.getElementById('refreshInterval');
    
    // Load saved settings
    const savedAutoRefresh = localStorage.getItem('autoRefresh') !== 'false';
    const savedInterval = parseInt(localStorage.getItem('refreshInterval')) || 5;
    
    autoRefreshCheckbox.checked = savedAutoRefresh;
    refreshIntervalInput.value = savedInterval;
    refreshInterval = savedInterval * 1000;
    
    autoRefreshCheckbox.addEventListener('change', (e) => {
        localStorage.setItem('autoRefresh', e.target.checked);
        if (e.target.checked) {
            startAutoRefresh();
        } else {
            stopAutoRefresh();
        }
    });
    
    refreshIntervalInput.addEventListener('change', (e) => {
        const interval = parseInt(e.target.value) || 5;
        localStorage.setItem('refreshInterval', interval);
        refreshInterval = interval * 1000;
        if (autoRefreshCheckbox.checked) {
            stopAutoRefresh();
            startAutoRefresh();
        }
    });
}

function startAutoRefresh() {
    if (autoRefreshInterval) return;
    autoRefreshInterval = setInterval(loadDevices, refreshInterval);
}

function stopAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
        autoRefreshInterval = null;
    }
}

// Load devices
async function loadDevices() {
    try {
        const response = await fetch(`${API_BASE}/api/devices`);
        const data = await response.json();
        devices = data.devices || [];
        updateStats();
        renderDevices();
        renderDevicesTable();
    } catch (error) {
        console.error('Failed to load devices:', error);
    }
}

function refreshDevices() {
    loadDevices();
}

// Update statistics
function updateStats() {
    const total = devices.length;
    const connected = devices.filter(d => d.isConnected).length;
    const totalClients = devices.reduce((sum, d) => sum + d.clientCount, 0);
    const totalReconnects = devices.reduce((sum, d) => sum + (d.reconnectCount || 0), 0);
    
    document.getElementById('totalDevices').textContent = total;
    document.getElementById('connectedDevices').textContent = connected;
    document.getElementById('totalClients').textContent = totalClients;
    document.getElementById('totalReconnects').textContent = totalReconnects;
    document.getElementById('deviceCount').textContent = total;
}

// Render devices grid
function renderDevices() {
    const grid = document.getElementById('devicesGrid');
    
    if (devices.length === 0) {
        grid.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-mobile-alt"></i>
                <p>No devices connected</p>
                <small>Waiting for iPhone connections...</small>
            </div>
        `;
        return;
    }
    
    grid.innerHTML = devices
        .filter(d => d.isConnected)
        .map(device => `
            <div class="device-card" onclick="openViewer('${device.deviceId}')">
                <div class="device-card-header">
                    <div class="device-id">${device.deviceId}</div>
                    <div class="device-status connected">
                        <span class="status-indicator online"></span>
                        Connected
                    </div>
                </div>
                <div class="device-info">
                    <div class="device-info-item">
                        <span>IP Address:</span>
                        <span>${device.remoteAddress || 'N/A'}</span>
                    </div>
                    <div class="device-info-item">
                        <span>Connected:</span>
                        <span>${formatTime(device.connectedAt)}</span>
                    </div>
                    <div class="device-info-item">
                        <span>Viewers:</span>
                        <span>${device.clientCount}</span>
                    </div>
                    ${device.reconnectCount > 0 ? `
                    <div class="device-info-item">
                        <span>Reconnects:</span>
                        <span>${device.reconnectCount}</span>
                    </div>
                    ` : ''}
                </div>
                <div class="device-actions">
                    <button class="btn btn-primary" onclick="event.stopPropagation(); openViewer('${device.deviceId}')">
                        <i class="fas fa-eye"></i> View
                    </button>
                </div>
            </div>
        `).join('');
}

// Render devices table
function renderDevicesTable() {
    const tbody = document.getElementById('devicesTableBody');
    const searchTerm = document.getElementById('searchInput')?.value.toLowerCase() || '';
    
    const filteredDevices = devices.filter(d => 
        d.deviceId.toLowerCase().includes(searchTerm) ||
        (d.remoteAddress && d.remoteAddress.includes(searchTerm))
    );
    
    if (filteredDevices.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" class="empty-row">
                    <div class="empty-state">
                        <i class="fas fa-mobile-alt"></i>
                        <p>No devices found</p>
                    </div>
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = filteredDevices.map(device => `
        <tr>
            <td><strong>${device.deviceId}</strong></td>
            <td>
                <div class="device-status ${device.isConnected ? 'connected' : 'disconnected'}">
                    <span class="status-indicator ${device.isConnected ? 'online' : ''}"></span>
                    ${device.isConnected ? 'Connected' : 'Disconnected'}
                </div>
            </td>
            <td>${device.remoteAddress || 'N/A'}</td>
            <td>${formatTime(device.connectedAt)}</td>
            <td>${device.lastReconnectAt ? formatTime(device.lastReconnectAt) : 'Never'}</td>
            <td>${device.reconnectCount || 0}</td>
            <td>${device.clientCount || 0}</td>
            <td>
                ${device.isConnected ? `
                    <button class="btn btn-sm btn-primary" onclick="openViewer('${device.deviceId}')">
                        <i class="fas fa-eye"></i> View
                    </button>
                ` : '<span class="text-muted">Offline</span>'}
            </td>
        </tr>
    `).join('');
}

// Search
if (document.getElementById('searchInput')) {
    document.getElementById('searchInput').addEventListener('input', renderDevicesTable);
}

// Format time
function formatTime(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    
    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

// Viewer
function openViewer(deviceId) {
    const device = devices.find(d => d.deviceId === deviceId);
    if (!device || !device.isConnected) {
        alert('Device is not connected');
        return;
    }
    
    currentViewer = deviceId;
    document.getElementById('viewerDeviceName').textContent = `Device: ${deviceId}`;
    document.getElementById('viewerModal').classList.add('active');
    
    connectViewer(deviceId);
}

function closeViewer() {
    document.getElementById('viewerModal').classList.remove('active');
    if (viewerWS) {
        viewerWS.close();
        viewerWS = null;
    }
    currentViewer = null;
    document.getElementById('vncCanvas').style.display = 'none';
    document.getElementById('vncLoading').style.display = 'block';
}

function connectViewer(deviceId) {
    const canvas = document.getElementById('vncCanvas');
    const loading = document.getElementById('vncLoading');
    const statusIndicator = document.getElementById('viewerStatus');
    const statusText = document.getElementById('viewerStatusText');
    
    // Reset
    canvas.style.display = 'none';
    loading.style.display = 'block';
    statusIndicator.className = 'status-indicator';
    statusText.textContent = 'Connecting...';
    
    // Connect WebSocket
    viewerWS = new WebSocket(`${WS_BASE}?deviceId=${deviceId}`);
    
    viewerWS.onopen = () => {
        console.log('Viewer WebSocket connected');
        statusIndicator.classList.add('online');
        statusText.textContent = 'Connected';
        loading.style.display = 'none';
        canvas.style.display = 'block';
        
        // Note: Full VNC protocol implementation requires noVNC library
        // This is a placeholder - you should integrate noVNC here
        initVNCViewer(canvas, viewerWS);
    };
    
    viewerWS.onmessage = (event) => {
        // Handle VNC data
        handleVNCData(event.data);
    };
    
    viewerWS.onerror = (error) => {
        console.error('WebSocket error:', error);
        statusIndicator.classList.remove('online');
        statusText.textContent = 'Connection Error';
    };
    
    viewerWS.onclose = () => {
        console.log('WebSocket closed');
        statusIndicator.classList.remove('online');
        statusText.textContent = 'Disconnected';
        
        // Try to reconnect if viewer is still open
        if (currentViewer === deviceId) {
            setTimeout(() => {
                if (currentViewer === deviceId) {
                    connectViewer(deviceId);
                }
            }, 3000);
        }
    };
}

function initVNCViewer(canvas, ws) {
    // TODO: Integrate noVNC library here
    // Example:
    // const rfb = new RFB(canvas, ws.url);
    // rfb.scaleViewport = true;
    // rfb.resizeSession = false;
    
    console.log('VNC Viewer initialized (noVNC integration needed)');
}

function handleVNCData(data) {
    // TODO: Handle VNC protocol data
    // This requires noVNC or similar library
    console.log('Received VNC data:', data.byteLength, 'bytes');
}

function toggleFullscreen() {
    const canvas = document.getElementById('vncCanvas');
    if (!document.fullscreenElement) {
        canvas.requestFullscreen();
    } else {
        document.exitFullscreen();
    }
}

function sendCtrlAltDel() {
    // TODO: Send Ctrl+Alt+Del to device
    console.log('Sending Ctrl+Alt+Del');
}

// Close modal on escape
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeViewer();
    }
});

