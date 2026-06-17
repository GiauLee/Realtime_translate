# 🌐 Realtime Screen Translator

Công cụ dịch màn hình thời gian thực trên Linux. Chọn một vùng trên màn hình → tự động nhận diện chữ (OCR) → dịch sang tiếng Việt và hiển thị.

## Mục đích

Hỗ trợ đọc nội dung tiếng Anh trên màn hình (game, truyện, tài liệu...) bằng cách dịch realtime sang tiếng Việt mà không cần chuyển tab hay copy-paste.

---

## Kiến trúc Project

```
Realtime_translate/
├── main.py                      # Entry point + class ScreenTranslatorApp (điều phối toàn bộ)
├── core/
│   ├── ocr_engine.py            # Nhận diện chữ bằng Tesseract OCR (pytesseract)
│   └── translator_engine.py     # Dịch văn bản (hiện dùng googletrans, sẽ đổi sang argostranslate)
├── ui/
│   ├── main_window.py           # Giao diện chính (Tkinter) - các nút + khung hiển thị text
│   └── overlay.py               # Overlay toàn màn hình để chọn vùng cần dịch
├── requirements.txt             # Danh sách thư viện Python
├── install.sh                   # Script cài đặt tự động (Ubuntu/Debian)
└── README.md                    # File này
```

### Luồng hoạt động

```
[User bấm "Chọn vùng dịch"]
    → overlay.py: Hiện overlay toàn màn hình, user kéo chuột chọn vùng chữ nhật
    → main.py: Nhận tọa độ vùng (bbox), bắt đầu capture_loop trong thread riêng
    → Mỗi 1.5 giây:
        1. ImageGrab.grab(bbox) → chụp ảnh vùng đã chọn
        2. ocr_engine.py → detect_text() → nhận diện chữ từ ảnh
        3. So sánh với text lần trước → nếu khác thì:
        4. translator_engine.py → translate() → dịch EN→VI
        5. main_window.py → update_display() → hiển thị lên giao diện
```

### Mô tả từng file

| File | Vai trò |
|------|---------|
| `main.py` | Class `ScreenTranslatorApp` - điều phối toàn bộ: khởi tạo engine + UI, xử lý callback từ UI (start/stop/reload/toggle_top), chạy capture_loop trong background thread |
| `core/ocr_engine.py` | Hàm `detect_text(image)` - nhận PIL Image, chuyển sang grayscale, tăng contrast, gọi Tesseract OCR, lọc kết quả confidence > 60%, trả về string |
| `core/translator_engine.py` | Class `MyTranslator` - wrapper dịch EN→VI. Hiện dùng `googletrans` (không ổn định, sẽ đổi sang `argostranslate`) |
| `ui/main_window.py` | Class `MainWindow` - giao diện Tkinter: cột trái có 4 nút (Chọn vùng / Dừng quét / Reload / Ghim cửa sổ), cột phải có 2 ScrolledText (văn bản gốc + bản dịch). Always-on-top mặc định |
| `ui/overlay.py` | Class `ScreenSelector` - overlay fullscreen, chụp ảnh màn hình làm nền, cho user kéo chọn vùng hình chữ nhật, trả bbox qua callback |

---

## Tech Stack

| Thành phần | Thư viện | Ghi chú |
|------------|----------|---------|
| Giao diện | `tkinter` (built-in Python) | Cửa sổ chính + overlay chọn vùng |
| OCR | `pytesseract` + Tesseract OCR | Cần cài `tesseract-ocr` trên hệ thống |
| Dịch thuật | `googletrans==4.0.0rc1` | ⚠️ Không ổn định, kế hoạch đổi sang `argostranslate` |
| Xử lý ảnh | `opencv-python`, `numpy`, `Pillow` | Chuyển đổi ảnh, tăng contrast cho OCR |
| Chụp màn hình | `Pillow.ImageGrab` | Chụp toàn màn hình hoặc vùng chọn |

---

## Cài đặt

### Cách 1: Script tự động (Ubuntu/Debian)

```bash
chmod +x install.sh
./install.sh
```

Script sẽ tự động:
- Cài Tesseract OCR + gói ngôn ngữ tiếng Việt + Tkinter
- Tạo môi trường ảo (venv)
- Cài thư viện Python từ requirements.txt

