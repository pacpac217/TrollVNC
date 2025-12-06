# ✅ CHECKLIST TRƯỚC KHI BUILD TROLLVNC

## 📋 Tổng quan

Checklist này giúp bạn đảm bảo mọi thứ đã sẵn sàng trước khi build TrollVNC để kết nối với serverapi.xyz.

---

## ✅ 1. KIỂM TRA FILES ĐÃ CHỈNH SỬA

### iPhone Side (TrollVNC Source Code)

- ✅ **`src/trollvncserver.mm`**
  - [x] Đã import `UIKit/UIDevice.h` (line 24)
  - [x] Đã thêm code lấy device ID từ `identifierForVendor` (line 4723-4727)
  - [x] Đã thêm code gửi device ID qua socket (line 4734-4751)
  - [x] Đã có logic auto-reconnect với watchdog

- ✅ **`prefs/TrollVNCPrefs/Resources/Managed.plist`**
  - [x] File đã được tạo từ `Managed.plist.example`
  - [x] `ReverseSocket` = `serverapi.xyz:5500`
  - [x] `ReverseMode` = `viewer`
  - [x] `Enabled` = `true`

### Server Side (serverapi.xyz)

- ✅ **`severapixyz.py`** (Flask Web UI)
  - [x] Đã thêm VNC viewer modal UI
  - [x] Đã thêm CSS cho VNC viewer
  - [x] Đã thêm JavaScript để kết nối WebSocket
  - [x] Đã thêm nút "📺 VNC Live" cho mỗi device online

- ✅ **`server-vnc-proxy.js`** (Node.js VNC Proxy)
  - [x] Lắng nghe port 5500 cho VNC từ iPhone
  - [x] WebSocket port 8080 cho web client
  - [x] HTTP API port 3000
  - [x] Đã có logic đọc device ID từ 32 bytes đầu
  - [x] Đã có logic auto-reconnect khi IP thay đổi

---

## 🚀 2. CÁC BƯỚC TIẾP THEO

### Trên Server (serverapi.xyz)

#### Bước 1: Cài đặt Node.js dependencies

```bash
cd /path/to/TrollVNC-main
npm install ws
```

#### Bước 2: Chạy VNC Proxy Server

**Option A: Chạy trực tiếp (test)**
```bash
node server-vnc-proxy.js
```

**Option B: Chạy với PM2 (production)**
```bash
npm install -g pm2
pm2 start server-vnc-proxy.js --name vnc-proxy
pm2 save
pm2 startup  # Tự động khởi động khi reboot
```

#### Bước 3: Mở Firewall Ports

```bash
# Ubuntu/Debian
sudo ufw allow 5500/tcp   # VNC từ iPhone
sudo ufw allow 8080/tcp   # WebSocket cho web client
sudo ufw allow 3000/tcp   # HTTP API (optional)

# hoặc CentOS/RHEL
sudo firewall-cmd --permanent --add-port=5500/tcp
sudo firewall-cmd --permanent --add-port=8080/tcp
sudo firewall-cmd --permanent --add-port=3000/tcp
sudo firewall-cmd --reload
```

#### Bước 4: Chạy Flask Server (nếu chưa chạy)

```bash
python3 severapixyz.py
```

Hoặc với gunicorn:
```bash
pip3 install gunicorn
gunicorn -w 4 -b 0.0.0.0:5678 severapixyz:app
```

### Trên iPhone

#### Bước 5: Build TrollVNC

**Trên macOS với Theos:**

```bash
cd /path/to/TrollVNC-main

# Build cho rootless (iOS 15+)
make package THEOS_PACKAGE_SCHEME=rootless

# Hoặc build cho roothide
make package THEOS_PACKAGE_SCHEME=roothide

# Hoặc build standard
make package
```

File output: `packages/com.82flex.trollvnc_*.deb`

#### Bước 6: Cài đặt trên iPhone

**Option A: Qua TrollStore**
1. Copy file `.deb` vào iPhone (AirDrop, iCloud, etc.)
2. Mở TrollStore
3. Tap vào file `.deb` để cài đặt

**Option B: Qua Sileo/Zebra**
1. Copy file `.deb` vào `/var/mobile/Documents/`
2. Mở Sileo/Zebra
3. Cài đặt từ file local

**Option C: Qua SSH/Filza**
```bash
# SSH vào iPhone
scp packages/*.deb mobile@iphone-ip:/var/mobile/Documents/
ssh mobile@iphone-ip
cd /var/mobile/Documents/
dpkg -i *.deb
uicache -p /Applications/TrollVNC.app
```

#### Bước 7: Khởi động TrollVNC trên iPhone

