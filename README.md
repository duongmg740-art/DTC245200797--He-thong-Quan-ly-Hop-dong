# DTC245200797 — Hệ thống quản lý hợp đồng

Ứng dụng Django quản lý hợp đồng và bên liên quan; PostgreSQL lưu trữ dữ liệu, pgAdmin quản trị cơ sở dữ liệu, Nginx làm reverse proxy. Prometheus/Grafana giám sát hệ thống; Loki/Promtail tập trung log ứng dụng, web server và database.

## Yêu cầu

- Docker Desktop hoặc Docker Engine hỗ trợ Docker Compose v2.
- Git.

## Khởi chạy

```powershell
Copy-Item .env.example .env
```

Sửa `.env` trước khi khởi chạy. Sinh chuỗi ngẫu nhiên trong PowerShell bằng lệnh sau (chạy riêng cho từng mật khẩu/secret), rồi điền các giá trị khác nhau vào `.env`:

```powershell
$bytes = New-Object byte[] 48
[System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
[Convert]::ToBase64String($bytes)
```

Dùng các chuỗi ngẫu nhiên riêng biệt cho `DJANGO_SECRET_KEY`, `POSTGRES_ADMIN_PASSWORD`, `APP_DB_PASSWORD`, `POSTGRES_EXPORTER_PASSWORD`, `PGADMIN_DEFAULT_PASSWORD` và `GRAFANA_ADMIN_PASSWORD`; không đưa `.env` lên Git.

```powershell
docker compose -f compose.yaml -f compose.monitoring.yaml -f compose.logging.yaml up --build -d
docker compose -f compose.yaml -f compose.monitoring.yaml -f compose.logging.yaml exec web python manage.py createsuperuser
```

Đợi `docker compose ps` báo các dịch vụ healthy. Tạo tài khoản quản trị Django rồi đăng nhập để quản lý dữ liệu.

| Thành phần | Địa chỉ từ máy host |
|---|---|
| Ứng dụng hợp đồng (qua Nginx) | http://localhost |
| Django Admin | http://localhost/admin/ |
| pgAdmin | http://127.0.0.1:5050 |
| Grafana | http://127.0.0.1:3000 |
| Prometheus | http://127.0.0.1:9090 |

pgAdmin kết nối máy chủ PostgreSQL với host `db`, port `5432`, và tài khoản quản trị `POSTGRES_ADMIN_USER` trong `.env`. Ứng dụng dùng tài khoản riêng `APP_DB_USER` không có quyền superuser; exporter dùng tài khoản `POSTGRES_EXPORTER_USER` chỉ có quyền giám sát.

## Chức năng

- Đăng nhập, phân quyền thao tác qua tài khoản Django.
- Tạo, tìm kiếm, lọc trạng thái, xem và cập nhật hợp đồng.
- Theo dõi mã hợp đồng, mô tả, giá trị, ngày hiệu lực/hết hạn và bên liên quan.
- Quản lý danh bạ tổ chức/cá nhân, thông tin liên hệ.
- Django Admin cho tác vụ quản trị.

## Giám sát

Prometheus thu thập `/metrics` của Django, trạng thái Nginx qua `nginx-prometheus-exporter`, PostgreSQL qua `postgres-exporter`, và số liệu container qua cAdvisor. Dashboard được provision tự động trong Grafana; kiểm tra target tại Prometheus `/targets`.

## Log tập trung / LogQL

Promtail đọc log file dùng chung của Django, Nginx và PostgreSQL rồi gửi đến Loki. Truy vấn tại **Grafana → Explore → Loki**:

```logql
{service="django"}
{service="nginx"} |= " 500 "
sum(count_over_time({service="postgres"}[5m]))
```

Loki giữ log tối đa 30 ngày. Promtail chỉ đọc volume log và không mount Docker socket.

## Hardening và lưu ý triển khai

- Django, Nginx, PostgreSQL, Prometheus, Grafana, Loki, Promtail và exporters chạy non-root; `log-init` là helper root khởi tạo quyền volume một lần, bỏ các capability mặc định và chỉ thêm `CHOWN`/`FOWNER`.
- PostgreSQL và observability nằm trong network nội bộ; chỉ Nginx công khai cổng 80. pgAdmin, Grafana và Prometheus chỉ bind `127.0.0.1`.
- Container hỗ trợ được đặt `read_only`, giới hạn filesystem ghi qua `tmpfs`/volume, và bật `no-new-privileges`.
- Nginx thêm CSP, `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy`, tắt server tokens, giới hạn body và cấu hình reverse proxy.
- cAdvisor cần UID root cùng một số mount host dạng read-only để thu thập số liệu container. Mount `/var/run` có thể chứa Docker socket; quyền truy cập socket tương đương quyền quản trị host dù mount chỉ đọc. Không expose cAdvisor ra host; với production có yêu cầu bảo mật cao, thay bằng socket proxy giới hạn endpoint hoặc nguồn metrics khác.
- Cấu hình mẫu dùng HTTP; bảo vệ bằng security headers nhưng **chưa bật HTTPS**. Đặt sau TLS-terminating load balancer hoặc bổ sung chứng chỉ TLS trước khi mở truy cập Internet.
- Thay tất cả secret mẫu; giữ `.env` ngoài Git, giới hạn quyền truy cập máy chủ, sao lưu PostgreSQL và pin/cập nhật image định kỳ.

## Kiểm thử

```powershell
docker compose -f compose.yaml -f compose.monitoring.yaml -f compose.logging.yaml run --rm -e DJANGO_TESTING=1 web python manage.py test
docker compose -f compose.yaml -f compose.monitoring.yaml -f compose.logging.yaml exec web python manage.py check
docker compose -f compose.yaml -f compose.monitoring.yaml -f compose.logging.yaml down
```

Test suite dùng SQLite in-memory để không cần cấp quyền tạo database cho tài khoản ứng dụng; môi trường chạy thật vẫn sử dụng PostgreSQL.

`docker compose down -v` xóa dữ liệu PostgreSQL và log; chỉ dùng khi chủ động muốn xóa sạch dữ liệu.
