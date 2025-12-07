# 🔍 CÁCH NHẬN DIỆN IPHONE CỦA BẠN TRÊN WEB MONITOR

## 📱 Khi có nhiều thiết bị, làm sao biết đâu là iPhone của bạn?

---

## 🎯 CÁCH 1: XEM DESKTOP NAME (Dễ nhất)

### Trong Settings → TrollVNC:

1. **Mở Settings** trên iPhone
2. **Vào TrollVNC**
3. **Xem "Desktop Name"** (thường hiển thị ở đầu hoặc trong phần cấu hình)
4. **Desktop Name mặc định:** `My iPhone` hoặc tên bạn đã đặt

### Trên Web Monitor:

- **Desktop Name** sẽ hiển thị trong danh sách thiết bị
- Ví dụ: `My iPhone`, `iPhone 13 Pro`, `Device 30`, v.v.

---

## 🏷️ CÁCH 2: ĐỔI DESKTOP NAME ĐỂ DỄ NHẬN DIỆN

### Nếu không ở Managed Mode:

1. **Settings → TrollVNC**
2. **Tìm "Desktop Name"**
3. **Đổi thành tên dễ nhớ:**
   - `iPhone của Quang`
   - `iPhone 13 Pro - Quang`
   - `Device 30` (như số trên tape)
   - `iPhone - 3114` (như số trên màn hình)

### Nếu ở Managed Mode (cần rebuild):

1. **Sửa file:** `prefs/TrollVNCPrefs/Resources/Managed.plist`
2. **Tìm dòng:**
   ```xml
   <key>DesktopName</key>
   <string>My iPhone</string>
   ```
3. **Đổi thành:**
   ```xml
   <key>DesktopName</key>
   <string>iPhone của Quang</string>
   ```
4. **Rebuild và reinstall**

---

## 📍 CÁCH 3: XEM IP ADDRESS CỦA IPHONE

### Trên iPhone:

1. **Settings → Wi-Fi**
2. **Tap vào mạng Wi-Fi đang kết nối** (có dấu ✅)
3. **Xem "IP Address"** (ví dụ: `192.168.1.100`)

### Trên Web Monitor:

- **IP Address** sẽ hiển thị trong thông tin thiết bị
- So sánh với IP trên iPhone để xác định

---

## 🔢 CÁCH 4: DÙNG SỐ TRÊN TAPE (Như hình bạn gửi)

Bạn có **số "30"** trên tape ở góc trên iPhone:

1. **Đổi Desktop Name thành:** `Device 30` hoặc `iPhone 30`
2. **Hoặc thêm số vào tên:** `My iPhone - 30`

### Cách đổi (nếu không managed):

1. **Settings → TrollVNC**
2. **Desktop Name → Đổi thành:** `Device 30`

---

## 🌐 CÁCH 5: KIỂM TRA TRÊN WEB MONITOR

### Khi vào https://serverapi.xyz/monitor:

1. **Xem danh sách thiết bị**
2. **Mỗi thiết bị sẽ hiển thị:**
   - **Desktop Name** (tên thiết bị)
   - **IP Address** (địa chỉ IP)
   - **Port** (thường là 5901)
   - **Status** (Online/Offline)
   - **Last Seen** (thời gian kết nối cuối)

3. **So sánh với thông tin iPhone của bạn:**
   - Desktop Name
   - IP Address
   - Thời gian kết nối (Last Seen)

---

## 🔧 CÁCH 6: XEM THÔNG TIN CHI TIẾT (SSH/Terminal)

### Xem thông tin device:

```bash
# SSH vào iPhone
ssh root@[IPHONE_IP]

# Xem Desktop Name hiện tại
defaults read /var/mobile/Library/Preferences/com.82flex.trollvnc.plist DesktopName

# Xem IP address
ifconfig | grep "inet " | grep -v 127.0.0.1

# Xem thông tin device
uname -a
```

### Xem log để biết device info:

```bash
# Xem log TrollVNC
tail -20 /var/log/trollvnc.log | grep -i "desktop\|name\|ip"
```

---

## 💡 GỢI Ý: ĐẶT TÊN DỄ NHẬN DIỆN

### Ví dụ tên hay:

- `iPhone 30` (theo số trên tape)
- `iPhone - 3114` (theo số trên màn hình)
- `Quang's iPhone`
- `iPhone 13 Pro - Quang`
- `Device 30 - VinaPhone`

### Cách đổi nhanh (nếu không managed):

1. **Settings → TrollVNC**
2. **Desktop Name**
3. **Gõ tên mới:** `Device 30`
4. **Respring hoặc restart TrollVNC**

---

## 🎯 TÓM TẮT

**Để nhận diện iPhone của bạn:**

1. ✅ **Xem Desktop Name** trong Settings → TrollVNC
2. ✅ **Đổi Desktop Name** thành tên dễ nhớ (ví dụ: `Device 30`)
3. ✅ **Xem IP Address** trong Settings → Wi-Fi
4. ✅ **So sánh trên web monitor:**
   - Desktop Name
   - IP Address
   - Thời gian kết nối

**Nếu có nhiều thiết bị:**
- Đặt tên khác nhau cho mỗi device
- Dùng số hoặc tên người dùng để phân biệt
- Xem IP address để xác định chính xác

---

## 🚀 BƯỚC TIẾP THEO

1. **Đổi Desktop Name** thành `Device 30` (hoặc tên bạn muốn)
2. **Respring iPhone**
3. **Vào web monitor:** https://serverapi.xyz/monitor
4. **Tìm thiết bị có tên "Device 30"**
5. **Click vào để xem màn hình!**

---

🎉 **Chúc bạn thành công!**

