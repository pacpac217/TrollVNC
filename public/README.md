# TrollVNC Web Dashboard

Giao diện web quản lý và xem các iPhone kết nối qua TrollVNC.

## Tính năng

- ✅ Dashboard với thống kê real-time
- ✅ Danh sách devices với thông tin chi tiết
- ✅ VNC viewer để xem màn hình iPhone
- ✅ Auto-refresh device list
- ✅ Responsive design
- ✅ Dark theme

## Cài đặt

1. Đảm bảo server proxy đang chạy
2. Mở browser và truy cập: `http://serverapi.xyz:3000`
3. Giao diện sẽ tự động load danh sách devices

## Tích hợp noVNC

Để hiển thị VNC đầy đủ, cần tích hợp noVNC library:

```html
<script src="https://cdn.jsdelivr.net/npm/@novnc/novnc@1.4.0/lib/noVNC.min.js"></script>
```

Sau đó sửa function `initVNCViewer` trong `app.js`:

```javascript
function initVNCViewer(canvas, ws) {
    const rfb = new RFB(canvas, ws.url);
    rfb.scaleViewport = true;
    rfb.resizeSession = false;
    rfb.background = '#000000';
}
```

## Customization

- Thay đổi màu sắc trong `style.css` (CSS variables)
- Thêm tính năng mới trong `app.js`
- Tùy chỉnh layout trong `index.html`

