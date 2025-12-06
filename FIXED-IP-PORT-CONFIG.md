# 🔧 CẤU HÌNH IP VÀ PORT CỐ ĐỊNH CHO NHIỀU THIẾT BỊ

## 🎯 Mục tiêu

- ✅ **Tắt Reverse Connection** (không dùng serverapi.xyz nữa)
- ✅ **Dùng Direct Connection** với IP và Port cố định
- ✅ **Mỗi thiết bị có Port riêng** (5901, 5902, 5903...)
- ✅ **Dễ quản lý hơn 100 thiết bị**

---

## 📝 BƯỚC 1: SỬA FILE Managed.plist

### File cần sửa:
```
prefs/TrollVNCPrefs/Resources/Managed.plist
```

### Cấu hình mới (Đã được sửa):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <!-- Enable TrollVNC -->
    <key>Enabled</key>
    <true/>
    
    <!-- Desktop Name - Đổi thành số thiết bị hoặc tên dễ nhận diện -->
    <key>DesktopName</key>
    <string>Device 30</string>
    
    <!-- Direct Connection Configuration (No Reverse) -->
    <!-- Port: Fixed port for direct VNC connection -->
    <!-- Mỗi thiết bị dùng port khác nhau: 5901, 5902, 5903... -->
    <key>Port</key>
    <integer>5901</integer>
    
    <!-- Tắt Reverse Connection -->
    <!-- Comment out hoặc xóa các dòng này: -->
    <!-- <key>ReverseMode</key> -->
    <!-- <string>viewer</string> -->
    <!-- <key>ReverseSocket</key> -->
    <!-- <string>serverapi.xyz:5500</string> -->
    
    <!-- Performance Settings -->
    <key>Scale</key>
    <real>0.75</real>
    
    <key>FrameRateSpec</key>
    <string>30:60:120</string>
    
    <!-- Clipboard Sync -->
    <key>ClipboardEnabled</key>
    <true/>
    
    <!-- Keep Alive -->
    <key>KeepAliveSec</key>
    <integer>60</integer>
</dict>
</plist>
```

---

## 🔢 BƯỚC 2: PHÂN BỔ PORT CHO TỪNG THIẾT BỊ

### Quy tắc phân bổ Port:

- **Device 1:** Port `5901`
- **Device 2:** Port `5902`
- **Device 3:** Port `5903`
- ...
- **Device 30:** Port `5930`
- ...
- **Device 100:** Port `6000`

### Công thức:
```
Port = 5900 + Device_Number
```

Ví dụ:
- Device 30 → Port `5930`
- Device 100 → Port `6000`

---

## 📋 BƯỚC 3: TẠO TEMPLATE CHO NHIỀU THIẾT BỊ

### Cách 1: Tạo script tự động (Khuyên dùng)

Tạo file `generate-device-config.sh`:

```bash
#!/bin/bash

# Usage: ./generate-device-config.sh <device_number> <device_name>
# Example: ./generate-device-config.sh 30 "Device 30"

DEVICE_NUM=$1
DEVICE_NAME=$2
PORT=$((5900 + DEVICE_NUM))

cat > "prefs/TrollVNCPrefs/Resources/Managed-Device${DEVICE_NUM}.plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Enabled</key>
    <true/>
    
    <key>DesktopName</key>
    <string>${DEVICE_NAME}</string>
    
    <key>Port</key>
    <integer>${PORT}</integer>
    
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
EOF

