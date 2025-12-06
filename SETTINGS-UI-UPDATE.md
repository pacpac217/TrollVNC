# 📱 Cập Nhật Settings UI - TrollVNC

## ✅ Đã Cải Thiện

### 1. **Desktop Name Field**
- ✅ Thêm placeholder: `Device-10` (ví dụ rõ ràng)
- ✅ Cải thiện footerText: Hướng dẫn format và mục đích
- ✅ Giải thích: Desktop Name sẽ được dùng làm Device ID

**Trước:**
```
Name shown to VNC clients.
```

**Sau:**
```
Name shown to VNC clients. This will be used as Device ID to identify your device on the server. Format: "Device-10", "Device-30", etc. (must match your device number).
```

### 2. **Reverse Connection - Server Field**
- ✅ Đổi label: `Server` → `Server (IP:Port)` (rõ ràng hơn)
- ✅ Cải thiện placeholder: `server:port` → `serverapi.xyz:10010` (ví dụ cụ thể)
- ✅ Thêm keyboardType: `URL` (bàn phím phù hợp cho IP:port)
- ✅ Cải thiện footerText: Hướng dẫn công thức port

**Trước:**
```
Server
Placeholder: server:port
```

**Sau:**
```
Server (IP:Port)
Placeholder: serverapi.xyz:10010
Keyboard: URL
```

### 3. **Reverse Connection - Footer Text**
- ✅ Thêm hướng dẫn công thức port: `Port = 10001 + Device_Number - 1`
- ✅ Ví dụ cụ thể: `serverapi.xyz:10010`

**Trước:**
```
Establish a reverse connection to a listening VNC viewer or repeater without opening a server port. This is useful for bypassing firewalls or NAT.
```

**Sau:**
```
Establish a reverse connection to a listening VNC viewer or repeater without opening a server port. This is useful for bypassing firewalls or NAT. Enter server IP and port in format: "serverapi.xyz:10010" (Port = 10001 + Device_Number - 1).
```

## 📱 Cách Sử Dụng Trên iPhone

### Bước 1: Mở Settings
1. Settings → **TrollVNC**

### Bước 2: Cấu hình Desktop Name
1. Tìm **Desktop Name**
2. Nhập: `Device-10` (thay số theo device của bạn)
3. Format: `Device-XX` (XX = số device)

### Bước 3: Cấu hình Reverse Connection
1. Tìm **Reverse Connection**
2. **Mode**: Chọn **Viewer**
3. **Server (IP:Port)**: Nhập `serverapi.xyz:10010`
   - Thay `10010` bằng port của device bạn
   - Công thức: `Port = 10001 + (Device_Number - 1)`
   - Ví dụ:
     - Device 1 → `serverapi.xyz:10001`
     - Device 10 → `serverapi.xyz:10010`
     - Device 30 → `serverapi.xyz:10030`

### Bước 4: Bật TrollVNC
1. Bật **Enabled** = ON
2. Respring hoặc restart service

## 🎯 Ví Dụ Cấu Hình

### Device 10:
```
Desktop Name: Device-10
Reverse Mode: Viewer
Server (IP:Port): serverapi.xyz:10010
Enabled: ON
```

### Device 30:
```
Desktop Name: Device-30
Reverse Mode: Viewer
Server (IP:Port): serverapi.xyz:10030
Enabled: ON
```

## ✅ Kết Quả

Sau khi cấu hình:
1. iPhone sẽ kết nối reverse connection đến server
2. Server nhận diện device qua Desktop Name (Device ID)
3. Server map Device ID → Port tương ứng
4. Web monitor hiển thị device với port đúng

## 📝 Lưu Ý

1. **Desktop Name phải unique** và khớp với device_id trong snapshot API
2. **Port phải đúng** theo công thức: `10001 + (Device_Number - 1)`
3. **Format IP:Port**: `serverapi.xyz:10010` (không có khoảng trắng)
4. **Server IP có thể thay đổi**: Nếu server IP đổi, chỉ cần sửa lại trong Settings

---

**Status**: ✅ Settings UI đã được cải thiện, user có thể tự điền IP:port dễ dàng

