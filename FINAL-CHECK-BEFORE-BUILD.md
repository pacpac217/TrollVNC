# ✅ KIỂM TRA CUỐI CÙNG TRƯỚC KHI BUILD TROLLVNC

**Ngày kiểm tra**: 2025-12-06  
**Mục tiêu**: Kết nối iPhone → serverapi.xyz → View trên web

---

## 🎯 TỔNG QUAN HỆ THỐNG

```
┌─────────────┐         ┌──────────────────┐         ┌─────────────────┐
│   iPhone    │ Reverse │  serverapi.xyz   │ WebSocket│   Web Browser   │
│  (TrollVNC) │────────>│ Node.js :5500    │────────>│ https://        │
│   4G/WiFi   │   VNC   │ Flask   :5678    │         │ serverapi.xyz   │
└─────────────┘         └──────────────────┘         └─────────────────┘
                              ↑
                              │
                        WebSocket :8080
```

---

## ✅ PHẦN 1: KIỂM TRA FILES ĐÃ CHỈNH SỬA

### 📱 iPhone Side (Source Code TrollVNC)

#### ✅ 1.1 File: `src/trollvncserver.mm`

**Đã chỉnh sửa:**
- ✅ Line 24: Import `#import <UIKit/UIDevice.h>`
- ✅ Line 4723-4727: Lấy Device ID từ `UIDevice.currentDevice.identifierForVendor`
- ✅ Line 4730: Tạo reverse connection đến `gRepeaterHost:gRepeaterPort`
- ✅ Line 4734-4751: Gửi Device ID (32 bytes) ngay sau khi kết nối
- ✅ Logic auto-reconnect với watchdog đã có sẵn

**Code quan trọng:**
```objective-c
// Line 4723: Lấy Device ID
NSString *deviceId = [[[UIDevice currentDevice] identifierForVendor] UUIDString];

// Line 4730: Kết nối reverse
sClient = rfbReverseConnection(gScreen, gRepeaterHost, gRepeaterPort);

// Line 4745: Gửi Device ID
ssize_t sent = send(sClient->sock, deviceIdBytes, 32, 0);
```

#### ✅ 1.2 File: `prefs/TrollVNCPrefs/Resources/Managed.plist`

**Trạng thái:** ✅ **ĐÃ TẠO VÀ CẤU HÌNH ĐÚNG**

**Nội dung:**
```xml
<key>Enabled</key>
<true/>

<key>ReverseMode</key>
<string>viewer</string>

<key>ReverseSocket</key>
<string>serverapi.xyz:5500</string>  ← ĐÃ ĐÚNG!

<key>KeepAliveSec</key>
<integer>60</integer>
```

**Ý nghĩa:**
- iPhone sẽ tự động kết nối đến `serverapi.xyz:5500` khi TrollVNC khởi động
- Mode `viewer` = reverse connection (iPhone chủ động kết nối ra ngoài)
- Keep alive 60s = giữ kết nối liên tục

---

### 🖥️ Server Side (serverapi.xyz)

#### ✅ 2.1 File: `server-vnc-proxy.js` (Node.js)

**Trạng thái:** ✅ **HOÀN CHỈNH**

**Cấu hình:**
- Port 5500: Nhận VNC từ iPhone
- Port 8080: WebSocket cho web client
- Port 3000: HTTP API

**Chức năng:**
- ✅ Đọc Device ID từ 32 bytes đầu tiên
- ✅ Lưu trữ connection theo Device ID
- ✅ Xử lý reconnect khi IP thay đổi
- ✅ Forward VNC data đến web client qua WebSocket
- ✅ API `/api/devices` để list devices

#### ✅ 2.2 File: `severapixyz.py` (Flask Web UI)

**Trạng thái:** ✅ **ĐÃ TÍCH HỢP VNC VIEWER**

**Đã thêm:**
- ✅ VNC Viewer Modal (popup fullscreen)
- ✅ CSS styling cho VNC viewer
- ✅ JavaScript để kết nối WebSocket
- ✅ Nút "📺 VNC Live" trên mỗi device online
- ✅ Status indicator (connecting/connected/disconnected)
- ✅ Fullscreen button
- ✅ Reconnect button

**WebSocket URL:** `ws://serverapi.xyz:8080/vnc/{deviceId}`

---

## 🚀 PHẦN 2: CÁC BƯỚC TRIỂN KHAI

### Bước 1: Deploy trên Server (serverapi.xyz)

