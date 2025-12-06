# 🚀 Hướng dẫn Build TrollVNC trên GitHub

## 📋 Mục đích

Build TrollVNC tự động trên GitHub Actions thay vì build trên máy local. Điều này giúp:
- ✅ Không cần cài Theos trên máy
- ✅ Build tự động mỗi khi push code
- ✅ Tải file .deb từ GitHub Actions
- ✅ Tạo Release tự động

---

## 🔧 Bước 1: Chuẩn bị Repository

### 1.1 Tạo Repository trên GitHub

1. Truy cập: https://github.com/new
2. Điền thông tin:
   - **Repository name**: `TrollVNC` (hoặc tên khác)
   - **Description**: `TrollVNC with serverapi.xyz integration`
   - **Visibility**: Private hoặc Public
3. **KHÔNG** chọn "Add a README file"
4. Click **"Create repository"**

### 1.2 Cài đặt Git trên Windows

**Tải Git:**
- Link: https://git-scm.com/download/win
- Chọn: "64-bit Git for Windows Setup"
- Cài đặt với các tùy chọn mặc định

**Kiểm tra sau khi cài:**
```bash
git --version
# Output: git version 2.x.x
```

---

## 📤 Bước 2: Tải Code lên GitHub

### Option A: Dùng Git Command Line

Mở **Git Bash** hoặc **PowerShell** tại thư mục `TrollVNC-main`:

```bash
# Khởi tạo Git repository
git init

# Thêm remote URL (thay YOUR_USERNAME và YOUR_REPO)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# Thêm tất cả files
git add .

# Commit
git commit -m "Initial commit: TrollVNC with serverapi.xyz integration"

# Push lên GitHub
git branch -M main
git push -u origin main
```

**Nếu lần đầu push, Git sẽ hỏi username/password:**
- Username: `your_github_username`
- Password: Dùng **Personal Access Token** (không phải password thường)

**Tạo Personal Access Token:**
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token
3. Chọn scope: `repo` (full control)
4. Copy token và dùng làm password

### Option B: Dùng GitHub Desktop (Dễ hơn)

1. Tải GitHub Desktop: https://desktop.github.com/
2. Cài đặt và đăng nhập GitHub
3. File → Add Local Repository → Chọn thư mục `TrollVNC-main`
4. Nếu chưa có Git repo, click "Create a repository here"
5. Publish repository → Chọn Private/Public → Publish

### Option C: Dùng Visual Studio Code

1. Mở thư mục `TrollVNC-main` trong VS Code
2. Click icon **Source Control** (bên trái)
3. Click "Initialize Repository"
4. Stage all changes (dấu +)
5. Commit message: `Initial commit`
6. Click "Publish Branch" → Chọn Private/Public

---

## 🏗️ Bước 3: Build trên GitHub Actions

### 3.1 Kiểm tra Workflow đã được tạo

File `.github/workflows/build.yml` đã được tạo tự động. Workflow này sẽ:
- Build TrollVNC khi có push hoặc pull request
- Build 2 versions: rootless và roothide
- Upload file .deb làm artifacts

### 3.2 Trigger Build

**Cách 1: Push code**
Mỗi khi bạn push code, GitHub Actions sẽ tự động build.

**Cách 2: Manual trigger**
1. Truy cập: `https://github.com/YOUR_USERNAME/YOUR_REPO/actions`
2. Click workflow "Build TrollVNC"
3. Click "Run workflow" → "Run workflow"

### 3.3 Xem Build Progress

1. GitHub → Repository → Actions tab
2. Click vào workflow run đang chạy
3. Xem logs chi tiết của từng bước

**Build thành công khi:**
- Tất cả steps có dấu ✅ màu xanh
- Thời gian: ~5-10 phút

---

## 📥 Bước 4: Tải file .deb

### 4.1 Tải từ Actions Artifacts

