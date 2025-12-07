# 🌐 Cấu Hình Dynamic DNS Cho serverapi.xyz

## 🎯 Mục Tiêu

Tự động cập nhật DNS khi IP server thay đổi, để domain `serverapi.xyz` luôn trỏ đến IP mới.

## ✅ Giải Pháp 1: Cloudflare DNS (Khuyên Dùng)

### Bước 1: Chuyển Domain Sang Cloudflare

1. **Đăng ký Cloudflare** (miễn phí): https://cloudflare.com
2. **Thêm domain** `serverapi.xyz` vào Cloudflare
3. **Thay đổi nameservers** của domain sang Cloudflare nameservers
4. **Đợi DNS propagate** (5-30 phút)

### Bước 2: Tạo API Token

1. Vào Cloudflare Dashboard → **My Profile** → **API Tokens**
2. Click **Create Token**
3. Chọn template: **Edit zone DNS**
4. Permissions:
   - Zone → DNS → Edit
5. Zone Resources:
   - Include → Specific zone → `serverapi.xyz`
6. Click **Continue to summary** → **Create Token**
7. **Copy token** (chỉ hiện 1 lần!)

### Bước 3: Lấy Zone ID

1. Vào Cloudflare Dashboard → Chọn zone `serverapi.xyz`
2. Ở sidebar bên phải, tìm **Zone ID**
3. Copy Zone ID

### Bước 4: Tạo DNS A Record

1. Vào **DNS** → **Records**
2. Click **Add record**
3. Cấu hình:
   - Type: `A`
   - Name: `@` (hoặc để trống cho root domain)
   - IPv4 address: `1.1.1.1` (tạm thời, sẽ tự động update)
   - Proxy status: `DNS only` (không proxy)
   - TTL: `Auto`
4. Click **Save**

### Bước 5: Cấu Hình Script

Tạo file `.env`:
```bash
CLOUDFLARE_API_TOKEN=your_api_token_here
CLOUDFLARE_ZONE_ID=your_zone_id_here
```

Hoặc export environment variables:
```bash
# Linux/Mac
export CLOUDFLARE_API_TOKEN="your_api_token_here"
export CLOUDFLARE_ZONE_ID="your_zone_id_here"

# Windows (PowerShell)
$env:CLOUDFLARE_API_TOKEN="your_api_token_here"
$env:CLOUDFLARE_ZONE_ID="your_zone_id_here"
```

### Bước 6: Chạy Script

```bash
# Cài đặt requests nếu chưa có
pip install requests

# Chạy script
python setup-dynamic-dns.py
```

### Bước 7: Tự Động Hóa (Cron Job)

**Linux/Mac:**
```bash
# Mở crontab
crontab -e

# Thêm dòng này (chạy mỗi 5 phút)
*/5 * * * * cd /path/to/script && /usr/bin/python3 setup-dynamic-dns.py >> /var/log/ddns.log 2>&1
```

**Windows (Task Scheduler):**
1. Mở **Task Scheduler**
2. Create Basic Task
3. Trigger: **Daily** → Repeat task every: **5 minutes**
4. Action: **Start a program**
   - Program: `python`
   - Arguments: `C:\path\to\setup-dynamic-dns.py`
   - Start in: `C:\path\to\`

## ✅ Giải Pháp 2: No-IP DDNS (Miễn Phí)

### Bước 1: Đăng Ký No-IP

1. Đăng ký: https://www.noip.com
2. Tạo hostname: `serverapi.ddns.net` (hoặc domain riêng nếu có)

### Bước 2: Cấu Hình Script

Sửa trong `setup-dynamic-dns.py`:
```python
DDNS_SERVICE = "noip"
```

Export credentials:
```bash
export NOIP_USERNAME="your_username"
export NOIP_PASSWORD="your_password"
```

### Bước 3: Chạy Script

```bash
python setup-dynamic-dns.py
```

## ✅ Giải Pháp 3: DuckDNS (Miễn Phí, Đơn Giản)

### Bước 1: Đăng Ký DuckDNS

1. Đăng ký: https://www.duckdns.org
2. Tạo subdomain: `serverapi.duckdns.org`
3. Copy token

### Bước 2: Cấu Hình Script

Sửa trong `setup-dynamic-dns.py`:
```python
DDNS_SERVICE = "duckdns"
DOMAIN = "serverapi"  # Subdomain name
```

Export token:
```bash
export DUCKDNS_TOKEN="your_token_here"
```

### Bước 3: Chạy Script

```bash
python setup-dynamic-dns.py
```

## 🔧 Tích Hợp Vào Flask Server

Có thể tích hợp vào `severapixyz.py` để tự động update khi server khởi động:

```python
# Thêm vào đầu file severapixyz.py
import subprocess
import threading

def update_dns():
    """Update DNS khi server khởi động"""
    try:
        subprocess.run(["python", "setup-dynamic-dns.py"], 
                      capture_output=True, timeout=30)
    except:
        pass

# Chạy trong thread riêng khi server start
if __name__ == "__main__":
    # Update DNS khi khởi động
    threading.Thread(target=update_dns, daemon=True).start()
    
    app.run(debug=False, host="0.0.0.0", port=5678)
```

## 📋 Checklist

- [ ] Domain đã được chuyển sang Cloudflare (hoặc dùng DDNS service)
- [ ] API token/credentials đã được cấu hình
- [ ] DNS A record đã được tạo
- [ ] Script đã được test và chạy thành công
- [ ] Cron job/Task Scheduler đã được setup
- [ ] Test truy cập: `http://serverapi.xyz:5678/monitor`

## 🚀 Test

### Test Script:
```bash
python setup-dynamic-dns.py
```

**Output mong đợi:**
```
[2025-01-XX XX:XX:XX] Checking IP...
Current IP: 123.45.67.89
IP changed: None → 123.45.67.89
✅ DNS updated successfully
```

### Test DNS:
```bash
nslookup serverapi.xyz
# hoặc
ping serverapi.xyz
```

### Test Web:
```
http://serverapi.xyz:5678/monitor
```

## ⚠️ Lưu Ý

1. **API Token phải bảo mật**, không commit vào git
2. **Cron job nên chạy mỗi 5-10 phút** để update kịp thời
3. **Kiểm tra log** thường xuyên để đảm bảo script chạy đúng
4. **Cloudflare có rate limit**, không nên update quá thường xuyên (< 1 phút)

---

**Status**: ✅ Hướng dẫn setup Dynamic DNS cho domain

