/**
 * VNC Reverse Connection Proxy Server
 * Nhận reverse connection từ iPhone và proxy đến web client
 */

const net = require('net');
const WebSocket = require('ws');
const http = require('http');

// Configuration
const VNC_LISTENER_PORT = 5500; // Port iPhone sẽ kết nối đến
const WEB_WS_PORT = 8080; // WebSocket port cho web client
const HTTP_PORT = 3000; // HTTP server port

// Store active connections
const activeConnections = new Map(); // deviceId -> {vncSocket, wsClients: []}
const deviceRegistry = new Map(); // deviceId -> deviceInfo

// VNC Listener - Nhận kết nối từ iPhone
const vncListener = net.createServer((vncSocket) => {
    let deviceId = null;
    let buffer = Buffer.alloc(0);

    console.log(`[VNC] New connection from ${vncSocket.remoteAddress}:${vncSocket.remotePort}`);

    // Nhận device ID từ iPhone (gửi trong 32 bytes đầu)
    vncSocket.on('data', (data) => {
        buffer = Buffer.concat([buffer, data]);

        // Đọc device ID từ 32 bytes đầu (nếu chưa có)
        if (!deviceId && buffer.length >= 32) {
            deviceId = buffer.slice(0, 32).toString('utf8').replace(/\0/g, '').trim();
            console.log(`[VNC] Device ID: ${deviceId} from ${vncSocket.remoteAddress}:${vncSocket.remotePort}`);

            // Check if this device was previously connected (reconnection after IP change)
            const existingConnection = activeConnections.get(deviceId);
            if (existingConnection && existingConnection.vncSocket) {
                console.log(`[VNC] Device ${deviceId} reconnected (IP may have changed)`);
                // Close old connection
                if (!existingConnection.vncSocket.destroyed) {
                    existingConnection.vncSocket.destroy();
                }
            }

            // Lưu connection (hoặc update nếu reconnect)
            const connection = existingConnection || {
                vncSocket: vncSocket,
                wsClients: [],
                deviceId: deviceId,
                connectedAt: new Date(),
                reconnectCount: 0
            };
            
            // Update connection info
            connection.vncSocket = vncSocket;
            if (existingConnection) {
                connection.reconnectCount = (connection.reconnectCount || 0) + 1;
                connection.lastReconnectAt = new Date();
                console.log(`[VNC] Device ${deviceId} reconnected ${connection.reconnectCount} time(s)`);
            }
            
            activeConnections.set(deviceId, connection);

            // Forward phần còn lại của buffer đến WebSocket clients
            const remainingData = buffer.slice(32);
            if (remainingData.length > 0) {
                forwardToWebClients(deviceId, remainingData);
            }
        } else if (deviceId) {
            // Forward data đến WebSocket clients
            forwardToWebClients(deviceId, buffer);
            buffer = Buffer.alloc(0);
        }
    });

    vncSocket.on('error', (err) => {
        console.error(`[VNC] Socket error for device ${deviceId}:`, err);
    });

    vncSocket.on('close', () => {
        console.log(`[VNC] Connection closed for device ${deviceId} (IP may have changed, will reconnect automatically)`);
        if (deviceId) {
            const connection = activeConnections.get(deviceId);
            if (connection) {
                // Notify all WebSocket clients that connection is lost
                // But keep the entry so device can reconnect with same ID
                connection.wsClients.forEach(ws => {
                    if (ws.readyState === WebSocket.OPEN) {
                        // Send close frame to notify client
                        ws.close(1006, 'VNC connection lost - device reconnecting');
                    }
                });
                // Clear WebSocket clients but keep entry for reconnection
                connection.wsClients = [];
                connection.vncSocket = null;
                // Don't delete - device will reconnect with same ID
                // activeConnections.delete(deviceId);
            }
        }
    });
});

vncListener.listen(VNC_LISTENER_PORT, () => {
    console.log(`[VNC] Listener started on port ${VNC_LISTENER_PORT}`);
});

// Forward VNC data to WebSocket clients
function forwardToWebClients(deviceId, data) {
    const connection = activeConnections.get(deviceId);
    if (!connection) return;

    connection.wsClients.forEach(ws => {
        if (ws.readyState === WebSocket.OPEN) {
            ws.send(data);
        }
    });
}

// WebSocket Server for Web Clients
const wss = new WebSocket.Server({ port: WEB_WS_PORT });

