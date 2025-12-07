# 🏗️ Giải Thích Kiến Trúc Port - Hệ Thống TrollVNC

## 📊 Tổng Quan Các Port

Hệ thống có **2 server riêng biệt** với các port khác nhau:

```
┌─────────────────────────────────────────────────────────────┐
│                    SERVER (serverapi.xyz)                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  1. server-vnc-proxy.js (Node.js)                            │
│     ├─ Port 10001-10500: VNC Listener (iPhone kết nối đến)   │
│     ├─ Port 3000: HTTP API (Flask gọi để lấy danh sách)     │
│     └─ Port 8080: WebSocket (Web client kết nối để xem VNC) │
│                                                               │
│  2. severapixyz.py (Flask)                                   │
│     └─ Port 5678: Web Monitor (Trình duyệt truy cập)         │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## 🔌 Chi Tiết Từng Port

### 1. **Port 10001-10500** (VNC Listener)
- **Mục đích**: iPhone kết nối reverse connection đến server
- **Server**: `server-vnc-proxy.js`
- **Ví dụ**:
  - Device 1 → Port 10001
  - Device 10 → Port 10010
  - Device 300 → Port 10300
- **Luồng**: `iPhone (4G/WiFi) → serverapi.xyz:10010`

### 2. **Port 3000** (HTTP API)
- **Mục đích**: Flask server gọi để lấy danh sách VNC devices
- **Server**: `server-vnc-proxy.js`
- **URL**: `http://localhost:3000/api/devices`
- **Luồng**: `severapixyz.py → http://localhost:3000/api/devices`
- **Tại sao localhost?**: Vì cả 2 server chạy trên cùng 1 máy

### 3. **Port 8080** (WebSocket)
- **Mục đích**: Web client kết nối để xem VNC live
- **Server**: `server-vnc-proxy.js`
- **URL**: `ws://serverapi.xyz:8080?deviceId=Device-10`
- **Luồng**: `Web Browser → ws://serverapi.xyz:8080 → VNC data từ iPhone`

### 4. **Port 5678** (Flask Web Monitor)
- **Mục đích**: Trình duyệt truy cập để xem dashboard
- **Server**: `severapixyz.py`
- **URL**: `http://serverapi.xyz:5678/monitor`
- **Luồng**: `Web Browser → http://serverapi.xyz:5678/monitor`

## 🔄 Luồng Hoạt Động Đầy Đủ

### Bước 1: iPhone kết nối VNC
```
iPhone (Device 10)
  ↓
Nhập: serverapi.xyz:10010
  ↓
Kết nối reverse connection
  ↓
server-vnc-proxy.js nhận trên port 10010
  ↓
Gửi Device ID: "Device-10"
```

### Bước 2: Flask lấy danh sách VNC devices
```
severapixyz.py
  ↓
Gọi: http://localhost:3000/api/devices
  ↓
server-vnc-proxy.js trả về:
  [
    {
      "deviceId": "Device-10",
      "port": 10010,
      "isConnected": true
    }
  ]
  ↓
Merge với snapshot devices
  ↓
Trả về cho web monitor
```

### Bước 3: Web client xem VNC
```
Web Browser
  ↓
Truy cập: http://serverapi.xyz:5678/monitor
  ↓
Click "📺 VNC" cho Device-10
  ↓
Kết nối: ws://serverapi.xyz:8080?deviceId=Device-10
  ↓
server-vnc-proxy.js proxy VNC data
  ↓
Hiển thị màn hình iPhone trên web
```

## ❓ Tại Sao Port 3000?

### Câu hỏi: "Sao lại port 3000, không phải 10001?"

**Trả lời:**
- **Port 10001-10500**: iPhone kết nối VNC (raw VNC protocol)
- **Port 3000**: HTTP API để Flask lấy thông tin (REST API)
- **Khác nhau**: 
  - Port 10010 = VNC connection (binary data)
  - Port 3000 = HTTP API (JSON data)

### Ví dụ cụ thể:

```python
# severapixyz.py
VNC_PROXY_URL = "http://localhost:3000"  # ← HTTP API port

# Gọi API để lấy danh sách
res = requests.get(f"{VNC_PROXY_URL}/api/devices")
# → http://localhost:3000/api/devices
# → Trả về JSON: [{"deviceId": "Device-10", "port": 10010}]
```

```javascript
// server-vnc-proxy.js
const HTTP_PORT = 3000;  // ← HTTP API port
httpServer.listen(HTTP_PORT, () => {
    console.log(`[HTTP] Server started on port ${HTTP_PORT}`);
});

// iPhone kết nối VNC
const VNC_BASE_PORT = 10001;  // ← VNC listener port
// iPhone → serverapi.xyz:10010 (VNC connection)
```

## 📋 Tóm Tắt

| Port | Mục đích | Server | Client |
|------|----------|--------|--------|
| **10001-10500** | VNC Listener | server-vnc-proxy.js | iPhone |
| **3000** | HTTP API | server-vnc-proxy.js | severapixyz.py |
| **8080** | WebSocket | server-vnc-proxy.js | Web Browser |
| **5678** | Web Monitor | severapixyz.py | Web Browser |

## ✅ Kết Luận

- **Port 10001-10500**: iPhone kết nối VNC (1 port cho mỗi device)
- **Port 3000**: HTTP API để Flask lấy thông tin (1 port cho tất cả)
- **Port 8080**: WebSocket để web client xem VNC (1 port cho tất cả)
- **Port 5678**: Web monitor dashboard (1 port cho tất cả)

**Port 3000 là HTTP API port, không phải VNC port!**

---

**Status**: ✅ Giải thích rõ ràng kiến trúc port

