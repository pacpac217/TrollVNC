/**
 * VNC Reverse Connection Proxy Server
 * Nhận reverse connection từ iPhone và proxy đến web client
 * Hỗ trợ 500 devices: Port 10001-10500
 */

const net = require('net');
const WebSocket = require('ws');
const http = require('http');

// Configuration
const VNC_BASE_PORT = 10001; // Device 1 bắt đầu từ port 10001
const MAX_DEVICES = 500; // Tối đa 500 devices (port 10001-10500)
const WEB_WS_PORT = 8080; // WebSocket port cho web client
const HTTP_PORT = 3000; // HTTP server port

// Store active connections: port -> {deviceId, vncSocket, wsClients}
const activeConnections = new Map(); // port -> connection
const devicePortMap = new Map(); // deviceId -> port

// Tạo listeners cho tất cả các port
const vncListeners = new Map(); // port -> server

console.log(`[INFO] Initializing ${MAX_DEVICES} VNC listeners (ports ${VNC_BASE_PORT} to ${VNC_BASE_PORT + MAX_DEVICES - 1})...`);

for (let port = VNC_BASE_PORT; port < VNC_BASE_PORT + MAX_DEVICES; port++) {
    const listener = net.createServer((vncSocket) => {
        const assignedPort = port;
        let deviceId = null;
        let buffer = Buffer.alloc(0);

        console.log(`[VNC:${assignedPort}] New connection from ${vncSocket.remoteAddress}:${vncSocket.remotePort}`);

        vncSocket.on('data', (data) => {
            buffer = Buffer.concat([buffer, data]);

            // Đọc device ID từ 32 bytes đầu
            if (!deviceId && buffer.length >= 32) {
                deviceId = buffer.slice(0, 32).toString('utf8').replace(/\0/g, '').trim();
                console.log(`[VNC:${assignedPort}] Device ID: ${deviceId}`);

                // Check if this device was previously connected on a different port
                const existingPort = devicePortMap.get(deviceId);
                if (existingPort && existingPort !== assignedPort) {
                    console.log(`[VNC:${assignedPort}] Device ${deviceId} moved from port ${existingPort} to ${assignedPort}`);
                    // Close old connection
                    const oldConnection = activeConnections.get(existingPort);
                    if (oldConnection && oldConnection.vncSocket && !oldConnection.vncSocket.destroyed) {
                        oldConnection.vncSocket.destroy();
                    }
                    activeConnections.delete(existingPort);
                }

                // Lưu mapping deviceId -> port
                devicePortMap.set(deviceId, assignedPort);

                // Lưu connection
                const connection = {
                    vncSocket: vncSocket,
                    wsClients: [],
                    deviceId: deviceId,
                    port: assignedPort,
                    connectedAt: new Date(),
                    reconnectCount: 0
                };
                
                activeConnections.set(assignedPort, connection);

                // Forward phần còn lại
                const remainingData = buffer.slice(32);
                if (remainingData.length > 0) {
                    forwardToWebClients(assignedPort, remainingData);
                }
            } else if (deviceId) {
                forwardToWebClients(assignedPort, buffer);
                buffer = Buffer.alloc(0);
            }
        });

        vncSocket.on('error', (err) => {
            console.error(`[VNC:${assignedPort}] Socket error for device ${deviceId}:`, err);
        });

        vncSocket.on('close', () => {
            console.log(`[VNC:${assignedPort}] Connection closed for device ${deviceId}`);
            const connection = activeConnections.get(assignedPort);
            if (connection) {
                connection.wsClients.forEach(ws => {
                    if (ws.readyState === WebSocket.OPEN) {
                        ws.close(1006, 'VNC connection lost - device reconnecting');
                    }
                });
                connection.wsClients = [];
                connection.vncSocket = null;
                // Keep entry for reconnection tracking
            }
        });
    });

    listener.listen(port, () => {
        // Chỉ log khi khởi động để không spam
        if (port === VNC_BASE_PORT || port === VNC_BASE_PORT + MAX_DEVICES - 1 || port % 50 === 0) {
            console.log(`[VNC] Listener started on port ${port}`);
        }
    });

    listener.on('error', (err) => {
        if (err.code === 'EADDRINUSE') {
            console.error(`[ERROR] Port ${port} is already in use!`);
        } else {
            console.error(`[ERROR] Failed to start listener on port ${port}:`, err);
        }
    });

    vncListeners.set(port, listener);
}

