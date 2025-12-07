# Script để commit và push lên GitHub
# Chạy script này: .\commit-and-push.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  🚀 COMMIT VÀ PUSH LÊN GITHUB" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Kiểm tra Git đã cài đặt chưa
try {
    $gitVersion = git --version
    Write-Host "✅ Git đã được cài đặt: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Git chưa được cài đặt!" -ForegroundColor Red
    Write-Host "   Vui lòng cài Git từ: https://git-scm.com/download/win" -ForegroundColor Yellow
    Write-Host "   Hoặc dùng GitHub Desktop: https://desktop.github.com/" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "📋 Kiểm tra trạng thái Git..." -ForegroundColor Yellow
git status

Write-Host ""
Write-Host "📦 Đang thêm tất cả files..." -ForegroundColor Yellow
git add .

Write-Host ""
Write-Host "💾 Đang commit..." -ForegroundColor Yellow
$commitMessage = "Simplify settings: Keep only IP:Port configuration"
git commit -m $commitMessage

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Commit thành công!" -ForegroundColor Green
} else {
    Write-Host "⚠️  Có thể không có thay đổi nào để commit" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "☁️  Đang push lên GitHub..." -ForegroundColor Yellow
Write-Host "   (Nếu hỏi username/password, dùng Personal Access Token)" -ForegroundColor Yellow
Write-Host ""

# Thử push lên main branch
git push origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  ✅ PUSH THÀNH CÔNG!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "📱 Tiếp theo:" -ForegroundColor Cyan
    Write-Host "   1. Truy cập GitHub repo của bạn" -ForegroundColor White
    Write-Host "   2. Vào tab 'Actions' để xem build progress" -ForegroundColor White
    Write-Host "   3. Đợi 5-10 phút cho GitHub Actions build" -ForegroundColor White
    Write-Host "   4. Tải file .deb từ Artifacts" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "⚠️  Push có thể cần thêm thông tin:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Nếu chưa có remote, thêm remote:" -ForegroundColor Cyan
    Write-Host "   git remote add origin https://github.com/YOUR_USERNAME/TrollVNC.git" -ForegroundColor White
    Write-Host ""
    Write-Host "Nếu branch là 'master' thay vì 'main':" -ForegroundColor Cyan
    Write-Host "   git push origin master" -ForegroundColor White
    Write-Host ""
    Write-Host "Nếu cần set upstream:" -ForegroundColor Cyan
    Write-Host "   git push -u origin main" -ForegroundColor White
    Write-Host ""
}

