# Xử lý khi IP iPhone thay đổi

## ✅ Có, vẫn kết nối được!

Vì đây là **reverse connection** (iPhone kết nối ra server), nên khi IP iPhone thay đổi:

### Cách hoạt động:

1. **iPhone là client** → iPhone tự kết nối ra server
2. **Server có IP tĩnh** → iPhone luôn biết địa chỉ server (serverapi.xyz)
3. **Khi IP iPhone thay đổi**:
   - Connection hiện tại sẽ bị ngắt
   - iPhone tự động reconnect (nhờ watchdog)
   - Server nhận kết nối mới với cùng Device ID
   - Web client tự động reconnect

## Cơ chế Auto-Reconnect

### 1. TrollVNC Watchdog (trollvncmanager)

- **Tự động restart** process nếu crash hoặc exit
- **Retry interval**: 30 giây (có thể config)
- Khi connection mất → process exit → watchdog restart → reconnect

### 2. Server Proxy

- **Giữ Device ID** trong memory khi connection mất
- **Nhận kết nối mới** với cùng Device ID → tự động replace connection cũ
- **WebSocket clients** được notify và tự động reconnect

### 3. Web Client

- **Auto-reconnect** khi WebSocket bị đóng
- **Polling device list** mỗi 5 giây để detect reconnection

## Các trường hợp IP thay đổi

### ✅ Trường hợp 1: Chuyển mạng (WiFi → 4G)

```
iPhone (WiFi IP: 192.168.1.100)
  ↓ kết nối
Server (serverapi.xyz:5500)
  ↓ IP thay đổi
iPhone (4G IP: 10.20.30.40)
  ↓ tự động reconnect (sau ~30s)
Server (nhận kết nối mới, cùng Device ID)
```

### ✅ Trường hợp 2: 4G roaming (chuyển cell tower)

```
iPhone (4G IP: 10.20.30.40)
  ↓ kết nối
Server
  ↓ chuyển cell tower
iPhone (4G IP: 10.50.60.70) ← IP mới
  ↓ tự động reconnect
Server (nhận kết nối mới)
```

### ✅ Trường hợp 3: Mất mạng tạm thời

```
iPhone kết nối
  ↓ mất mạng 5 phút
  ↓ mạng trở lại
  ↓ tự động reconnect
Server (nhận kết nối lại)
```

## Cấu hình để tối ưu

### 1. TrollVNC Manager (trollvncmanager.mm)

Đã có sẵn retry interval:
```objc
@"TROLLVNC_REPEATER_RETRY_INTERVAL" : @"30.0"
```

### 2. Server Proxy

- **Keep-alive**: Tự động detect connection loss
- **Reconnection tracking**: Đếm số lần reconnect
- **Connection pooling**: Giữ connection info để reuse

### 3. Web Client

- **Reconnect delay**: 3 giây (có thể config)
- **Exponential backoff**: Tăng delay nếu reconnect fail nhiều lần

## Monitoring & Logs

### Server logs:

```
[VNC] Device ID: ABC123 from 192.168.1.100:54321
[VNC] Device ABC123 reconnected (IP may have changed)
[VNC] Device ABC123 reconnected 1 time(s)
```

### API Response:

```json
{
  "devices": [
    {
      "deviceId": "ABC123",
      "connectedAt": "2025-01-20T10:00:00Z",
      "lastReconnectAt": "2025-01-20T10:05:00Z",
      "reconnectCount": 1,
      "isConnected": true,
      "remoteAddress": "10.20.30.40"
    }
  ]
}
```

## Best Practices

1. **Set retry interval hợp lý**: 30-60 giây
   - Quá ngắn → tốn battery
   - Quá dài → reconnect chậm

2. **Monitor connection health**:
   - Check connection status định kỳ
   - Alert nếu device offline quá lâu

3. **Handle multiple reconnections**:
   - Server tự động cleanup connection cũ
   - Web client tự động switch sang connection mới

4. **Network resilience**:
   - Sử dụng keep-alive packets
   - Detect connection loss sớm
   - Graceful reconnection

## Troubleshooting

### Vấn đề: Device không reconnect sau khi IP thay đổi

**Giải pháp**:
1. Kiểm tra watchdog có đang chạy không
2. Kiểm tra logs: `pm2 logs vnc-proxy`
3. Kiểm tra firewall trên server
4. Tăng retry interval nếu cần

### Vấn đề: Web client không tự động reconnect

**Giải pháp**:
1. Kiểm tra WebSocket close event handler
2. Kiểm tra device list polling
3. Thêm manual reconnect button

### Vấn đề: Connection bị duplicate

**Giải pháp**:
- Server tự động cleanup connection cũ
- Device ID là unique identifier
- Chỉ giữ 1 connection active per device

## Kết luận

✅ **Reverse connection** giải quyết hoàn toàn vấn đề IP động:
- iPhone tự kết nối ra server
- Không cần biết IP iPhone
- Tự động reconnect khi IP thay đổi
- Server luôn có thể kết nối với iPhone