1. GitHub → Actions → Click vào build run đã hoàn thành
2. Scroll xuống phần **"Artifacts"**
3. Tải file: `TrollVNC-X.X.X.zip`
4. Giải nén → Lấy file `.deb`

### 4.2 Tải từ Releases (nếu đã tạo tag)

Nếu bạn muốn tạo Release:

```bash
# Tag version
git tag v1.0.0

# Push tag
git push origin v1.0.0
```

GitHub Actions sẽ tự động tạo Release với file .deb đính kèm.

Tải tại: `https://github.com/YOUR_USERNAME/YOUR_REPO/releases`

---

## 🔧 Bước 5: Tùy chỉnh Build (Optional)

### 5.1 Thay đổi server address

Nếu muốn đổi server khác `serverapi.xyz`, sửa file:

**`prefs/TrollVNCPrefs/Resources/Managed.plist`**
```xml
<key>ReverseSocket</key>
<string>YOUR_SERVER.com:5500</string>
```

Sau đó commit và push lại.

### 5.2 Thay đổi version

**`layout/DEBIAN/control`**
```
Version: 1.0.1
```

### 5.3 Build chỉ rootless hoặc roothide

Sửa file `.github/workflows/build.yml`, xóa bỏ job không cần.

---

## 📱 Bước 6: Cài đặt trên iPhone

### 6.1 Copy file .deb lên iPhone

**Option A: AirDrop**
- Gửi file .deb qua AirDrop
- Mở trong TrollStore

**Option B: iCloud Drive**
- Upload .deb lên iCloud
- Tải trên iPhone
- Open in TrollStore

**Option C: SSH/Filza**
```bash
scp TrollVNC-rootless.deb mobile@IPHONE_IP:/var/mobile/
```

### 6.2 Cài đặt qua TrollStore

1. Mở TrollStore
2. Tap dấu `+`
3. Chọn file `.deb`
4. Tap "Install"

### 6.3 Khởi động

1. Mở app **TrollVNC**
2. Settings → Bật **Enabled**
3. App sẽ tự động kết nối đến `serverapi.xyz:5500`

---

## 🔍 Bước 7: Kiểm tra kết nối

### Trên Server

```bash
pm2 logs vnc-proxy
```

**Phải thấy:**
```
[VNC] New connection from XXX.XXX.XXX.XXX
[VNC] Device ID: XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
```

### Trên iPhone

```bash
ssh mobile@IPHONE_IP
tail -f /var/mobile/Library/Logs/TrollVNC/trollvncserver.log
```

**Phải thấy:**
```
[TrollVNC] Reverse connection established to serverapi.xyz
[TrollVNC] Device ID sent to server
```

### Trên Web

1. Truy cập: https://serverapi.xyz/monitor
2. Thấy device trong list (🟢 Bật)
3. Click "📺 VNC Live"

---

## ⚠️ Troubleshooting

### Build failed: "Could not find Theos"

→ Workflow đã cấu hình tự động cài Theos, không cần lo

### Build failed: Permission denied

→ Check file permissions trong workflow

### Artifact not found

→ Build phải thành công trước (tất cả steps màu xanh)

### .deb không cài được

→ Check iOS version compatibility
→ Thử build lại với `roothide` thay vì `rootless`

---

## 📊 Tóm tắt

```
┌─────────────────┐
│  Push to GitHub │
└────────┬────────┘
         │
         ▼
┌─────────────────────┐
│ GitHub Actions      │
│ Build Automatically │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│ Download .deb       │
│ from Artifacts      │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│ Install on iPhone   │
│ via TrollStore      │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│ Auto-connect to     │
│ serverapi.xyz:5500  │
└─────────────────────┘
```

---

## 🎯 Next Steps

1. ✅ Push code lên GitHub
2. ✅ Đợi GitHub Actions build (5-10 phút)
3. ✅ Tải file .deb
4. ✅ Cài lên iPhone
5. ✅ Kiểm tra trên https://serverapi.xyz/monitor

**Chúc bạn thành công!** 🚀