echo "✅ Created config for Device ${DEVICE_NUM}: Port ${PORT}, Name: ${DEVICE_NAME}"
```

### Cách 2: Sửa thủ công từng file

1. **Copy** `Managed.plist` thành `Managed-Device30.plist`
2. **Sửa Port:** `5901` → `5930`
3. **Sửa DesktopName:** `My iPhone` → `Device 30`
4. **Lặp lại** cho từng thiết bị

---

## 🏗️ BƯỚC 4: BUILD PACKAGE CHO TỪNG THIẾT BỊ

### Option A: Build riêng từng package (Khuyên dùng)

1. **Sửa Managed.plist** với Port và DesktopName cho thiết bị
2. **Build package:**
   ```bash
   make package THEOS_PACKAGE_SCHEME=roothide FINALPACKAGE=1
   ```
3. **Rename package:**
   ```bash
   mv packages/*.deb packages/TrollVNC-Device30-Port5930.deb
   ```
4. **Lặp lại** cho từng thiết bị

### Option B: Build một lần, cấu hình sau khi cài

1. **Build package chung** (không có Managed.plist hoặc có template)
2. **Sau khi cài**, SSH vào từng iPhone
3. **Tạo file cấu hình:**
   ```bash
   # Trên iPhone
   cat > /var/mobile/Library/Preferences/com.82flex.trollvnc.plist <<EOF
   <?xml version="1.0" encoding="UTF-8"?>
   <plist version="1.0">
   <dict>
       <key>Port</key>
       <integer>5930</integer>
       <key>DesktopName</key>
       <string>Device 30</string>
   </dict>
   </plist>
   EOF
   ```
4. **Restart TrollVNC:**
   ```bash
   launchctl unload /Library/LaunchDaemons/com.82flex.trollvnc.plist
   launchctl load -w /Library/LaunchDaemons/com.82flex.trollvnc.plist
   ```

---

## 🌐 BƯỚC 5: KẾT NỐI TỪ VNC CLIENT

### Với IP và Port cố định:

1. **Lấy IP của iPhone:**
   - Settings → Wi-Fi → Tap vào mạng → Xem IP Address
   - Ví dụ: `192.168.1.100`

2. **Kết nối từ VNC Client:**
   - **Address:** `192.168.1.100:5930` (IP:Port)
   - **Password:** (không cần mặc định)

3. **Hoặc từ Web Browser:**
   - Nếu có HTTP server: `http://192.168.1.100:5801`
   - (Cần enable HttpPort trong Managed.plist)

---

## 📊 BƯỚC 6: QUẢN LÝ NHIỀU THIẾT BỊ

### Tạo bảng quản lý:

| Device # | Desktop Name | Port | IP Address | Status |
|----------|--------------|------|------------|--------|
| 1 | Device 1 | 5901 | 192.168.1.101 | ✅ |
| 2 | Device 2 | 5902 | 192.168.1.102 | ✅ |
| ... | ... | ... | ... | ... |
| 30 | Device 30 | 5930 | 192.168.1.130 | ✅ |
| ... | ... | ... | ... | ... |
| 100 | Device 100 | 6000 | 192.168.1.200 | ✅ |

### Script kiểm tra tất cả thiết bị:

```bash
#!/bin/bash
# check-all-devices.sh

for i in {1..100}; do
    PORT=$((5900 + i))
    IP="192.168.1.$((100 + i))"
    
    # Kiểm tra port có đang listen không
    if nc -z -w1 $IP $PORT 2>/dev/null; then
        echo "✅ Device $i: $IP:$PORT - ONLINE"
    else
        echo "❌ Device $i: $IP:$PORT - OFFLINE"
    fi
done
```

---

## 🔒 BƯỚC 7: BẢO MẬT (Tùy chọn)

### Thêm Password:

Trong `Managed.plist`, thêm:

```xml
<key>FullPassword</key>
<string>your_password_here</string>

<key>ViewOnlyPassword</key>
<string>viewonly_password</string>
```

### Giới hạn IP kết nối:

Cần cấu hình firewall trên router hoặc dùng VPN.

---

## 🎯 TÓM TẮT

### Đã sửa trong Managed.plist:

1. ✅ **Tắt Reverse Connection** (comment out ReverseMode/ReverseSocket)
2. ✅ **Thêm Port cố định** (5901, hoặc port khác cho từng device)
3. ✅ **Đổi DesktopName** để dễ nhận diện

### Các bước tiếp theo:

1. **Rebuild package** với cấu hình mới
2. **Reinstall** trên iPhone
3. **Kết nối bằng:** `[IP_ADDRESS]:[PORT]`
4. **Lặp lại** cho từng thiết bị với port khác nhau

---

## 📝 LƯU Ý

- **Port range:** 1024-65535 (không dùng port < 1024)
- **Mỗi thiết bị cần port riêng** để tránh conflict
- **IP có thể thay đổi** (DHCP), nhưng port cố định
- **Nếu IP thay đổi:** Cần update bảng quản lý hoặc dùng static IP

---

## 🚀 SẴN SÀNG!

File `Managed.plist` đã được sửa để dùng Direct Connection với Port cố định. Bây giờ bạn có thể:

1. **Rebuild package**
2. **Cấu hình port khác nhau cho từng thiết bị**
3. **Kết nối trực tiếp bằng IP:Port**

🎉 **Chúc bạn quản lý 100+ thiết bị thành công!**