1. Mở app **TrollVNC** trên iPhone
2. App sẽ tự động kết nối reverse đến `serverapi.xyz:5500`
3. Check notification để xem trạng thái kết nối

---

## 🧪 3. KIỂM TRA KẾT NỐI

### A. Kiểm tra Server Logs

**VNC Proxy Server:**
```bash
# Nếu chạy với PM2
pm2 logs vnc-proxy

# Hoặc check console nếu chạy trực tiếp
# Bạn sẽ thấy:
# [VNC] New connection from <iPhone-IP>:<port>
# [VNC] Device ID: <UUID>
```

### B. Kiểm tra Web UI

1. Truy cập: https://serverapi.xyz/monitor
2. Bạn sẽ thấy:
   - 📱 Tổng: 1 (hoặc nhiều hơn nếu có nhiều iPhone)
   - 🟢 Bật: 1
   - Nút **"📺 VNC Live"** xuất hiện trên device card

### C. Test VNC Viewer

1. Click nút **"📺 VNC Live"**
2. Modal VNC viewer sẽ mở
3. Trạng thái sẽ hiển thị: "✅ Đã kết nối"
4. Màn hình iPhone sẽ hiển thị (nếu tích hợp noVNC thành công)

---

## 🔧 4. TROUBLESHOOTING

### iPhone không kết nối được

**Check 1: iPhone có kết nối internet không?**
```bash
# Trên iPhone, mở Safari và test
# Hoặc ping từ iPhone
ping serverapi.xyz
```

**Check 2: Server có mở port 5500 không?**
```bash
# Trên server
netstat -tulpn | grep 5500
# Hoặc
ss -tulpn | grep 5500
```

**Check 3: Firewall có block không?**
```bash
# Test từ iPhone bằng telnet
telnet serverapi.xyz 5500
```

**Check 4: TrollVNC logs trên iPhone**
```bash
# SSH vào iPhone
ssh mobile@iphone-ip
cat /var/mobile/Library/Preferences/com.82flex.trollvnc.log
# Hoặc check Console.app trên Mac
```

### Web UI không hiển thị VNC

**Check 1: WebSocket có chạy không?**
```bash
# Trên server
netstat -tulpn | grep 8080
```

**Check 2: Browser console có lỗi không?**
- Mở Chrome DevTools (F12)
- Tab "Console" sẽ hiển thị lỗi WebSocket nếu có

**Check 3: Mixed content issue (HTTP/HTTPS)**
- Nếu web dùng HTTPS nhưng WebSocket dùng WS (không SSL)
- Cần đổi sang WSS (WebSocket Secure)
- Hoặc chạy web UI qua HTTP thay vì HTTPS

---

## 📝 5. TÓM TẮT CẤU HÌNH

### Ports cần mở:

| Port | Protocol | Mục đích | Kết nối từ |
|------|----------|----------|------------|
| 5500 | TCP | VNC từ iPhone | iPhone (4G/WiFi) |
| 8080 | TCP/WS | WebSocket viewer | Browser |
| 3000 | TCP/HTTP | API (optional) | Browser |
| 5678 | TCP/HTTP | Flask UI | Browser |

### File paths quan trọng:

```
TrollVNC-main/
├── src/trollvncserver.mm                           # Core VNC server (ĐÃ SỬA)
├── prefs/TrollVNCPrefs/Resources/Managed.plist     # Config cho iPhone (ĐÃ TẠO)
├── server-vnc-proxy.js                             # Node.js proxy (ĐÃ TẠO)
├── severapixyz.py                                  # Flask web UI (ĐÃ SỬA)
└── packages/*.deb                                  # Build output (SẼ TẠO)
```

### Environment:

- **Server**: Linux (Ubuntu/Debian/CentOS)
- **Domain**: serverapi.xyz
- **iPhone**: iOS 14+ với TrollStore/jailbreak
- **Build machine**: macOS với Theos installed

---

## ✨ 6. TÍNH NĂNG ĐÃ TÍCH HỢP

✅ **Reverse Connection**: iPhone tự kết nối ra server, không cần biết IP trước

✅ **Auto-reconnect**: Khi iPhone đổi IP (4G), sẽ tự động kết nối lại

✅ **Device Identification**: Mỗi iPhone có UUID riêng để phân biệt

✅ **Web UI**: Giao diện đẹp để xem tất cả iPhone

✅ **VNC Live View**: Click nút để xem màn hình real-time

✅ **Multi-device**: Hỗ trợ nhiều iPhone cùng lúc

---

## 🎯 READY TO BUILD!

Nếu tất cả checklist trên đều ✅, bạn đã sẵn sàng để:

```bash
make package
```

Sau khi build xong, cài file `.deb` lên iPhone và enjoy! 🎉

