# 📋 Tóm Tắt Cập Nhật TrollVNC Source Code

## ✅ Đã Cập Nhật

### 1. `src/trollvncserver.mm` (Line 4722-4756)

**Thay đổi chính:**
- ✅ **Dùng Desktop Name làm Device ID** thay vì UUID
- ✅ Desktop Name sẽ được gửi đến server để nhận diện device
- ✅ Fallback về UUID nếu Desktop Name không được set

**Code mới:**
```objective-c
// Use Desktop Name as Device ID (e.g., "Device-10", "Device-30")
NSString *deviceId = gDesktopName;
if (!deviceId || deviceId.length == 0) {
    // Fallback to UUID if Desktop Name is not set
    deviceId = [[[UIDevice currentDevice] identifierForVendor] UUIDString];
    ...
}
```

**Lợi ích:**
- Device ID dễ nhận diện: "Device-10", "Device-30" thay vì UUID dài
- Khớp với device_id trong snapshot API
- User có thể set Desktop Name trong Settings hoặc Managed.plist

### 2. `prefs/TrollVNCPrefs/Resources/Managed.plist`

**Thay đổi chính:**
- ✅ **Bật Reverse Connection** (đã uncomment)
- ✅ Set Desktop Name = "Device-10" (ví dụ)
- ✅ Set ReverseSocket = "serverapi.xyz:10010" (ví dụ cho Device 10)

**Cấu hình mới:**
```xml
<key>DesktopName</key>
<string>Device-10</string>

<key>ReverseMode</key>
<string>viewer</string>

<key>ReverseSocket</key>
<string>serverapi.xyz:10010</string>
```

## 🔧 Cách Sử Dụng

### Cho Mỗi Device:

1. **Desktop Name**: Phải khớp với device_id trong snapshot API
   - Device 10 → "Device-10"
   - Device 30 → "Device-30"

2. **Reverse Socket Port**: Tính theo công thức
   - Device 10 → Port 10010 (`serverapi.xyz:10010`)
   - Device 30 → Port 10030 (`serverapi.xyz:10030`)
   - Công thức: `Port = 10001 + (Device_Number - 1)`

3. **Tạo Managed.plist cho từng device:**
   - Option 1: Tạo file riêng cho mỗi device khi build .deb
   - Option 2: User tự config trong Settings sau khi cài

## 📦 Build .deb

Sau khi cập nhật code, build lại package:

```bash
# Trong GitHub Actions (tự động)
# Hoặc build local:
make package THEOS_PACKAGE_SCHEME=roothide FINALPACKAGE=1
```

## ✅ Kiểm Tra Sau Khi Build

1. **Cài .deb lên iPhone**
2. **Settings → TrollVNC:**
   - Enabled = ON
   - Desktop Name = "Device-10" (hoặc device number tương ứng)
   - Reverse Mode = "viewer"
   - Reverse Socket = "serverapi.xyz:10010" (port tương ứng)

3. **Kiểm tra log trên server:**
   ```
   [VNC:10010] Device ID: Device-10
   [VNC:10010] New connection from ...
   ```

4. **Kiểm tra trên web monitor:**
   - Device "Device-10" hiển thị với icon 🔵 VNC
   - Port hiển thị: 10010

## 🎯 Tóm Tắt Logic

```
iPhone (Device 10)
  ↓
Desktop Name = "Device-10"
  ↓
Reverse Socket = "serverapi.xyz:10010"
  ↓
Kết nối đến server port 10010
  ↓
Gửi "Device-10" (32 bytes) làm Device ID
  ↓
Server nhận diện: Device-10 → Port 10010
  ↓
Web monitor hiển thị: Device-10 (Port 10010) 🔵 VNC
```

## ⚠️ Lưu Ý Quan Trọng

1. **Desktop Name phải unique** và khớp với device_id trong snapshot API
2. **Port phải đúng** theo công thức: `10001 + (Device_Number - 1)`
3. **ReverseSocket phải đúng format**: `serverapi.xyz:PORT`
4. **Device ID được gửi là Desktop Name**, không phải UUID

---

**Status**: ✅ Code đã được cập nhật, sẵn sàng build .deb

