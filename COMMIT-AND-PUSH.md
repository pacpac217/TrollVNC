# Hướng dẫn Commit và Push lên GitHub

## Các lệnh cần chạy:

```bash
# 1. Kiểm tra file đã thay đổi
git status

# 2. Thêm file đã sửa
git add prefs/TrollVNCPrefs/Resources/ManagedRoot.plist

# 3. Commit với message
git commit -m "Fix: Add IP:Port settings to ManagedRoot.plist for managed mode"

# 4. Push lên GitHub
git push origin main
```

## Hoặc nếu dùng GitHub Desktop:

1. Mở GitHub Desktop
2. Sẽ thấy file `prefs/TrollVNCPrefs/Resources/ManagedRoot.plist` đã thay đổi
3. Nhập commit message: `Fix: Add IP:Port settings to ManagedRoot.plist for managed mode`
4. Click "Commit to main"
5. Click "Push origin" để push lên GitHub

## Sau khi push:

GitHub Actions sẽ tự động build deb file mới với settings IP:Port đã được thêm vào.