#### 1.1 Cài đặt Node.js dependencies

```bash
cd /path/to/TrollVNC-main
npm install
```

**Output mong đợi:**
```
added 1 package
ws@8.14.2
```

#### 1.2 Chạy Node.js VNC Proxy

**Option A: Chạy trực tiếp (test)**
```bash
node server-vnc-proxy.js
```

**Option B: Chạy background với PM2 (production)**
```bash
npm install -g pm2
pm2 start server-vnc-proxy.js --name vnc-proxy
pm2 save
pm2 startup
```

**Kiểm tra:**
```bash
pm2 status
# Nên thấy: vnc-proxy | online
```

#### 1.3 Mở Firewall Ports

```bash
# Ubuntu/Debian
sudo ufw allow 5500/tcp   # VNC từ iPhone
sudo ufw allow 8080/tcp   # WebSocket cho web
sudo ufw allow 3000/tcp   # HTTP API (optional)

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=5500/tcp
sudo firewall-cmd --permanent --add-port=8080/tcp
sudo firewall-cmd --permanent --add-port=3000/tcp
sudo firewall-cmd --reload
```

#### 1.4 Chạy Flask Web UI (nếu chưa chạy)

```bash
python3 severapixyz.py
# Hoặc
gunicorn -w 4 -b 0.0.0.0:5678 severapixyz:app
```

**URL:** https://serverapi.xyz/monitor

---

### Bước 2: Build TrollVNC trên macOS

#### 2.1 Cài đặt Theos (nếu chưa có)

```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/theos/theos/master/bin/install-theos)"
```

#### 2.2 Build Package

```bash
cd /path/to/TrollVNC-main

# Clean trước
make clean

# Build
make package THEOS_PACKAGE_SCHEME=rootless
# Hoặc cho rootful:
# make package THEOS_PACKAGE_SCHEME=roothide
```

**Output mong đợi:**
```
==> Building TrollVNC...
==> Packaging...
==> Created: packages/com.82flex.trollvnc_X.X.X_iphoneos-arm.deb
```

#### 2.3 Lấy file .deb

File sẽ được tạo trong thư mục `packages/`:
```
packages/com.82flex.trollvnc_X.X.X_iphoneos-arm.deb
```

---

### Bước 3: Cài đặt trên iPhone

#### 3.1 Copy file .deb lên iPhone

**Option A: qua SSH**
```bash
scp packages/*.deb mobile@IPHONE_IP:/var/mobile/
```

**Option B: qua Filza**
- Dùng iTunes/Finder share file
- Hoặc dùng cloud storage (Dropbox, Google Drive)

#### 3.2 Cài đặt

**Option A: TrollStore (khuyến nghị)**
1. Mở TrollStore
2. Tap vào dấu `+`
3. Chọn file `.deb`
4. Install

**Option B: dpkg (qua SSH)**
```bash
ssh mobile@IPHONE_IP
sudo dpkg -i /var/mobile/com.82flex.trollvnc*.deb
killall -9 SpringBoard  # Respring
```

#### 3.3 Khởi động TrollVNC

1. Mở app **TrollVNC** trên iPhone
2. Vào **Settings** → **TrollVNC**
3. Bật **Enabled**

**Hoặc**, app sẽ tự động khởi động nếu đã bật trong Settings.

---

## 🔍 PHẦN 3: KIỂM TRA KẾT NỐI

### Trên Server (kiểm tra logs)

#### Check Node.js proxy logs:

```bash
# Nếu dùng node trực tiếp:
# Xem terminal output

# Nếu dùng PM2:
pm2 logs vnc-proxy
```

**Log mong đợi khi iPhone kết nối:**
```
[VNC] New connection from XXX.XXX.XXX.XXX:XXXXX
[VNC] Device ID: XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX from XXX.XXX.XXX.XXX:XXXXX
[VNC] Stored connection for device: XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
```

#### Check Flask logs:

```bash
tail -f /path/to/flask.log
```

### Trên iPhone (kiểm tra logs)

```bash
ssh mobile@IPHONE_IP
tail -f /var/mobile/Library/Logs/TrollVNC/trollvncserver.log
```

**Log mong đợi:**
```
[TrollVNC] Reverse mode enabled: viewer -> serverapi.xyz:5500
[TrollVNC] Device ID sent to server: XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
[TrollVNC] Reverse connection established to serverapi.xyz
```

### Trên Web Browser