wss.on('connection', (ws, req) => {
    const url = new URL(req.url, `http://${req.headers.host}`);
    const deviceId = url.searchParams.get('deviceId');

    if (!deviceId) {
        console.error('[WS] No deviceId provided');
        ws.close();
        return;
    }

    console.log(`[WS] New web client connected for device: ${deviceId}`);

    const connection = activeConnections.get(deviceId);
    if (!connection) {
        console.error(`[WS] No active VNC connection for device: ${deviceId}`);
        ws.close();
        return;
    }

    // Add WebSocket to connection
    connection.wsClients.push(ws);

    // Forward WebSocket data to VNC socket
    ws.on('message', (data) => {
        if (connection.vncSocket && !connection.vncSocket.destroyed) {
            connection.vncSocket.write(data);
        }
    });

    ws.on('close', () => {
        console.log(`[WS] Web client disconnected for device: ${deviceId}`);
        const index = connection.wsClients.indexOf(ws);
        if (index > -1) {
            connection.wsClients.splice(index, 1);
        }
    });

    ws.on('error', (err) => {
        console.error(`[WS] Error for device ${deviceId}:`, err);
    });
});

// HTTP Server - API và Web Interface
const httpServer = http.createServer((req, res) => {
    const url = new URL(req.url, `http://${req.headers.host}`);

    // CORS headers
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    if (req.method === 'OPTIONS') {
        res.writeHead(200);
        res.end();
        return;
    }

    // API: Get list of active devices
    if (url.pathname === '/api/devices' && req.method === 'GET') {
        const devices = Array.from(activeConnections.entries()).map(([deviceId, conn]) => ({
            deviceId: deviceId,
            connectedAt: conn.connectedAt,
            lastReconnectAt: conn.lastReconnectAt || null,
            reconnectCount: conn.reconnectCount || 0,
            clientCount: conn.wsClients.length,
            isConnected: conn.vncSocket && !conn.vncSocket.destroyed,
            remoteAddress: conn.vncSocket ? conn.vncSocket.remoteAddress : null
        }));

        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ devices }));
        return;
    }

    // API: Get device info
    if (url.pathname.startsWith('/api/device/') && req.method === 'GET') {
        const deviceId = url.pathname.split('/')[3];
        const connection = activeConnections.get(deviceId);

        if (!connection) {
            res.writeHead(404, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: 'Device not found' }));
            return;
        }

        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
            deviceId: deviceId,
            connectedAt: connection.connectedAt,
            clientCount: connection.wsClients.length,
            isConnected: !connection.vncSocket.destroyed
        }));
        return;
    }

    // WebSocket endpoint info
    if (url.pathname === '/api/ws-info' && req.method === 'GET') {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
            wsUrl: `ws://${req.headers.host.replace(/:\d+$/, ':' + WEB_WS_PORT)}`,
            vncPort: VNC_LISTENER_PORT
        }));
        return;
    }

    // Serve static files
    if (url.pathname === '/' || url.pathname === '/index.html') {
        const fs = require('fs');
        const path = require('path');
        const filePath = path.join(__dirname, 'public', 'index.html');
        if (fs.existsSync(filePath)) {
            res.writeHead(200, { 'Content-Type': 'text/html' });
            res.end(fs.readFileSync(filePath));
            return;
        }
    }
    
    // Serve other static files (CSS, JS, etc.)
    if (url.pathname.startsWith('/')) {
        const fs = require('fs');
        const path = require('path');
        const filePath = path.join(__dirname, 'public', url.pathname);
        if (fs.existsSync(filePath) && fs.statSync(filePath).isFile()) {
            const ext = path.extname(filePath);
            const contentTypes = {
                '.html': 'text/html',
                '.css': 'text/css',
                '.js': 'application/javascript',
                '.json': 'application/json',
                '.png': 'image/png',
                '.jpg': 'image/jpeg',
                '.svg': 'image/svg+xml'
            };
            res.writeHead(200, { 'Content-Type': contentTypes[ext] || 'application/octet-stream' });
            res.end(fs.readFileSync(filePath));
            return;
        }
    }
    
    res.writeHead(404);
    res.end('Not Found');
});

httpServer.listen(HTTP_PORT, () => {
    console.log(`[HTTP] Server started on port ${HTTP_PORT}`);
    console.log(`[INFO] VNC Listener: ${VNC_LISTENER_PORT}`);
    console.log(`[INFO] WebSocket Server: ${WEB_WS_PORT}`);
    console.log(`[INFO] Ready to accept connections from iPhones!`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
    console.log('[INFO] Shutting down...');
    vncListener.close();
    wss.close();
    httpServer.close();
    process.exit(0);
});

