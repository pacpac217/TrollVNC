from flask import Flask, Response, send_file, request, jsonify
import os
from datetime import datetime, timezone
from werkzeug.utils import secure_filename

app = Flask(__name__)

# ==============================================================================
# CHẶN CACHE TRÌNH DUYỆT
# ==============================================================================
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = (
        'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    )
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response


# ==============================================================================
# CẤU HÌNH THƯ MỤC
# ==============================================================================
ROOT_FOLDER = "."
SNAPSHOT_ROOT = os.path.join(ROOT_FOLDER, "_snapshots")
os.makedirs(SNAPSHOT_ROOT, exist_ok=True)

TEXT_EXTENSIONS = {
    ".txt", ".js", ".json", ".md", ".py", ".html", ".css", ".xml", ".log"
}
MEDIA_EXTENSIONS = {
    ".mp4", ".avi", ".mov", ".mkv",
    ".jpg", ".jpeg", ".png", ".gif", ".webp",
    ".mp3", ".wav", ".pdf"
}

# Thiết bị nào gửi ảnh trong vòng N giây gần nhất → coi như "ĐANG BẬT"
ONLINE_THRESHOLD_SECONDS = 20


# ==============================================================================
# 1) API CHO IPHONE UPLOAD ẢNH MÀN HÌNH
# ==============================================================================

@app.route("/snapshot/<device_id>", methods=["POST"])
def upload_snapshot(device_id):
    """
    iPhone gửi:
      POST /snapshot/MAY01
        form-data:
          image = file .jpg/.png
    """
    try:
        if "image" not in request.files:
            return "Thiếu field 'image' trong form-data", 400

        img_file = request.files["image"]
        if img_file.filename == "":
            return "Tên file trống", 400

        device_safe = secure_filename(device_id)
        device_folder = os.path.join(SNAPSHOT_ROOT, device_safe)
        os.makedirs(device_folder, exist_ok=True)

        _, ext = os.path.splitext(img_file.filename)
        ext = (ext or ".jpg").lower()
        if ext not in {".jpg", ".jpeg", ".png"}:
            ext = ".jpg"

        latest_path = os.path.join(device_folder, "latest" + ext)
        img_file.save(latest_path)

        ts_path = os.path.join(device_folder, "latest_ts.txt")
        with open(ts_path, "w", encoding="utf-8") as f:
            f.write(datetime.now(timezone.utc).isoformat())

        return "OK", 200
    except Exception as e:
        return f"Lỗi upload snapshot: {str(e)}", 500


@app.route("/snapshot/latest/<device_id>")
def get_latest_snapshot(device_id):
    """
    Trả về ảnh mới nhất của device_id
    """
    device_safe = secure_filename(device_id)
    device_folder = os.path.join(SNAPSHOT_ROOT, device_safe)
    if not os.path.isdir(device_folder):
        return "Chưa có snapshot cho device này", 404

    for ext, mime in [(".jpg", "image/jpeg"), (".jpeg", "image/jpeg"), (".png", "image/png")]:
        p = os.path.join(device_folder, "latest" + ext)
        if os.path.isfile(p):
            return send_file(p, mimetype=mime)

    return "Không tìm thấy ảnh latest", 404


def get_device_info(device_id: str):
    device_safe = secure_filename(device_id)
    device_folder = os.path.join(SNAPSHOT_ROOT, device_safe)

    last_ts = None
    last_ts_str = None
    age_sec = None

    ts_path = os.path.join(device_folder, "latest_ts.txt")
    if os.path.isfile(ts_path):
        try:
            with open(ts_path, "r", encoding="utf-8") as f:
                ts_raw = f.read().strip()
            last_ts = datetime.fromisoformat(ts_raw)
        except Exception:
            last_ts = None

    if last_ts is None:
        # fallback: lấy theo mtime của file ảnh
        for ext in [".jpg", ".jpeg", ".png"]:
            p = os.path.join(device_folder, "latest" + ext)
            if os.path.isfile(p):
                try:
                    mtime = os.path.getmtime(p)
                    last_ts = datetime.fromtimestamp(mtime, tz=timezone.utc)
                except Exception:
                    pass
                break

    if last_ts is not None:
        if last_ts.tzinfo is None:
            last_ts = last_ts.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        age_sec = (now - last_ts).total_seconds()
        last_ts_str = last_ts.isoformat().replace("+00:00", "Z")

    online = age_sec is not None and age_sec <= ONLINE_THRESHOLD_SECONDS

    return {
        "id": device_id,
        "last_ts": last_ts_str,
        "age_sec": age_sec,
        "online": online,
    }


@app.route("/api/devices")
def api_devices():
    """
    Trả về JSON danh sách devices + trạng thái bật/tắt
    Tích hợp với VNC devices từ proxy server
    """
    devices = []
    if os.path.isdir(SNAPSHOT_ROOT):
        for name in os.listdir(SNAPSHOT_ROOT):
            p = os.path.join(SNAPSHOT_ROOT, name)
            if os.path.isdir(p):
                device_info = get_device_info(name)
                # TODO: Có thể check VNC connection status từ proxy server
                # import requests
                # try:
                #     vnc_status = requests.get(f'http://localhost:3000/api/device/{name}', timeout=1)
                #     if vnc_status.status_code == 200:
                #         device_info['vnc_connected'] = True
                # except:
                #     device_info['vnc_connected'] = False
                devices.append(device_info)
    devices.sort(key=lambda d: d["id"])
    return jsonify(devices)


# ==============================================================================
# 2) DASHBOARD / MONITOR TOÀN BỘ PHONE
# ==============================================================================

@app.route("/monitor")
def monitor():
    """
    Giao diện hiển thị toàn bộ thiết bị:
      - grid nhiều phone
      - sắp xếp: theo ID, theo đang bật/tắt
      - chỉnh số cột / kích thước thumbnail
      - bật/tắt refresh toàn bộ / từng phone
      - click 1 phone để phóng to toàn màn
    """
    html = """
    <!doctype html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Monitor Devices</title>
        <style>
            :root {
                --columns: 5;
                --thumb-height: 220px;
            }
            * { box-sizing: border-box; }
            body {
                margin: 0;
                background: #111;
                color: #eee;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            }
            .toolbar {
                position: sticky;
                top: 0;
                z-index: 10;
                background: #181818;
                padding: 8px 12px;
                display: flex;
                flex-wrap: wrap;
                align-items: center;
                gap: 8px 16px;
                border-bottom: 1px solid #333;
            }
            .toolbar .group {
                display: flex;
                flex-wrap: wrap;
                align-items: center;
                gap: 6px;
                font-size: 13px;
            }
            .toolbar button {
                padding: 4px 8px;
                background: #2c3e50;
                border: 1px solid #34495e;
                color: #ecf0f1;
                border-radius: 4px;
                cursor: pointer;
                font-size: 12px;
            }
            .toolbar button.active {
                background: #27ae60;
                border-color: #2ecc71;
            }
            .toolbar input[type="number"],
            .toolbar input[type="range"] {
                accent-color: #27ae60;
            }
            .toolbar label {
                opacity: 0.8;
            }
            #deviceGrid {
                display: grid;
                grid-template-columns: repeat(var(--columns), minmax(0, 1fr));
                gap: 8px;
                padding: 8px;
            }
            .device-card {
                background: #222;
                border-radius: 8px;
                box-shadow: 0 0 12px rgba(0,0,0,0.6);
                padding: 6px;
                display: flex;
                flex-direction: column;
                cursor: pointer;
                transition: transform 0.15s ease, box-shadow 0.15s ease, opacity 0.15s ease;
            }
            .device-card.online {
                border: 1px solid #2ecc71;
            }
            .device-card.offline {
                border: 1px solid #555;
                opacity: 0.4;
            }
            .device-card.paused {
                outline: 1px dashed #f1c40f;
            }
            .device-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 0 18px rgba(0,0,0,0.9);
            }
            .card-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 4px;
                font-size: 12px;
            }
            .card-header .name {
                font-weight: 600;
            }
            .card-header .status {
                font-size: 11px;
                opacity: 0.85;
            }
            .img-wrap {
                background: #000;
                border-radius: 4px;
                overflow: hidden;
            }
            .img-wrap img {
                width: 100%;
                height: auto;
                max-height: var(--thumb-height);
                object-fit: contain;
                display: block;
                background: #000;
            }
            .card-footer {
                margin-top: 4px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                font-size: 11px;
            }
            .card-footer button {
                padding: 2px 6px;
                font-size: 11px;
                background: #2c3e50;
                border: 1px solid #34495e;
                color: #ecf0f1;
                border-radius: 4px;
                cursor: pointer;
            }
            .card-footer button:hover {
                background: #34495e;
            }
            .card-footer .vnc-btn {
                background: #3498db;
                border-color: #2980b9;
            }
            .card-footer .vnc-btn:hover {
                background: #2980b9;
            }
            .card-footer .time {
                opacity: 0.7;
                font-family: monospace;
            }
            /* VNC Modal */
            .vnc-modal {
                display: none;
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0,0,0,0.95);
                z-index: 10000;
                flex-direction: column;
            }
            .vnc-modal.active {
                display: flex;
            }
            .vnc-header {
                padding: 12px 16px;
                background: #181818;
                border-bottom: 1px solid #333;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .vnc-header h3 {
                margin: 0;
                font-size: 16px;
                font-weight: 600;
            }
            .vnc-close-btn {
                background: #e74c3c;
                border: 1px solid #c0392b;
                color: #fff;
                padding: 6px 16px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 13px;
                font-weight: 600;
            }
            .vnc-close-btn:hover {
                background: #c0392b;
            }
            .vnc-container {
                flex: 1;
                display: flex;
                flex-direction: column;
                overflow: hidden;
            }
            .vnc-toolbar {
                padding: 8px 16px;
                background: #181818;
                border-bottom: 1px solid #333;
                display: flex;
                gap: 8px;
                align-items: center;
            }
            .vnc-screen {
                flex: 1;
                background: #000;
                display: flex;
                align-items: center;
                justify-content: center;
                position: relative;
                overflow: auto;
            }
            .vnc-screen canvas {
                max-width: 100%;
                max-height: 100%;
            }
            .vnc-loading {
                position: absolute;
                color: #eee;
                text-align: center;
            }
            .vnc-spinner {
                width: 40px;
                height: 40px;
                border: 3px solid #333;
                border-top-color: #27ae60;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin: 0 auto 16px;
            }
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
            .vnc-status {
                margin-left: auto;
                display: flex;
                align-items: center;
                gap: 8px;
                font-size: 12px;
            }
            .status-dot {
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: #555;
            }
            .status-dot.connected {
                background: #27ae60;
                box-shadow: 0 0 8px #27ae60;
            }
            /* Khi phóng to 1 phone */
            .device-card.expanded {
                position: fixed;
                inset: 8px;
                margin: 0;
                z-index: 9999;
                max-width: none;
                max-height: none;
                border-radius: 8px;
                background: #000;
                box-shadow: 0 0 0 9999px rgba(0,0,0,0.85);
            }
            .device-card.expanded .img-wrap img {
                max-height: none;
                height: calc(100vh - 64px);
                object-fit: contain;
            }
            .device-card.expanded .card-footer,
            .device-card.expanded .card-header {
                padding: 0 4px;
            }
            .device-card.expanded .card-header {
                font-size: 14px;
            }
            .info-line {
                font-size: 12px;
                opacity: 0.9;
            }
        </style>
    </head>
    <body>
        <div class="toolbar">
            <div class="group">
                <span class="info-line">📱 Tổng: <span id="deviceCount">0</span></span>
                <span class="info-line">🟢 Bật: <span id="onlineCount">0</span></span>
            </div>
            <div class="group">
                <label>Sắp xếp:</label>
                <button id="sortIdBtn" class="active">Theo số (ID)</button>
                <button id="sortOnlineBtn">Bật trước</button>
                <button id="sortOfflineBtn">Tắt trước</button>
            </div>
            <div class="group">
                <label for="columnsInput">Số phone / hàng:</label>
                <input id="columnsInput" type="number" min="1" max="12" value="5" style="width:60px;">
            </div>
            <div class="group">
                <label for="sizeInput">Kích thước:</label>
                <input id="sizeInput" type="range" min="120" max="400" value="220">
            </div>
            <div class="group">
                <label>Refresh:</label>
                <button id="startAllBtn" class="active">Bật toàn bộ</button>
                <button id="stopAllBtn">Tắt toàn bộ</button>
            </div>
        </div>

        <div id="deviceGrid"></div>

        <!-- VNC Viewer Modal -->
        <div class="vnc-modal" id="vncModal">
            <div class="vnc-header">
                <h3 id="vncDeviceName">📺 VNC Viewer</h3>
                <button class="vnc-close-btn" onclick="closeVNCViewer()">✕ Đóng</button>
            </div>
            <div class="vnc-container">
                <div class="vnc-toolbar">
                    <button onclick="toggleVNCFullscreen()" style="padding: 4px 8px; background: #2c3e50; border: 1px solid #34495e; color: #ecf0f1; border-radius: 4px; cursor: pointer; font-size: 12px;">⛶ Fullscreen</button>
                    <button onclick="reconnectVNC()" style="padding: 4px 8px; background: #27ae60; border: 1px solid #229954; color: #ecf0f1; border-radius: 4px; cursor: pointer; font-size: 12px;">🔄 Kết nối lại</button>
                    <div class="vnc-status">
                        <div class="status-dot" id="vncStatusDot"></div>
                        <span id="vncStatusText">Đang kết nối...</span>
                    </div>
                </div>
                <div class="vnc-screen" id="vncScreen">
                    <div class="vnc-loading" id="vncLoading">
                        <div class="vnc-spinner"></div>
                        <p>Đang kết nối đến thiết bị...</p>
                    </div>
                    <canvas id="vncCanvas" style="display: none;"></canvas>
                </div>
            </div>
        </div>

        <script>
            let devices = [];
            let sortMode = "id"; // id | online | offline
            let autoRefreshAll = true;
            const pausedDevices = new Set();

            const deviceGrid = document.getElementById("deviceGrid");
            const deviceCountSpan = document.getElementById("deviceCount");
            const onlineCountSpan = document.getElementById("onlineCount");

            const sortIdBtn = document.getElementById("sortIdBtn");
            const sortOnlineBtn = document.getElementById("sortOnlineBtn");
            const sortOfflineBtn = document.getElementById("sortOfflineBtn");

            const columnsInput = document.getElementById("columnsInput");
            const sizeInput = document.getElementById("sizeInput");
            const startAllBtn = document.getElementById("startAllBtn");
            const stopAllBtn = document.getElementById("stopAllBtn");

            function setSortMode(mode) {
                sortMode = mode;
                sortIdBtn.classList.toggle("active", mode === "id");
                sortOnlineBtn.classList.toggle("active", mode === "online");
                sortOfflineBtn.classList.toggle("active", mode === "offline");
                renderDevices();
            }

            sortIdBtn.addEventListener("click", () => setSortMode("id"));
            sortOnlineBtn.addEventListener("click", () => setSortMode("online"));
            sortOfflineBtn.addEventListener("click", () => setSortMode("offline"));

            columnsInput.addEventListener("change", () => {
                const val = Math.max(1, Math.min(12, parseInt(columnsInput.value || "1", 10)));
                document.documentElement.style.setProperty("--columns", val);
            });
            document.documentElement.style.setProperty("--columns", columnsInput.value);

            sizeInput.addEventListener("input", () => {
                const val = parseInt(sizeInput.value || "220", 10);
                document.documentElement.style.setProperty("--thumb-height", val + "px");
            });
            document.documentElement.style.setProperty("--thumb-height", sizeInput.value + "px");

            startAllBtn.addEventListener("click", () => {
                autoRefreshAll = true;
                startAllBtn.classList.add("active");
                stopAllBtn.classList.remove("active");
            });

            stopAllBtn.addEventListener("click", () => {
                autoRefreshAll = false;
                startAllBtn.classList.remove("active");
                stopAllBtn.classList.add("active");
            });

            async function fetchDevices() {
                try {
                    const res = await fetch("/api/devices");
                    const data = await res.json();
                    devices = data;
                    renderDevices();
                } catch (e) {
                    console.error("Lỗi fetch /api/devices", e);
                }
            }

            function renderDevices() {
                if (!Array.isArray(devices)) return;

                let arr = devices.slice();

                if (sortMode === "online") {
                    arr.sort((a, b) => {
                        if (a.online === b.online) return a.id.localeCompare(b.id);
                        return (b.online ? 1 : 0) - (a.online ? 1 : 0);
                    });
                } else if (sortMode === "offline") {
                    arr.sort((a, b) => {
                        if (a.online === b.online) return a.id.localeCompare(b.id);
                        return (a.online ? 1 : 0) - (b.online ? 1 : 0);
                    });
                } else {
                    arr.sort((a, b) => a.id.localeCompare(b.id));
                }

                deviceGrid.innerHTML = "";
                let onlineCount = 0;

                for (const d of arr) {
                    if (d.online) onlineCount++;

                    const card = document.createElement("div");
                    card.className = "device-card " + (d.online ? "online" : "offline");
                    if (pausedDevices.has(d.id)) {
                        card.classList.add("paused");
                    }
                    card.dataset.id = d.id;

                    const last = d.last_ts ? d.last_ts.replace("T", " ").replace("Z", "") : "";

                    card.innerHTML = `
                        <div class="card-header">
                            <div class="name">${d.id}</div>
                            <div class="status">${d.online ? "🟢 Bật" : "⚫ Tắt"}</div>
                        </div>
                        <div class="img-wrap">
                            <img src="/snapshot/latest/${d.id}?t=${Date.now()}" alt="${d.id}">
                        </div>
                        <div class="card-footer">
                            <div style="display: flex; gap: 4px;">
                                <button class="toggle-btn">${pausedDevices.has(d.id) ? "▶ Tiếp tục" : "⏸ Tạm dừng"}</button>
                                ${d.online ? `<button class="vnc-btn" data-device-id="${d.id}">📺 VNC Live</button>` : ''}
                            </div>
                            <span class="time">${last}</span>
                        </div>
                    `;

                    const toggleBtn = card.querySelector(".toggle-btn");
                    toggleBtn.addEventListener("click", (ev) => {
                        ev.stopPropagation();
                        if (pausedDevices.has(d.id)) {
                            pausedDevices.delete(d.id);
                            toggleBtn.textContent = "⏸ Tạm dừng";
                            card.classList.remove("paused");
                        } else {
                            pausedDevices.add(d.id);
                            toggleBtn.textContent = "▶ Tiếp tục";
                            card.classList.add("paused");
                        }
                    });

                    const vncBtn = card.querySelector(".vnc-btn");
                    if (vncBtn) {
                        vncBtn.addEventListener("click", (ev) => {
                            ev.stopPropagation();
                            openVNCViewer(d.id);
                        });
                    }

                    card.addEventListener("click", (ev) => {
                        if (ev.target.classList.contains("toggle-btn") || ev.target.classList.contains("vnc-btn")) return;
                        card.classList.toggle("expanded");
                    });

                    deviceGrid.appendChild(card);
                }

                deviceCountSpan.textContent = arr.length.toString();
                onlineCountSpan.textContent = onlineCount.toString();
            }

            function refreshImages() {
                if (!autoRefreshAll) return;
                const now = Date.now();
                document.querySelectorAll(".device-card").forEach(card => {
                    const id = card.dataset.id;
                    if (pausedDevices.has(id)) return;
                    const img = card.querySelector("img");
                    if (img) {
                        img.src = "/snapshot/latest/" + id + "?t=" + now;
                    }
                });
            }

            setInterval(refreshImages, 1000);   // refresh ảnh mỗi 1s
            setInterval(fetchDevices, 5000);    // cập nhật trạng thái online/offline mỗi 5s
            fetchDevices();

            // ===========================================
            // VNC VIEWER FUNCTIONALITY
            // ===========================================
            let currentVNCDevice = null;
            let vncWebSocket = null;
            let vncCanvas = null;
            let vncContext = null;

            function openVNCViewer(deviceId) {
                currentVNCDevice = deviceId;
                document.getElementById('vncModal').classList.add('active');
                document.getElementById('vncDeviceName').textContent = '📺 VNC Viewer - ' + deviceId;
                document.getElementById('vncLoading').style.display = 'block';
                document.getElementById('vncCanvas').style.display = 'none';
                updateVNCStatus('Đang kết nối...', false);
                
                connectVNCWebSocket(deviceId);
            }

            function closeVNCViewer() {
                if (vncWebSocket) {
                    vncWebSocket.close();
                    vncWebSocket = null;
                }
                document.getElementById('vncModal').classList.remove('active');
                currentVNCDevice = null;
            }

            function reconnectVNC() {
                if (currentVNCDevice) {
                    closeVNCWebSocket();
                    connectVNCWebSocket(currentVNCDevice);
                }
            }

            function closeVNCWebSocket() {
                if (vncWebSocket) {
                    vncWebSocket.close();
                    vncWebSocket = null;
                }
            }

            function connectVNCWebSocket(deviceId) {
                // Kết nối đến Node.js VNC proxy server
                // Thay đổi URL này phù hợp với server của bạn
                const wsUrl = 'ws://' + window.location.hostname + ':8080/vnc/' + deviceId;
                
                console.log('Connecting to VNC WebSocket:', wsUrl);
                updateVNCStatus('Đang kết nối đến ' + wsUrl + '...', false);

                try {
                    vncWebSocket = new WebSocket(wsUrl);
                    vncWebSocket.binaryType = 'arraybuffer';

                    vncWebSocket.onopen = function() {
                        console.log('VNC WebSocket connected');
                        updateVNCStatus('✅ Đã kết nối', true);
                        document.getElementById('vncLoading').style.display = 'none';
                        document.getElementById('vncCanvas').style.display = 'block';
                        
                        // Initialize canvas
                        vncCanvas = document.getElementById('vncCanvas');
                        vncContext = vncCanvas.getContext('2d');
                    };

                    vncWebSocket.onmessage = function(event) {
                        // Nhận dữ liệu VNC từ proxy
                        // Đây là raw VNC protocol data
                        // Bạn cần sử dụng thư viện noVNC để decode
                        console.log('Received VNC data:', event.data.byteLength, 'bytes');
                        
                        // Tạm thời hiển thị thông báo (cần tích hợp noVNC library)
                        updateVNCStatus('✅ Đang nhận dữ liệu VNC...', true);
                    };

                    vncWebSocket.onerror = function(error) {
                        console.error('VNC WebSocket error:', error);
                        updateVNCStatus('❌ Lỗi kết nối', false);
                    };

                    vncWebSocket.onclose = function() {
                        console.log('VNC WebSocket closed');
                        updateVNCStatus('⚫ Đã ngắt kết nối', false);
                        document.getElementById('vncLoading').innerHTML = '<div class="vnc-spinner"></div><p>Mất kết nối. Click "Kết nối lại" để thử lại.</p>';
                        document.getElementById('vncLoading').style.display = 'block';
                        document.getElementById('vncCanvas').style.display = 'none';
                    };

                } catch (e) {
                    console.error('Failed to connect VNC WebSocket:', e);
                    updateVNCStatus('❌ Lỗi: ' + e.message, false);
                }
            }

            function updateVNCStatus(text, connected) {
                document.getElementById('vncStatusText').textContent = text;
                const dot = document.getElementById('vncStatusDot');
                if (connected) {
                    dot.classList.add('connected');
                } else {
                    dot.classList.remove('connected');
                }
            }

            function toggleVNCFullscreen() {
                const modal = document.getElementById('vncModal');
                if (!document.fullscreenElement) {
                    modal.requestFullscreen().catch(err => {
                        console.error('Fullscreen error:', err);
                    });
                } else {
                    document.exitFullscreen();
                }
            }

            // Đóng modal khi nhấn ESC
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && document.getElementById('vncModal').classList.contains('active')) {
                    closeVNCViewer();
                }
            });

            // IMPORTANT: Để VNC hoạt động đầy đủ, bạn cần:
            // 1. Chạy server-vnc-proxy.js trên server (port 8080)
            // 2. Tích hợp thư viện noVNC để decode VNC protocol
            // 3. Hoặc sử dụng một VNC client library khác
            
            console.log('VNC Viewer initialized. Waiting for connections...');
        </script>
    </body>
    </html>
    """
    return Response(html, mimetype="text/html")


# ==============================================================================
# 3) PHẦN DUYỆT FILE + UPLOAD ZIP (GIỮ LẠI)
# ==============================================================================

@app.route("/")
def index():
    return browse_folder("")


@app.route("/upload", methods=["POST"])
def upload_file():
    """
    Upload file .zip lên server, lưu vào:
      ./<project_name>/uploads/<filename>.zip
    """
    try:
        if "file" not in request.files:
            return "Không có file trong request", 400
        file = request.files["file"]
        if file.filename == "":
            return "Tên file trống", 400
        if not file.filename.lower().endswith(".zip"):
            return "Chỉ chấp nhận file .zip", 400

        project_name = request.form.get("project_name", "").strip()
        if not project_name:
            return "Thiếu tên project", 400

        project_safe = secure_filename(project_name)
        upload_folder = os.path.join(ROOT_FOLDER, project_safe, "uploads")
        os.makedirs(upload_folder, exist_ok=True)

        filename = secure_filename(file.filename)
        zip_path = os.path.join(upload_folder, filename)
        file.save(zip_path)

        return f"Upload thành công! File đã lưu tại: /{project_safe}/uploads/{filename}", 200
    except Exception as e:
        return f"Lỗi upload: {str(e)}", 500


@app.route("/<path:subpath>")
def browse_folder(subpath):
    folder_path = os.path.join(ROOT_FOLDER, subpath)

    if not os.path.exists(folder_path):
        return f"Đường dẫn không tồn tại: {subpath}", 404

    if os.path.isfile(folder_path):
        return handle_file(folder_path)

    if os.path.isdir(folder_path):
        return list_directory(folder_path, subpath)

    return "Không xác định được loại đường dẫn", 400


def handle_file(filepath):
    filename = os.path.basename(filepath)
    file_ext = os.path.splitext(filename)[1].lower()

    if file_ext in TEXT_EXTENSIONS:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            return Response(content, mimetype="text/plain")
        except Exception as e:
            return f"Lỗi đọc file: {str(e)}", 500
    else:
        try:
            return send_file(filepath, as_attachment=False)
        except Exception as e:
            return f"Lỗi tải file: {str(e)}", 500


def list_directory(folder_path, subpath):
    try:
        items = os.listdir(folder_path)
        items.sort()

        links = []

        if subpath:
            parent_path = os.path.dirname(subpath)
            if parent_path:
                links.append(f'<a href="/{parent_path}">📁 .. (Thư mục cha)</a>')
            else:
                links.append('<a href="/">📁 .. (Thư mục gốc)</a>')
            links.append("<br><br>")

        # Thư mục con
        for item in items:
            item_path = os.path.join(folder_path, item)
            if item.startswith(".") or item == "__pycache__":
                continue
            if os.path.isdir(item_path):
                folder_url = f"/{subpath}/{item}" if subpath else f"/{item}"
                links.append(f'<a href="{folder_url}">📁 {item}/</a>')

        # File
        if subpath:
            links.append("<br>")
        for item in items:
            item_path = os.path.join(folder_path, item)
            if item.startswith(".") or item == "__pycache__":
                continue
            if os.path.isfile(item_path):
                filename = item
                file_url = f"/{subpath}/{filename}" if subpath else f"/{filename}"
                file_ext = os.path.splitext(filename)[1].lower()
                if file_ext in TEXT_EXTENSIONS:
                    icon = "📄"
                elif file_ext in MEDIA_EXTENSIONS:
                    icon = "🎬" if file_ext in {".mp4", ".avi", ".mov", ".mkv"} else "🖼️"
                else:
                    icon = "📦"
                links.append(f'<a href="{file_url}">{icon} {filename}</a>')

        upload_form = """
        <br><br><hr>
        <form action="/upload" method="post" enctype="multipart/form-data">
            <label>📁 Tên project:</label>
            <input type="text" name="project_name" required>
            <label> 📦 File ZIP:</label>
            <input type="file" name="file" accept=".zip" required>
            <button type="submit">📤 Upload ZIP</button>
        </form>
        """

        title = f"<h3>📂 Thư mục: /{subpath}</h3><br>" if subpath else "<h3>📂 Thư mục gốc</h3><br>"
        return title + "<br>".join(links) + upload_form
    except Exception as e:
        return f"Lỗi đọc thư mục: {str(e)}", 500


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5678)