console.log(`[INFO] All ${MAX_DEVICES} VNC listeners initialized`);

// Forward VNC data to WebSocket clients
function forwardToWebClients(port, data) {
    const connection = activeConnections.get(port);
    if (!connection) return;

    connection.wsClients.forEach(ws => {
        if (ws.readyState === WebSocket.OPEN) {
            ws.send(data);
        }
    });
}

// WebSocket Server - Kết nối qua deviceId
const wss = new WebSocket.Server({ port: WEB_WS_PORT });

wss.on('connection', (ws, req) => {
    const url = new URL(req.url, `http://${req.headers.host}`);
    const deviceId = url.searchParams.get('deviceId');

    if (!deviceId) {
        console.error('[WS] No deviceId provided');
        ws.close();
        return;
    }

    // Tìm port của device này
    const port = devicePortMap.get(deviceId);
    if (!port) {
        console.error(`[WS] No port found for device: ${deviceId}`);
        ws.close();
        return;
    }

    const connection = activeConnections.get(port);
    if (!connection || !connection.vncSocket || connection.vncSocket.destroyed) {
        console.error(`[WS] No active VNC connection for device: ${deviceId} on port ${port}`);
        ws.close();
        return;
    }

    console.log(`[WS] New web client connected for device: ${deviceId} (port ${port})`);
    connection.wsClients.push(ws);

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

// HTTP Server - API
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
        const devices = Array.from(activeConnections.entries())
            .filter(([port, conn]) => conn.vncSocket && !conn.vncSocket.destroyed)
            .map(([port, conn]) => ({
                deviceId: conn.deviceId,
                port: port,
                connectedAt: conn.connectedAt,
                clientCount: conn.wsClients.length,
                isConnected: true
            }));

        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ devices }));
        return;
    }

    // API: Get device info by deviceId
    if (url.pathname.startsWith('/api/device/') && req.method === 'GET') {
        const deviceId = url.pathname.split('/')[3];
        const port = devicePortMap.get(deviceId);
        
        if (!port) {
            res.writeHead(404, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: 'Device not found' }));
            return;
        }

        const connection = activeConnections.get(port);
        if (!connection || !connection.vncSocket || connection.vncSocket.destroyed) {
            res.writeHead(404, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: 'Device not connected' }));
            return;
        }

        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
            deviceId: deviceId,
            port: port,
            connectedAt: connection.connectedAt,
            clientCount: connection.wsClients.length,
            isConnected: true
        }));
        return;
    }

    res.writeHead(404);
    res.end('Not Found');
});

httpServer.listen(HTTP_PORT, () => {
    console.log(`[HTTP] Server started on port ${HTTP_PORT}`);
    console.log(`[INFO] VNC Listeners: ${VNC_BASE_PORT} to ${VNC_BASE_PORT + MAX_DEVICES - 1} (${MAX_DEVICES} ports)`);
    console.log(`[INFO] WebSocket Server: ${WEB_WS_PORT}`);
    console.log(`[INFO] Device 1 → Port 10001, Device 10 → Port 10010, Device 500 → Port 10500`);
    console.log(`[INFO] Ready to accept connections from iPhones!`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
    console.log('[INFO] Shutting down...');
    vncListeners.forEach(listener => listener.close());
    wss.close();
    httpServer.close();
    process.exit(0);
});
