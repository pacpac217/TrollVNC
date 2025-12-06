# ⚡ QUICK START - BUILD VÀ DEPLOY TROLLVNC

## 🎯 MỤC TIÊU
Kết nối iPhone → serverapi.xyz → Xem trên web

---

## ✅ 1. KIỂM TRA NHANH

### iPhone Side ✅
- [x] `src/trollvncserver.mm` - Đã có code gửi device ID
- [x] `Managed.plist` - Đã cấu hình `serverapi.xyz:5500`

### Server Side ✅  
- [x] `server-vnc-proxy.js` - Proxy server sẵn sàng (port 5500, 8080)
- [x] `severapixyz.py` - Web UI đã có VNC viewer

**KẾT LUẬN: ✅ SẴN SÀNG BUILD!**

---

## 🚀 2. TRIỂN KHAI - 3 BƯỚC ĐƠN GIẢN

### BƯỚC 1: Trên Server (serverapi.xyz)

```bash
# Cài đặt dependencies
cd /path/to/TrollVNC-main
npm install

# Chạy VNC Proxy (chọn 1 trong 2)

# Option A: Test mode
node server-vnc-proxy.js &

# Option B: Production mode (khuyến nghị)
npm install -g pm2
pm2 start server-vnc-proxy.js --name vnc-proxy
pm2 save

# Mở firewall
sudo ufw allow 5500/tcp
sudo ufw allow 8080/tcp
```

**Kiểm tra:**
```bash
pm2 status  # Phải thấy "vnc-proxy | online"
netstat -tulpn | grep 5500  # Phải thấy port đang listen
```

---

### BƯỚC 2: Build TrollVNC (trên macOS)

```bash
cd /path/to/TrollVNC-main

# Clean + Build
make clean
make package THEOS_PACKAGE_SCHEME=rootless

# File output: packages/com.82flex.trollvnc_X.X.X_iphoneos-arm.deb
```

**Nếu lỗi Theos chưa cài:**
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/theos/theos/master/bin/install-theos)"
```

---

### BƯỚC 3: Cài trên iPhone

**Cách 1: TrollStore (dễ nhất)**
1. Copy file `.deb` lên iPhone (AirDrop/iCloud/...)
2. Mở **TrollStore**
3. Tap dấu `+` → Chọn file `.deb` → Install
4. Mở app **TrollVNC** → Settings → Bật **Enabled**

**Cách 2: SSH + dpkg**
```bash
scp packages/*.deb mobile@IPHONE_IP:/var/mobile/
ssh mobile@IPHONE_IP
sudo dpkg -i /var/mobile/*.deb
killall -9 SpringBoard
```

---

## 🔍 3. KIỂM TRA KẾT NỐI

### Trên Server - Xem logs:
```bash
pm2 logs vnc-proxy --lines 50
```

**Phải thấy:**
```
[VNC] New connection from XXX.XXX.XXX.XXX:XXXXX
[VNC] Device ID: XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
```

### Trên iPhone - Xem logs:
```bash
ssh mobile@IPHONE_IP
tail -f /var/mobile/Library/Logs/TrollVNC/trollvncserver.log
```

**Phải thấy:**
```
[TrollVNC] Device ID sent to server: XXXXXXXX-...
[TrollVNC] Reverse connection established
```

### Trên Web Browser:

1. Mở: **https://serverapi.xyz/monitor**
2. Thấy device trong danh sách (🟢 Bật)
3. Click nút **📺 VNC Live**
4. Popup mở → Status: **✅ Đã kết nối**

---

## ❌ 4. NẾU CÓ LỖI

### Lỗi: iPhone không kết nối được

```bash
# Trên iPhone test:
ping serverapi.xyz
nc -zv serverapi.xyz 5500

# Giải pháp:
# - Check firewall: sudo ufw status
# - Check proxy running: pm2 status
# - Check domain DNS
```

### Lỗi: Node.js proxy không chạy

```bash
# Check port:
netstat -tulpn | grep 5500

# Restart:
pm2 restart vnc-proxy
pm2 logs vnc-proxy
```

### Lỗi: Web không thấy device

```bash
# Test API:
curl http://localhost:3000/api/devices

# Giải pháp:
# - Restart proxy: pm2 restart vnc-proxy
# - Check iPhone logs
```

---

## 📌 5. THÔNG TIN QUAN TRỌNG

### Ports đang dùng:
- **5500** - VNC từ iPhone vào
- **8080** - WebSocket cho web client
- **5678** - Flask web UI (severapixyz.py)

### Files cấu hình:
- `prefs/TrollVNCPrefs/Resources/Managed.plist` - Cấu hình iPhone
- `server-vnc-proxy.js` - Proxy server settings
- `severapixyz.py` - Web UI

### Cơ chế hoạt động:
1. iPhone khởi động → Đọc `Managed.plist`
2. Kết nối reverse đến `serverapi.xyz:5500`
3. Gửi Device ID (32 bytes đầu tiên)
4. Proxy lưu connection theo Device ID
5. Web client kết nối WebSocket đến proxy
6. Proxy forward VNC data giữa iPhone ↔ Web

---

## 🎉 HOÀN TẤT!

Sau khi hoàn thành 3 bước trên, bạn có thể:
- ✅ Xem danh sách iPhone trên https://serverapi.xyz/monitor
- ✅ Click "📺 VNC Live" để view màn hình
- ✅ iPhone tự động reconnect khi đổi IP (4G)
- ✅ Hỗ trợ nhiều iPhone cùng lúc

---

**Lưu ý về hiển thị VNC:**
- Hiện tại: WebSocket đã kết nối nhưng chưa decode VNC protocol
- Để hiển thị hình ảnh: Cần tích hợp thư viện **noVNC**
- Xem file `web-client-example.html` để tham khảo

**Ready to build!** 🚀

