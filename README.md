# install
```bash
# 1. Tạo và kích hoạt môi trường (nếu chưa làm)
python3 -m venv venv
source venv/bin/activate

# 2. Cập nhật công cụ cài đặt TRƯỚC (Bước quan trọng)
pip install --upgrade pip setuptools wheel

# 3. Sau đó mới cài thư viện từ file
pip install -r requirements.txt
```

# how to run
```bash
python3 realtime_translator.py
```

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