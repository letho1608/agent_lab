# Pupy Web UI

Giao diện web để quản lý Pupy: xem sessions, listeners, chạy module trên client, xem jobs.

## Bật Web UI

Trong `conf/pupy.conf`:

```ini
[pupyd]
webserver = true
```

Sau khi chạy server (`python main.py` → chọn 1), trong MOTD sẽ có:

```
Web UI: http://localhost:9000/webui
```

Mở URL đó trong trình duyệt (chỉ truy cập từ local/ip trong `[webserver] local_ips`).

## Chức năng

- **Sessions**: Danh sách client đang kết nối (ID, user, hostname, platform).
- **Listeners**: Danh sách listener đang chạy (tên, address, port).
- **Run module**: Chọn session (ID), nhập tên module và args → Run → xem output.
- **Jobs**: Danh sách job (ID, tên, clients).

## API (JSON)

- `GET /webui/api/ping` – kiểm tra kết nối (`{"ok": true}`)
- `GET /webui/api/sessions` – danh sách sessions
- `GET /webui/api/listeners` – danh sách listeners
- `GET /webui/api/modules` – danh sách modules
- `POST /webui/api/run` – body: `{ "session_id": 1, "module": "get_info", "args": [] }`
- `GET /webui/api/jobs` – danh sách jobs
- `GET /webui/api/config` – base path
