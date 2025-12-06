# Hướng dẫn tích hợp TrollVNC với Web Server

## Tổng quan

Giải pháp này cho phép iPhone kết nối ra server của bạn (reverse connection) để vượt qua vấn đề NAT/firewall khi mỗi iPhone có IP 4G khác nhau.

## Kiến trúc

```
iPhone (4G) → Reverse VNC → serverapi.xyz:5500 → VNC Proxy → WebSocket → Web Client
```

## Bước 1: Setup Server (serverapi.xyz)

### 1.1 Cài đặt Node.js và dependencies

```bash
# Trên server của bạn
npm install
```

### 1.2 Chạy VNC Proxy Server

```bash
npm start
```

Hoặc dùng PM2 để chạy background:

```bash
npm install -g pm2
pm2 start server-vnc-proxy.js --name vnc-proxy
pm2 save
```

### 1.3 Mở ports trên firewall

- Port 5500: VNC listener (iPhone kết nối đến)
- Port 8080: WebSocket server (web client kết nối)
- Port 3000: HTTP API server

```bash
# Ubuntu/Debian
sudo ufw allow 5500/tcp
sudo ufw allow 8080/tcp
sudo ufw allow 3000/tcp
```

## Bước 2: Cấu hình iPhone

### 2.1 Tạo Managed.plist

Copy file `prefs/TrollVNCPrefs/Resources/Managed.plist.example` thành `prefs/TrollVNCPrefs/Resources/Managed.plist` và chỉnh sửa:

```xml
<key>ReverseSocket</key>
<string>serverapi.xyz:5500</string>
```

### 2.2 Build và cài đặt TrollVNC

```bash
# Build với Managed.plist
make THEOS_PACKAGE_SCHEME=rootless
# Hoặc dùng GitHub Actions với is_managed=true
```

### 2.3 Cài đặt trên iPhone

Sau khi build, cài đặt package lên iPhone. TrollVNC sẽ tự động kết nối reverse đến server của bạn.

## Bước 3: Tích hợp với Web của bạn

### 3.1 API Endpoints

Server proxy cung cấp các API:

- `GET /api/devices` - Lấy danh sách devices đang kết nối
- `GET /api/device/:deviceId` - Lấy thông tin device
- `GET /api/ws-info` - Lấy thông tin WebSocket endpoint

### 3.2 WebSocket Connection

Kết nối WebSocket với device ID:

```javascript
const ws = new WebSocket('ws://serverapi.xyz:8080?deviceId=YOUR_DEVICE_ID');
```

### 3.3 Sử dụng noVNC library

Để hiển thị VNC trên web, bạn nên dùng [noVNC](https://github.com/novnc/noVNC):

```html
<script src="https://cdn.jsdelivr.net/npm/@novnc/novnc@1.4.0/lib/noVNC.min.js"></script>

<script>
const rfb = new RFB(document.getElementById('vnc-canvas'), 'ws://serverapi.xyz:8080?deviceId=YOUR_DEVICE_ID');
</script>
```

## Bước 4: Tùy chỉnh cho nhiều iPhone

### 4.1 Device ID

Mỗi iPhone cần có device ID duy nhất. Bạn có thể:

1. **Tự động từ UDID**: Sửa code TrollVNC để gửi UDID trong reverse connection
2. **Từ Settings**: Cho phép user nhập device ID trong Settings app
3. **Từ server**: Server assign device ID khi iPhone kết nối

### 4.2 Sửa code TrollVNC để gửi Device ID

Cần sửa file `src/trollvncserver.mm` tại dòng ~4720 để gửi device ID trước khi gửi VNC protocol:

```objc
// Trong hàm rfbReverseConnection, trước khi kết nối
// Gửi device ID (32 bytes) trước VNC handshake
NSString *deviceId = [[[UIDevice currentDevice] identifierForVendor] UUIDString];
const char *deviceIdCStr = [deviceId UTF8String];
send(socket, deviceIdCStr, 32, 0); // Gửi 32 bytes device ID
```

## Bước 5: Tích hợp với serverapi.xyz hiện tại

### 5.1 Thêm vào web server của bạn

Nếu bạn đã có web server, có thể tích hợp proxy vào:

```javascript
// Trong server của bạn
const vncProxy = require('./server-vnc-proxy');
// Hoặc chạy như microservice riêng
```

### 5.2 API để quản lý devices

Thêm API vào server của bạn:

```javascript
app.get('/api/vnc/devices', async (req, res) => {
    // Call proxy API
    const response = await fetch('http://localhost:3000/api/devices');
    const data = await response.json();
    res.json(data);
});
```

## Troubleshooting

### iPhone không kết nối được

1. Kiểm tra firewall trên server
2. Kiểm tra reverse connection config trong Managed.plist
3. Xem logs: `pm2 logs vnc-proxy`

### Web không hiển thị

1. Kiểm tra WebSocket connection trong browser console
2. Đảm bảo dùng noVNC hoặc VNC client library
3. Kiểm tra CORS settings

### Nhiều iPhone cùng lúc

1. Mỗi iPhone cần device ID duy nhất
2. Server proxy hỗ trợ nhiều connections
3. Web client chọn device từ dropdown

## Security Notes

⚠️ **Quan trọng**: 

- Thêm authentication cho WebSocket connections
- Sử dụng WSS (WebSocket Secure) trong production
- Validate device IDs
- Rate limiting cho API endpoints
- Firewall rules để chỉ cho phép connections từ trusted sources

## Next Steps

1. Implement device ID trong TrollVNC
2. Thêm authentication
3. Tích hợp với database để lưu device info
4. Thêm user management
5. Implement reconnection logic tốt hơn

