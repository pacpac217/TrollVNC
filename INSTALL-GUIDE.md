# 📱 HƯỚNG DẪN CÀI ĐẶT TROLLVNC LÊN IPHONE (DOPAMINE)

## ✅ Build đã thành công!

File `.deb` đã được build thành công và sẵn sàng để cài đặt.

---

## 📥 BƯỚC 1: TẢI FILE .DEB

### Cách 1: Tải từ GitHub Actions (Khuyên dùng)

1. **Mở link này:**
   ```
   https://github.com/pacpac217/TrollVNC/actions
   ```

2. **Tìm workflow run mới nhất** (có dấu ✅ màu xanh)

3. **Cuộn xuống phần "Artifacts"** (ở cuối trang)

4. **Click vào "TrollVNC-2.7"** (hoặc tên tương tự)

5. **Download file `.deb`** về máy tính

### Cách 2: Clone repository và build local

```bash
git clone https://github.com/pacpac217/TrollVNC.git
cd TrollVNC
# Build trên macOS với Theos
```

---

## 📲 BƯỚC 2: CHUYỂN FILE VÀO IPHONE

### Cách 1: AirDrop (Nhanh nhất)
1. Mở AirDrop trên iPhone
2. Right-click file `.deb` trên Mac → Share → AirDrop
3. Chọn iPhone của bạn

### Cách 2: iCloud Drive
1. Upload file `.deb` lên iCloud Drive
2. Mở Files app trên iPhone
3. Tải file về

### Cách 3: SSH (Cho người dùng nâng cao)
```bash
# Từ máy tính, copy file vào iPhone qua SSH
scp TrollVNC-roothide.deb root@[IPHONE_IP]:/var/mobile/Documents/
```

---

## 🔧 BƯỚC 3: CÀI ĐẶT TRÊN IPHONE

### Phương pháp 1: Sileo (Khuyên dùng)

1. **Mở Sileo** trên iPhone
2. **Vào tab "Sources"**
3. **Click "Local Packages"** hoặc "Add Package"
4. **Chọn file `.deb`** đã tải về
5. **Click "Install"**
6. **Chờ cài đặt xong**

### Phương pháp 2: Filza

1. **Mở Filza** trên iPhone
2. **Tìm file `.deb`** (thường ở `/var/mobile/Documents/`)
3. **Tap vào file `.deb`**
4. **Chọn "Install"**
5. **Chờ cài đặt xong**

### Phương pháp 3: SSH + dpkg (Terminal)

1. **SSH vào iPhone:**
   ```bash
   ssh root@[IPHONE_IP]
   ```

2. **Cài đặt package:**
   ```bash
   cd /var/mobile/Documents
   dpkg -i TrollVNC-roothide.deb
   ```

3. **Fix dependencies (nếu cần):**
   ```bash
   apt-get install -f
   ```

---

## ⚙️ BƯỚC 4: KÍCH HOẠT TROLLVNC

1. **Mở Settings** trên iPhone
2. **Tìm "TrollVNC"** trong danh sách
3. **Bật "Enable TrollVNC"**
4. **Thiết bị sẽ tự động kết nối đến serverapi.xyz**

---

## 🌐 BƯỚC 5: XEM TRÊN WEB

1. **Mở trình duyệt**
2. **Vào:** `https://serverapi.xyz/monitor`
3. **Bạn sẽ thấy iPhone của mình trong danh sách**
4. **Click vào để xem màn hình iPhone**

---

## ❓ TROUBLESHOOTING

### Lỗi: "Unable to install package"
- **Giải pháp:** Đảm bảo bạn đang dùng Dopamine jailbreak
- Kiểm tra: Settings → Dopamine → Status

### Lỗi: "Dependencies not satisfied"
- **Giải pháp:** Chạy `apt-get install -f` trong terminal

### TrollVNC không hiện trong Settings
- **Giải pháp:** 
  1. Respring iPhone: `killall -9 SpringBoard`
  2. Hoặc reboot và rejailbreak

### Không kết nối được đến server
- **Giải pháp:**
  1. Kiểm tra internet trên iPhone
  2. Kiểm tra file `Managed.plist` có đúng cấu hình không
  3. Xem log: `tail -f /var/log/trollvnc.log`

---

## 📞 HỖ TRỢ

Nếu gặp vấn đề, hãy:
1. Kiểm tra log: `/var/log/trollvnc.log`
2. Xem GitHub Issues: https://github.com/pacpac217/TrollVNC/issues
3. Kiểm tra README: https://github.com/pacpac217/TrollVNC

---

## 🎉 XONG!

Chúc bạn sử dụng TrollVNC thành công! 🚀

