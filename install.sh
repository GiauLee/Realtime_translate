#!/bin/bash

echo "--- Bắt đầu cài đặt Realtime Screen Translator ---"

# 1. Cài đặt các gói hệ thống (Cần thiết để chạy giao diện và OCR trên Linux)
echo "[1/4] Đang cài đặt Tesseract và Tkinter từ kho ứng dụng Ubuntu..."
sudo apt update
sudo apt install -y tesseract-ocr tesseract-ocr-vie python3-tk python3-venv libtesseract-dev

# 2. Tạo môi trường ảo (venv)
echo "[2/4] Kiểm tra và tạo môi trường ảo venv..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Đã tạo venv thành công."
fi

# 3. Cài đặt từ file requirements.txt
echo "[3/4] Đang cài đặt các thư viện Python từ requirements.txt..."
source venv/bin/activate
pip install --upgrade pip

if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "Đã cài đặt xong các thư viện từ requirements.txt."
else
    echo "LỖI: Không tìm thấy file requirements.txt! Đang cài thủ công các gói cơ bản..."
    pip install pytesseract argostranslate pillow opencv-python numpy
fi

echo "--- CÀI ĐẶT HOÀN TẤT! ---"
echo "Để chạy ứng dụng, hãy gõ: source venv/bin/activate && python3 main.py"