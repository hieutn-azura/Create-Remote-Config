# Ads Config Generator — bản build

## Ubuntu / Linux (ĐÃ BUILD SẴN)
- File chạy: `ads_config_generator` (13MB, không cần cài Python).
- Chạy trực tiếp:
  ```bash
  ./ads_config_generator
  ```
- Cài vào menu ứng dụng (tuỳ chọn):
  ```bash
  ./install-ubuntu.sh
  ```
  Sau đó mở "Ads Config Generator" từ menu.

> Binary này build trên Ubuntu x86-64. Máy Ubuntu khác chạy được ngay;
> nếu máy quá cũ về glibc thì build lại bằng `build.yml` (job linux).

## Windows (.exe) — build trên máy Windows
PyInstaller **không** tạo được .exe từ Linux, nên chọn 1 trong 2:

**Cách 1 — máy Windows có sẵn Python:**
1. Cài Python 3.10–3.12 từ python.org (tick *Add Python to PATH*).
2. Chép cả thư mục này sang Windows.
3. Double-click `build-windows.bat`.
4. Lấy file ở `dist\ads_config_generator.exe`.

**Cách 2 — không có máy Windows, dùng GitHub Actions (miễn phí):**
1. Đưa thư mục này lên 1 repo GitHub (kèm `ads_config_generator.py` và `.github/workflows/build.yml`).
2. Vào tab **Actions** → chạy **build-installers** (hoặc push tag `v1`).
3. Tải **windows-exe** (và **linux-binary**) ở mục *Artifacts*.

## File nguồn
`ads_config_generator.py` — sửa code ở đây rồi build lại.
# Create-Remote-Config
