# Hướng Dẫn Cấu Hình Port và IP cho TrollVNC

## 📋 Tóm Tắt Cấu Hình

- **IP Server**: `serverapi.xyz` (cố định)
- **Port Range**: 10001 - 10500 (500 devices)
- **Công thức**: `Port = 10001 + (Device_Number - 1)`

## 🔢 Bảng Port Theo Device

| Device | Port | Cấu hình trên iPhone |
|--------|------|---------------------|
| Device 1 | 10001 | `serverapi.xyz:10001` |
| Device 2 | 10002 | `serverapi.xyz:10002` |
| Device 10 | 10010 | `serverapi.xyz:10010` |
| Device 30 | 10030 | `serverapi.xyz:10030` |
| Device 100 | 10100 | `serverapi.xyz:10100` |
| Device 500 | 10500 | `serverapi.xyz:10500` |

## 📱 Cách Cấu Hình Trên iPhone

### Cách 1: Cấu hình thủ công trong Settings

1. Mở **Settings** → **TrollVNC**
2. Bật **Enabled**
3. Vào **Reverse Connection**
4. Nhập **Server**: `serverapi.xyz:10001` (thay số port theo device)
5. Chọn **Mode**: `viewer`
6. Lưu và respring

### Cách 2: Dùng Managed Configuration (cho nhiều devices)

Tạo file `Managed.plist` với cấu hình:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <!-- Enable TrollVNC -->
    <key>Enabled</key>
    <true/>
    
    <!-- Desktop Name (để nhận diện device) -->
    <key>DesktopName</key>
    <string>Device-10</string>
    
    <!-- Reverse Connection Configuration -->
    <key>ReverseMode</key>
    <string>viewer</string>
    
    <!-- Server: serverapi.xyz:PORT (thay PORT theo device) -->
    <key>ReverseSocket</key>
    <string>serverapi.xyz:10010</string>
    
    <!-- Performance Settings -->
    <key>Scale</key>
    <real>0.75</real>
    
    <key>FrameRateSpec</key>
    <string>30:60:120</string>
    
    <key>ClipboardEnabled</key>
    <true/>
    
    <key>KeepAliveSec</key>
    <integer>60</integer>
</dict>
</plist>
```

**Lưu ý**: Mỗi device cần một file `Managed.plist` riêng với `ReverseSocket` khác nhau.

## 🖥️ Cấu Hình Server

### 1. VNC Proxy Server (`server-vnc-proxy.js`)

Server tự động listen trên tất cả ports từ 10001 đến 10500:

```bash
node server-vnc-proxy.js
```

**Output**:
```
[INFO] Initializing 500 VNC listeners (ports 10001 to 10500)...
[INFO] All 500 VNC listeners initialized
[HTTP] Server started on port 3000
[INFO] VNC Listeners: 10001 to 10500 (500 ports)
[INFO] WebSocket Server: 8080
[INFO] Device 1 → Port 10001, Device 10 → Port 10010, Device 500 → Port 10500
[INFO] Ready to accept connections from iPhones!
```

### 2. Flask Server (`severapixyz.py`)

Flask server tự động tích hợp với VNC proxy:

```bash
python severapixyz.py
```

**Output**:
```
 * Running on http://0.0.0.0:5678
```

## 🌐 Xem Trên Web Monitor

1. Mở trình duyệt: `http://your-server-ip:5678/monitor`
2. Web monitor sẽ hiển thị:
   - Tất cả devices (snapshot + VNC)
   - Port của mỗi device (nếu đã kết nối VNC)
   - Trạng thái: 🟢 Bật / ⚫ Tắt / 🔵 VNC
3. Click nút **📺 VNC (Port XXXX)** để xem live VNC

## ✅ Kiểm Tra Kết Nối

### Kiểm tra trên iPhone:
1. Settings → TrollVNC → Kiểm tra **Enabled** = ON
2. Kiểm tra **Reverse Socket** = `serverapi.xyz:100XX` (đúng port)
3. Respring hoặc restart service

### Kiểm tra trên Server:
1. Xem log của `server-vnc-proxy.js`:
   ```
   [VNC:10010] Device ID: Device-10
   [VNC:10010] New connection from ...
   ```

2. Kiểm tra API:
   ```bash
   curl http://localhost:3000/api/devices
   ```

3. Xem trên web monitor: Device có icon 🔵 VNC = đã kết nối

## 🔧 Troubleshooting

### Device không kết nối được VNC:

1. **Kiểm tra port đúng chưa**:
   - Device 10 phải dùng port 10010
   - Công thức: `Port = 10001 + (Device_Number - 1)`

2. **Kiểm tra server đang chạy**:
   ```bash
   # Kiểm tra VNC proxy
   ps aux | grep server-vnc-proxy
   
   # Kiểm tra Flask server
   ps aux | grep severapixyz
   ```

3. **Kiểm tra firewall**:
   - Port 10001-10500 phải mở trên server
   - Port 8080 (WebSocket) phải mở
   - Port 3000 (HTTP API) phải mở

4. **Kiểm tra log**:
   - Xem log của `server-vnc-proxy.js` để biết device có kết nối không
   - Xem log của iPhone (nếu có)

### Port đã được sử dụng:

Nếu thấy lỗi `EADDRINUSE`:
```bash
# Tìm process đang dùng port
lsof -i :10010

# Kill process (nếu cần)
kill -9 <PID>
```

## 📝 Lưu Ý Quan Trọng

1. **IP Server**: `serverapi.xyz` là cố định, không đổi
2. **Port**: Mỗi device có port riêng, không trùng
3. **Device ID**: Phải đồng nhất giữa:
   - Desktop Name trên iPhone
   - Device ID trong snapshot API
   - Device ID trong VNC connection
4. **Auto Reconnect**: Khi IP iPhone đổi, device tự động reconnect với cùng port và Device ID

## 🎯 Ví Dụ Cấu Hình

### Device 10:
- **Desktop Name**: `Device-10`
- **Reverse Socket**: `serverapi.xyz:10010`
- **Port trên server**: `10010`

### Device 30:
- **Desktop Name**: `Device-30`
- **Reverse Socket**: `serverapi.xyz:10030`
- **Port trên server**: `10030`

---

**Tóm lại**: Chỉ cần set port trên iPhone theo công thức `10001 + (Device_Number - 1)`, IP luôn là `serverapi.xyz`. Server tự động nhận diện device qua Device ID và port.

