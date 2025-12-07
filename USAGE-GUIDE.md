# 📱 HƯỚNG DẪN SỬ DỤNG TROLLVNC

## ✅ TrollVNC đã được cài đặt thành công!

Bạn đã thấy TrollVNC trong Sileo với version **2.7**. Bây giờ hãy kích hoạt và sử dụng!

---

## 🚀 BƯỚC 1: KÍCH HOẠT TROLLVNC

### Cách 1: Qua Settings (Khuyên dùng)

1. **Mở Settings** trên iPhone
2. **Cuộn xuống** tìm **"TrollVNC"** (thường ở cuối danh sách)
3. **Tap vào "TrollVNC"**
4. **Bật toggle "Enable TrollVNC"** hoặc **"TrollVNC Enabled"**
5. **Respring** nếu được yêu cầu (hoặc tự động)

### Cách 2: Qua Terminal (SSH)

```bash
# SSH vào iPhone
ssh root@[IPHONE_IP]

# Kích hoạt TrollVNC
launchctl load -w /Library/LaunchDaemons/com.82flex.trollvnc.plist

# Kiểm tra trạng thái
launchctl list | grep trollvnc
```

---

## 🌐 BƯỚC 2: XEM MÀN HÌNH IPHONE TRÊN WEB

### Truy cập Web Interface

1. **Mở trình duyệt** (Chrome, Safari, Firefox...)
2. **Vào địa chỉ:**
   ```
   https://serverapi.xyz/monitor
   ```
3. **Bạn sẽ thấy danh sách các thiết bị đã kết nối**
4. **Click vào iPhone của bạn** để xem màn hình

### Tính năng Web Interface

- ✅ **Xem màn hình iPhone real-time**
- ✅ **Điều khiển chuột/touch**
- ✅ **Bàn phím ảo**
- ✅ **Xem nhiều thiết bị cùng lúc**

---

## 🎮 BƯỚC 3: SỬ DỤNG VNC CLIENT (Tùy chọn)

Nếu muốn dùng VNC client thay vì web:

### Trên máy tính:

1. **Tải VNC Viewer:**
   - Windows: https://www.realvnc.com/en/connect/download/viewer/
   - Mac: App Store → "VNC Viewer"
   - Linux: `sudo apt install tigervnc-viewer`

2. **Kết nối:**
   - **Address:** `[IPHONE_IP]:5901`
   - **Password:** (không cần password mặc định)

### Trên điện thoại khác:

1. **Tải VNC Viewer** từ App Store/Play Store
2. **Kết nối:** `[IPHONE_IP]:5901`

---

## ⚙️ BƯỚC 4: CẤU HÌNH NÂNG CAO

### Trong Settings → TrollVNC:

#### 1. **Port Settings**
- **Default Port:** 5901
- Có thể đổi nếu port bị conflict

#### 2. **Clipboard Sync**
- **Enable Clipboard:** Bật/tắt đồng bộ clipboard
- Cho phép copy/paste giữa iPhone và máy tính

#### 3. **Desktop Name**
- **Desktop Name:** Tên hiển thị trong VNC client
- Mặc định: "TrollVNC"

#### 4. **Reverse Connection**
- **Auto-connect:** Tự động kết nối đến serverapi.xyz
- Đã được cấu hình sẵn trong Managed.plist

#### 5. **Performance Settings**
- **Frame Rate:** Điều chỉnh FPS (0 = auto)
- **Scale:** Điều chỉnh độ phân giải (0.0 - 1.0)

---

## 🔧 CÁC LỆNH HỮU ÍCH

### Kiểm tra trạng thái:

```bash
# Xem log
tail -f /var/log/trollvnc.log

# Kiểm tra process
ps aux | grep trollvncserver

# Kiểm tra port
netstat -an | grep 5901
```

### Restart TrollVNC:

```bash
# Qua Terminal
launchctl unload /Library/LaunchDaemons/com.82flex.trollvnc.plist
launchctl load -w /Library/LaunchDaemons/com.82flex.trollvnc.plist

# Hoặc qua Settings → TrollVNC → Toggle Off/On
```

### Xem thông tin kết nối:

```bash
# Xem clients đang kết nối
trollvncserver --status
```

---

## 🎯 CÁC TÍNH NĂNG CHÍNH

### ✅ Đã được cấu hình sẵn:

1. **Reverse Connection**
   - Tự động kết nối đến `serverapi.xyz:5500`
   - Không cần port forwarding
   - Xem từ bất kỳ đâu qua web

2. **Screen Capture**
   - Real-time screen sharing
   - Hỗ trợ nhiều độ phân giải
   - Tối ưu bandwidth

3. **Input Control**
   - Touch/mouse control
   - Keyboard input
   - Multi-touch gestures

4. **Clipboard Sync**
   - Copy/paste giữa devices
   - Two-way sync

---

## ❓ TROUBLESHOOTING

### TrollVNC không hiện trong Settings?

**Giải pháp:**
```bash
# Respring
killall -9 SpringBoard

# Hoặc reboot và rejailbreak
```

### Không kết nối được đến server?

**Kiểm tra:**
1. Internet trên iPhone có hoạt động không?
2. TrollVNC đã được bật trong Settings chưa?
3. Xem log: `tail -f /var/log/trollvnc.log`

### Màn hình bị lag?

**Giải pháp:**
1. Settings → TrollVNC → Giảm Frame Rate
2. Giảm Scale (ví dụ: 0.75)
3. Kiểm tra kết nối internet

### Không thấy iPhone trên web?

**Kiểm tra:**
1. Reverse connection đã được enable chưa?
2. File `Managed.plist` có đúng cấu hình không?
3. Xem log để debug

---

## 📊 MONITORING

### Xem thống kê:

```bash
# Xem số clients đang kết nối
trollvncserver --clients

# Xem thông tin chi tiết
trollvncserver --info
```

### Web Dashboard:

- **URL:** https://serverapi.xyz/monitor
- Xem tất cả thiết bị đã kết nối
- Thống kê real-time

---

## 🎉 TIPS & TRICKS

1. **Pin Settings Icon:**
   - Settings → TrollVNC → Pin để dễ truy cập

2. **Quick Toggle:**
   - Dùng Control Center shortcut (nếu có)

3. **Multiple Devices:**
   - Có thể kết nối nhiều iPhone cùng lúc
   - Mỗi device có port riêng

4. **Security:**
   - Chỉ bật khi cần dùng
   - Tắt khi không dùng để tiết kiệm pin

---

## 📞 HỖ TRỢ

Nếu gặp vấn đề:
1. Xem log: `/var/log/trollvnc.log`
2. GitHub Issues: https://github.com/pacpac217/TrollVNC/issues
3. Kiểm tra README: https://github.com/pacpac217/TrollVNC

---

## 🎊 CHÚC BẠN SỬ DỤNG VUI VẺ!

TrollVNC giờ đã sẵn sàng! Bạn có thể:
- ✅ Xem màn hình iPhone từ máy tính
- ✅ Điều khiển iPhone từ xa
- ✅ Copy/paste giữa devices
- ✅ Monitor nhiều thiết bị cùng lúc

🚀 **Enjoy!**