1. Mở: https://serverapi.xyz/monitor
2. Tìm device của bạn trong danh sách
3. Nếu **🟢 Bật**, click nút **📺 VNC Live**
4. Popup VNC viewer sẽ mở
5. Status nên hiển thị: **✅ Đã kết nối**

---

## ⚠️ PHẦN 4: TROUBLESHOOTING

### Vấn đề 1: iPhone không kết nối được

**Kiểm tra:**
```bash
# Trên iPhone, test ping
ping serverapi.xyz

# Test port
nc -zv serverapi.xyz 5500
```

**Giải pháp:**
- Kiểm tra firewall trên server
- Kiểm tra domain DNS
- Kiểm tra iPhone có internet

### Vấn đề 2: Node.js proxy không chạy

**Kiểm tra:**
```bash
# Check port đang lắng nghe
netstat -tulpn | grep 5500
netstat -tulpn | grep 8080

# Check process
ps aux | grep node
```

**Giải pháp:**
```bash
# Kill process cũ
killall node

# Start lại
pm2 restart vnc-proxy
```

### Vấn đề 3: Web không hiển thị device

**Kiểm tra:**
```bash
# Test API
curl http://localhost:3000/api/devices
```

**Nên trả về:**
```json
[
  {
    "deviceId": "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX",
    "status": "connected",
    "connectedAt": "2025-12-06T..."
  }
]
```

### Vấn đề 4: VNC viewer không hiển thị hình

**Lưu ý:** 
- Hiện tại code chỉ thiết lập WebSocket connection
- Để hiển thị hình ảnh VNC thực tế, cần tích hợp thư viện **noVNC**
- Xem file `web-client-example.html` để tham khảo cách tích hợp noVNC

**Tích hợp noVNC:**
1. Thêm vào `severapixyz.py`:
```html
<script src="https://novnc.com/noVNC/core/rfb.js"></script>
```

2. Sửa hàm `connectVNCWebSocket()` để dùng noVNC RFB client

---

## 📊 PHẦN 5: TỔNG KẾT

### ✅ ĐÃ HOÀN THÀNH

| Component | Status | Notes |
|-----------|--------|-------|
| `trollvncserver.mm` | ✅ | Đã có device ID + reverse connection |
| `Managed.plist` | ✅ | Cấu hình serverapi.xyz:5500 |
| `server-vnc-proxy.js` | ✅ | Hoàn chỉnh, sẵn sàng chạy |
| `severapixyz.py` | ✅ | Đã tích hợp VNC viewer UI |
| `package.json` | ✅ | Dependencies đã đủ |

### 🔄 CẦN LÀM TIẾP

1. **Trên Server:**
   - [ ] Chạy `npm install`
   - [ ] Start `server-vnc-proxy.js`
   - [ ] Mở firewall ports
   - [ ] (Optional) Tích hợp noVNC để hiển thị hình

2. **Build TrollVNC:**
   - [ ] `make package`
   - [ ] Copy file .deb

3. **Trên iPhone:**
   - [ ] Cài đặt .deb
   - [ ] Bật TrollVNC
   - [ ] Kiểm tra logs

### 🎉 KẾT QUẢ MONG ĐỢI

Sau khi hoàn thành các bước trên:

1. iPhone tự động kết nối đến `serverapi.xyz:5500`
2. Server nhận connection và lưu device ID
3. Truy cập https://serverapi.xyz/monitor sẽ thấy device hiển thị
4. Click "📺 VNC Live" sẽ mở VNC viewer
5. **Nếu đã tích hợp noVNC:** Thấy màn hình iPhone realtime
6. **Nếu chưa tích hợp noVNC:** Thấy "Đã kết nối" nhưng chưa có hình

---

## 📝 GHI CHÚ BẢO MẬT

- Nên dùng SSL/TLS cho WebSocket (wss://)
- Nên thêm authentication cho VNC connection
- Nên giới hạn rate limiting
- Nên log access để audit

---

## 🔗 FILES LIÊN QUAN

- `README-INTEGRATION.md` - Hướng dẫn tích hợp chi tiết
- `IP-CHANGE-HANDLING.md` - Giải thích cơ chế auto-reconnect
- `web-client-example.html` - Ví dụ tích hợp noVNC
- `server-vnc-proxy.js` - Source code proxy server
- `severapixyz.py` - Source code web UI

---

**Sẵn sàng build!** 🚀

Tất cả code đã được kiểm tra và sẵn sàng. Bạn có thể bắt đầu build TrollVNC ngay bây giờ!

