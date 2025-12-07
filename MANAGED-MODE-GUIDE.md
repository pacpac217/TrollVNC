# 🔒 HƯỚNG DẪN SỬ DỤNG TROLLVNC Ở CHẾ ĐỘ MANAGED

## ✅ TrollVNC đang ở chế độ Managed!

Khi thấy thông báo **"This TrollVNC instance is managed by your organization"**, nghĩa là:
- ✅ TrollVNC đã được cấu hình sẵn qua `Managed.plist`
- ✅ Đã có `Enabled: true` trong cấu hình
- ✅ **KHÔNG CẦN** toggle switch trong Settings
- ✅ TrollVNC sẽ tự động chạy khi iPhone khởi động

---

## 🚀 KÍCH HOẠT TROLLVNC (Nếu chưa chạy)

### Cách 1: Kiểm tra và Restart Service (SSH/Terminal)

1. **SSH vào iPhone:**
   ```bash
   ssh root@[IPHONE_IP]
   ```

2. **Kiểm tra trạng thái:**
   ```bash
   # Xem process có đang chạy không
   ps aux | grep trollvncserver
   
   # Xem log
   tail -f /var/log/trollvnc.log
   ```

3. **Nếu chưa chạy, khởi động service:**
   ```bash
   # Load service
   launchctl load -w /Library/LaunchDaemons/com.82flex.trollvnc.plist
   
   # Hoặc restart
   launchctl unload /Library/LaunchDaemons/com.82flex.trollvnc.plist
   launchctl load -w /Library/LaunchDaemons/com.82flex.trollvnc.plist
   ```

### Cách 2: Respring iPhone

1. **Mở Terminal/SSH:**
   ```bash
   killall -9 SpringBoard
   ```

2. **Hoặc dùng tweak như PowerModule** để respring

### Cách 3: Reboot và Rejailbreak

1. **Reboot iPhone**
2. **Mở Dopamine** và **Rejailbreak**
3. **TrollVNC sẽ tự động khởi động** theo Managed.plist

---

## 🌐 KIỂM TRA KẾT NỐI

### 1. Xem trên Web

1. **Mở trình duyệt:**
   ```
   https://serverapi.xyz/monitor
   ```

2. **Kiểm tra xem iPhone có trong danh sách không**

### 2. Kiểm tra qua Terminal

```bash
# Xem port 5901 có đang listen không
netstat -an | grep 5901

# Hoặc
lsof -i :5901
```

### 3. Kiểm tra Log

```bash
# Xem log real-time
tail -f /var/log/trollvnc.log

# Xem log gần đây
tail -n 50 /var/log/trollvnc.log
```

---

## ⚙️ CẤU HÌNH HIỆN TẠI (Từ Managed.plist)

Theo file `Managed.plist` đã được build vào package:

- ✅ **Enabled:** `true` (Tự động bật)
- ✅ **Reverse Connection:** `serverapi.xyz:5500`
- ✅ **Mode:** `viewer` (Direct reverse)
- ✅ **Desktop Name:** `My iPhone`
- ✅ **Clipboard:** Enabled
- ✅ **Scale:** 0.75 (75% resolution)
- ✅ **Frame Rate:** 30:60:120

---

## 🔧 THAY ĐỔI CẤU HÌNH (Nếu cần)

### Cách 1: Sửa Managed.plist (Cần rebuild)

1. **Sửa file:** `prefs/TrollVNCPrefs/Resources/Managed.plist`
2. **Rebuild package**
3. **Reinstall trên iPhone**

### Cách 2: Override qua Terminal (Tạm thời)

```bash
# Chạy trollvncserver với options tùy chỉnh
trollvncserver -port 5901 -reverse serverapi.xyz:5500
```

---

## ❓ TROUBLESHOOTING

### TrollVNC không tự động chạy?

**Giải pháp:**
```bash
# Kiểm tra LaunchDaemon
ls -la /Library/LaunchDaemons/com.82flex.trollvnc.plist

# Load service thủ công
launchctl load -w /Library/LaunchDaemons/com.82flex.trollvnc.plist

# Kiểm tra log
tail -f /var/log/trollvnc.log
```

### Không thấy iPhone trên web?

**Kiểm tra:**
1. Internet trên iPhone có hoạt động không?
2. Reverse connection có đúng không?
3. Xem log để debug:
   ```bash
   tail -f /var/log/trollvnc.log
   ```

### Service bị crash?

**Giải pháp:**
```bash
# Xem crash log
cat /var/log/trollvnc.log | grep -i error

# Restart service
launchctl unload /Library/LaunchDaemons/com.82flex.trollvnc.plist
launchctl load -w /Library/LaunchDaemons/com.82flex.trollvnc.plist
```

---

## 📊 KIỂM TRA TRẠNG THÁI

### Xem thông tin chi tiết:

```bash
# Xem process
ps aux | grep trollvnc

# Xem port
netstat -an | grep 5901

# Xem log
tail -20 /var/log/trollvnc.log

# Xem LaunchDaemon status
launchctl list | grep trollvnc
```

---

## 🎯 TÓM TẮT

**Trong Managed Mode:**
- ✅ TrollVNC **TỰ ĐỘNG BẬT** theo Managed.plist
- ✅ **KHÔNG CẦN** toggle switch trong Settings
- ✅ Settings UI bị **lock down** (chỉ xem, không sửa được)
- ✅ Cấu hình đã được **set sẵn** trong build

**Nếu TrollVNC chưa chạy:**
1. Respring: `killall -9 SpringBoard`
2. Hoặc restart service qua SSH
3. Hoặc reboot và rejailbreak

**Kiểm tra:**
- Web: https://serverapi.xyz/monitor
- Log: `tail -f /var/log/trollvnc.log`
- Process: `ps aux | grep trollvnc`

---

## 🎉 XONG!

TrollVNC đã được cấu hình sẵn và sẽ tự động chạy. Chỉ cần kiểm tra xem nó đã kết nối đến server chưa!

🚀 **Enjoy!**

