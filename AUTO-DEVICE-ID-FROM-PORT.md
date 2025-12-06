# 🔄 Tự Động Generate Device ID Từ Port

## ✅ Logic Mới

### Cách Hoạt Động:
1. **User chỉ cần nhập IP:Port** trong Settings
   - Ví dụ: `serverapi.xyz:10010`
   - Ví dụ: `serverapi.xyz:10300`

2. **Device ID tự động generate từ port:**
   - Port 10010 → Device Number = 10010 - 10000 = **10** → Device ID = **"Device-10"**
   - Port 10300 → Device Number = 10300 - 10000 = **300** → Device ID = **"Device-300"**
   - Port 10001 → Device Number = 10001 - 10000 = **1** → Device ID = **"Device-1"**

3. **Desktop Name tự động cập nhật:**
   - Desktop Name sẽ được set = Device ID
   - Không cần user nhập thủ công

## 📱 Cách Sử Dụng Trên iPhone

### Bước 1: Mở Settings
1. Settings → **TrollVNC**

### Bước 2: Cấu hình Reverse Connection
1. **Mode**: Chọn **Viewer**
2. **Server (IP:Port)**: Nhập `serverapi.xyz:10010`
   - Thay port theo device number của bạn
   - Port = 10000 + Device Number
   - Ví dụ:
     - Device 10 → `serverapi.xyz:10010`
     - Device 300 → `serverapi.xyz:10300`
     - Device 500 → `serverapi.xyz:10500`

### Bước 3: Bật TrollVNC
1. Bật **Enabled** = ON
2. Respring hoặc restart service

### Bước 4: Kiểm Tra (Tự Động)
- Desktop Name sẽ tự động = "Device-10" (nếu port = 10010)
- Device ID gửi đến server = "Device-10"
- Server nhận diện: Device-10 → Port 10010

## 🎯 Ví Dụ

### Device 10:
```
Input: serverapi.xyz:10010
Auto-generated:
  - Device Number: 10 (10010 - 10000)
  - Device ID: "Device-10"
  - Desktop Name: "Device-10"
```

### Device 300:
```
Input: serverapi.xyz:10300
Auto-generated:
  - Device Number: 300 (10300 - 10000)
  - Device ID: "Device-300"
  - Desktop Name: "Device-300"
```

### Device 500:
```
Input: serverapi.xyz:10500
Auto-generated:
  - Device Number: 500 (10500 - 10000)
  - Device ID: "Device-500"
  - Desktop Name: "Device-500"
```

## 🔢 Công Thức

```
Device Number = Port - 10000
Device ID = "Device-" + Device Number
Desktop Name = Device ID (auto-updated)
```

## ⚠️ Lưu Ý

1. **Port Range**: 10001 - 10500 (Device 1 - 500)
   - Nếu port ngoài range này, sẽ fallback về Desktop Name hoặc UUID

2. **Desktop Name Field**: 
   - Vẫn có trong Settings nhưng sẽ tự động fill
   - User không cần nhập thủ công

3. **Server nhận diện:**
   - Server vẫn nhận Device ID qua 32 bytes đầu
   - Device ID = "Device-XX" (tự động từ port)

## ✅ Kết Quả

- ✅ **User chỉ cần nhập IP:Port**
- ✅ **Device ID tự động generate từ port**
- ✅ **Desktop Name tự động cập nhật**
- ✅ **Server nhận diện device đúng**

---

**Status**: ✅ Logic đã được cập nhật, sẵn sàng build