### Cách 2: Cài thủ công

```bash
# 1. Cài đặt Tesseract OCR (hệ thống)
sudo apt update
sudo apt install -y tesseract-ocr tesseract-ocr-vie python3-tk python3-venv libtesseract-dev

# 2. Tạo và kích hoạt môi trường ảo
python3 -m venv venv
source venv/bin/activate

# 3. Cập nhật pip
pip install --upgrade pip setuptools wheel

# 4. Cài thư viện Python
pip install -r requirements.txt
```

---

## Cách sử dụng

```bash
# Kích hoạt môi trường ảo
source venv/bin/activate

# Chạy ứng dụng
python3 main.py
```

### Các bước thao tác

1. **Chọn vùng dịch**: Bấm nút `Chọn vùng dịch` → màn hình overlay hiện lên → kéo chuột chọn vùng chứa text cần dịch → thả chuột
2. **Xem kết quả**: Văn bản gốc (EN) và bản dịch (VI) hiển thị trong 2 khung text
3. **Dừng quét**: Bấm `Dừng quét` để ngừng capture
4. **Reload**: Bấm `Reload` để dịch lại vùng hiện tại ngay lập tức (không chờ 1.5s)
5. **Ghim cửa sổ**: Bấm `Tắt ghim cửa sổ` để bỏ always-on-top, bấm lại để bật

---

## Các vấn đề đã biết

1. **`googletrans` không ổn định**: Thường xuyên lỗi do Google thay đổi API. Dịch có thể ngừng hoạt động bất ngờ
2. **OCR tốn CPU**: Gọi Tesseract mỗi 1.5s kể cả khi màn hình không đổi
3. **Cửa sổ cố định kích thước**: Không co giãn tốt khi resize, khung text chỉ giãn ngang
4. **Cửa sổ vướng víu**: Luôn nổi trên màn hình, không có cách thu gọn hay làm trong suốt
5. **Cố định EN→VI**: Không đổi được ngôn ngữ nguồn/đích

---

## Kế hoạch nâng cấp (Chưa thực hiện)

### Đợt 1: Sửa lỗi + Tối ưu (Ưu tiên cao)

| # | Thay đổi | File ảnh hưởng | Mô tả |
|---|----------|----------------|-------|
| 1 | Đổi sang `argostranslate` | `core/translator_engine.py`, `requirements.txt`, `install.sh` | Dịch offline, ổn định. Lần đầu tải model ~50MB, sau đó không cần internet |
| 2 | So sánh screenshot trước OCR | `main.py` (hàm `capture_loop`) | Hash MD5 ảnh chụp, nếu giống lần trước thì skip OCR → tiết kiệm CPU |
| 3 | Cache bản dịch | `main.py` | Dùng dict lưu text→translation, tránh dịch lại cùng nội dung |
| 4 | Thread safety | `main.py` | Thêm `threading.Lock` cho `self.roi` và `self.is_capturing` |
| 5 | Cleanup khi thoát | `main.py` | Thêm `WM_DELETE_WINDOW` handler, join thread trước khi destroy |

### Đợt 2: Nâng cấp UI (Trải nghiệm)

| # | Thay đổi | File ảnh hưởng | Mô tả |
|---|----------|----------------|-------|
| 6 | Resize linh hoạt | `ui/main_window.py` | Đổi layout sang grid, ScrolledText co giãn cả ngang lẫn dọc |
| 7 | Thu gọn / Mở rộng | `ui/main_window.py` | Nút `▼ Thu gọn` ẩn toàn bộ, chỉ còn nút `▶ Mở rộng` nhỏ gọn |
| 8 | Điều chỉnh Opacity | `ui/main_window.py` | Slider kéo từ 20%→100% độ trong suốt, nhìn xuyên qua cửa sổ |
| 9 | Chế độ Compact | `ui/main_window.py` | Ẩn cột nút bên trái, chỉ hiện khung dịch + nút ≡ hamburger |

> Chi tiết kỹ thuật của từng thay đổi xem trong implementation_plan.md

---

## Git

```bash
# Repository
git remote: https://github.com/GiauLee/Realtime_translate.git
git branch: main
```