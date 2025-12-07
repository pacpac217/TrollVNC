# 🚀 Hướng Dẫn Build và Push lên GitHub

## ✅ Đã hoàn thành:
- Đã đơn giản hóa Settings, chỉ còn trường **Server (IP:Port)**

## 📤 Cách Push lên GitHub:

### ⭐ CÁCH 1: Dùng Script PowerShell (Khuyến nghị)

1. **Mở PowerShell** (nhấn `Windows + X` → chọn "Windows PowerShell" hoặc "Terminal")

2. **Chuyển đến thư mục project:**
   ```powershell
   cd "C:\Users\quang nguyen\Desktop\setting view máy iphone\TrollVNC-main"
   ```

3. **Chạy script:**
   ```powershell
   .\commit-and-push.ps1
   ```

4. **Nếu Git chưa cài:**
   - Tải Git: https://git-scm.com/download/win
   - Hoặc dùng GitHub Desktop: https://desktop.github.com/

---

### 💻 CÁCH 2: Dùng GitHub Desktop (Dễ nhất)

1. **Tải GitHub Desktop:**
   - Link: https://desktop.github.com/
   - Cài đặt và đăng nhập GitHub

2. **Thêm Repository:**
   - File → Add Local Repository
   - Chọn thư mục: `TrollVNC-main`
   - Nếu hỏi "create a repository here" → Click OK

3. **Commit và Push:**
   - Nhập commit message: "Simplify settings: Keep only IP:Port"
   - Click "Commit to main"
   - Click "Push origin" hoặc "Publish repository"

---

### 🔧 CÁCH 3: Dùng Git Command Line

**Nếu Git đã cài và có trong PATH:**

```bash
# Kiểm tra trạng thái
git status

# Thêm tất cả files
git add .

# Commit
git commit -m "Simplify settings: Keep only IP:Port configuration"

# Push lên GitHub
git push origin main
```

**Nếu chưa có remote:**
```bash
git remote add origin https://github.com/YOUR_USERNAME/TrollVNC.git
git push -u origin main
```

**Nếu branch là 'master':**
```bash
git push origin master
```

---

## 🔐 Nếu hỏi Username/Password:

GitHub không còn hỗ trợ password. Cần dùng **Personal Access Token**:

1. Truy cập: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Chọn scope: **repo** (full control)
4. Copy token
5. Khi Git hỏi password → paste token vào

---

## 📱 Sau khi Push lên GitHub:

1. **GitHub Actions sẽ tự động build:**
   - Truy cập repo trên GitHub
   - Vào tab "Actions"
   - Xem build progress (đợi 5-10 phút)

2. **Tải file .deb:**
   - Sau khi build xong (tất cả steps màu xanh)
   - Click vào build run
   - Scroll xuống "Artifacts"
   - Tải file `.deb`

3. **Cài trên iPhone:**
   - Copy file `.deb` vào iPhone
   - Mở bằng TrollStore
   - Cài đặt

---

## ⚠️ Lưu ý:

- Nếu Git chưa cài, dùng **GitHub Desktop** (dễ nhất)
- Nếu gặp lỗi, xem file `RUN-THESE-COMMANDS.txt` hoặc `UPLOAD-TO-GITHUB.txt`
- Đảm bảo đã đăng nhập GitHub trước khi push

