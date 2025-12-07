# 🔧 Khắc Phục Lỗi Không Mở Được Web Monitor

## ❌ Vấn Đề: Không mở được `serverapi.xyz/monitor`

## ✅ Giải Pháp

### 1. **Kiểm Tra Flask Server Có Đang Chạy Không**

```bash
# Kiểm tra process
ps aux | grep severapixyz
# hoặc
tasklist | findstr python
```

**Nếu chưa chạy**, khởi động server:
```bash
cd "C:\Users\quang nguyen\Desktop"
python severapixyz.py
```

**Output mong đợi:**
```
 * Running on http://0.0.0.0:5678
```

### 2. **URL Đúng**

Flask server chạy trên **port 5678**, không phải port 80!

**❌ SAI:**
```
serverapi.xyz/monitor
```

**✅ ĐÚNG:**
```
http://serverapi.xyz:5678/monitor
```

**Hoặc nếu truy cập local:**
```
http://localhost:5678/monitor
```

### 3. **Kiểm Tra Firewall**

Port 5678 phải được mở trên server:

```bash
# Linux
sudo ufw allow 5678
# hoặc
sudo iptables -A INPUT -p tcp --dport 5678 -j ACCEPT

# Windows (PowerShell as Admin)
New-NetFirewallRule -DisplayName "Flask Server" -Direction Inbound -LocalPort 5678 -Protocol TCP -Action Allow
```

### 4. **Kiểm Tra Server Đang Listen Đúng Port**

Trong file `severapixyz.py`:
```python
if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5678)
```

- `host="0.0.0.0"` = Listen trên tất cả interfaces (cho phép truy cập từ bên ngoài)
- `port=5678` = Port Flask server

### 5. **Kiểm Tra Logs**

Xem log của Flask server để biết lỗi:
```bash
python severapixyz.py
```

**Lỗi thường gặp:**
- `Address already in use` → Port 5678 đã được dùng
- `Permission denied` → Cần quyền admin để bind port
- `Connection refused` → Firewall chặn

## 🔍 Checklist

- [ ] Flask server đang chạy (`python severapixyz.py`)
- [ ] URL đúng: `http://serverapi.xyz:5678/monitor`
- [ ] Port 5678 mở trên firewall
- [ ] Server listen trên `0.0.0.0:5678` (không phải `127.0.0.1`)
- [ ] Không có process khác đang dùng port 5678

## 🚀 Cách Khởi Động Đúng

### Bước 1: Khởi động VNC Proxy Server
```bash
node server-vnc-proxy.js
```

**Output:**
```
[INFO] Initializing 500 VNC listeners...
[HTTP] Server started on port 3000
[INFO] VNC Listeners: 10001 to 10500
[INFO] WebSocket Server: 8080
```

### Bước 2: Khởi động Flask Server
```bash
cd "C:\Users\quang nguyen\Desktop"
python severapixyz.py
```

**Output:**
```
 * Running on http://0.0.0.0:5678
```

### Bước 3: Truy cập Web Monitor
```
http://serverapi.xyz:5678/monitor
```

## ⚠️ Lưu Ý

1. **Port 5678 không phải port mặc định** (port 80), nên phải ghi rõ trong URL
2. **Nếu dùng domain**, đảm bảo DNS trỏ đúng đến server IP
3. **Nếu truy cập từ bên ngoài**, cần mở port 5678 trên firewall/router

## 🔧 Nếu Vẫn Không Được

### Test local trước:
```bash
# Trên server
curl http://localhost:5678/monitor
```

### Kiểm tra port có đang listen:
```bash
# Linux
netstat -tuln | grep 5678
# hoặc
ss -tuln | grep 5678

# Windows
netstat -an | findstr 5678
```

### Kiểm tra từ client:
```bash
# Test kết nối
telnet serverapi.xyz 5678
# hoặc
curl http://serverapi.xyz:5678/monitor
```

---

**Status**: ✅ Hướng dẫn khắc phục lỗi truy cập web monitor

