python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

sudo apt install python3-tk python3-pil.imagetk tesseract-ocr tesseract-ocr-eng
pip install opencv-python pillow pytesseract googletrans-py numpy
pip install argostranslate

# how to run
python3 realtime_translator.py

# Bước 1: Tạo và kích hoạt venv
python3 -m venv venv
source venv/bin/activate

# Bước 2: Cài đặt thư viện
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
# Lưu ý: argostranslate==1.9.1 có thể cần thêm các dependency hệ thống
sudo apt install -y python3-gi gir1.2-gtk-3.0 libopenblas-dev

# Bước 3: Chạy chương trình
python realtime_translator.py
pip install googletrans==4.0.0rc1

# Tạo github
```bash
cd /duong/dan/den/thu-muc-cua-ban
git init

git add .

git commit -m "Initial commit"

git branch -M main

git remote add origin https://github.com/GiauLee/Realtime_translate.git

git push -u origin main
```