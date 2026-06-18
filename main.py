import tkinter as tk
from PIL import ImageGrab
import threading
import time
import hashlib

# Import từ các module bạn đã chia
from core.ocr_engine import detect_text
from core.translator_engine import MyTranslator
from ui.main_window import MainWindow
# Lưu ý: Bạn cần file ui/overlay.py để chọn vùng, tôi sẽ thêm logic tạm thời ở đây
from ui.overlay import ScreenSelector 

class ScreenTranslatorApp:
    def __init__(self):
        self.lock = threading.Lock()
        # 1. Khởi tạo các engine xử lý
        self.translator = MyTranslator()
        self.translation_cache = {}
        
        # 2. Khởi tạo Giao diện và truyền các hàm "callback" vào
        self.ui = MainWindow(
            on_start=self.handle_start,
            on_stop=self.handle_stop,
            on_reload=self.handle_reload,
            on_toggle_top=self.handle_toggle_top,
            on_engine_change=self.handle_engine_change
        )
        
        # 3. Các biến trạng thái
        self.is_capturing = False
        self.roi = None # Region of Interest (Vùng chọn)
        self.capture_thread = None

    # --- Các hàm xử lý Sự kiện từ Giao diện ---
    
    def handle_start(self):
        """Khi bấm nút 'Chọn vùng dịch'"""
        # Mở màn hình chọn vùng (Overlay)
        ScreenSelector(self.save_roi_and_start)

    def save_roi_and_start(self, bbox):
        """Callback nhận tọa độ từ Overlay và bắt đầu quét"""
        with self.lock:
            self.roi = bbox
            self.is_capturing = True
        self.ui.set_button_state(scanning=True) # Đổi màu/trạng thái nút
        
        # Chạy luồng quét trong background để không treo UI
        if self.capture_thread is None or not self.capture_thread.is_alive():
            self.capture_thread = threading.Thread(target=self.capture_loop, daemon=True)
            self.capture_thread.start()

    def handle_stop(self):
        """Khi bấm nút 'Dừng quét'"""
        with self.lock:
            self.is_capturing = False
        self.ui.set_button_state(scanning=False)

    def handle_reload(self):
        """Khi bấm nút 'Reload' để dịch lại vùng cũ ngay lập tức"""
        with self.lock:
            roi = self.roi
            
        if roi:
            screenshot = ImageGrab.grab(bbox=roi)
            text = detect_text(screenshot)
            
            if text in self.translation_cache:
                translated = self.translation_cache[text]
            else:
                translated = self.translator.translate(text)
                self.translation_cache[text] = translated
                
            self.ui.update_display(text, translated)

    def handle_toggle_top(self):
        """Khi bấm nút 'Ghim cửa sổ'"""
        self.ui.is_always_on_top = not self.ui.is_always_on_top
        self.ui.root.attributes('-topmost', self.ui.is_always_on_top)
        new_text = "Tắt ghim cửa sổ" if self.ui.is_always_on_top else "Bật ghim cửa sổ"
        self.ui.btn_top.config(text=new_text)

    def handle_engine_change(self, engine_name):
        """Khi user chọn engine dịch khác từ dropdown"""
        self.translator.set_engine(engine_name)
        # Xóa cache vì kết quả dịch sẽ khác
        self.translation_cache.clear()
        # Dịch lại ngay với engine mới nếu đang có vùng chọn
        self.handle_reload()

    # --- Luồng xử lý chính ---

    def capture_loop(self):
        last_text = ""
        last_img_hash = None
        
        while True:
            with self.lock:
                if not self.is_capturing:
                    break
                roi = self.roi
                
            if roi:
                try:
                    # 1. Chụp ảnh vùng đã chọn
                    screenshot = ImageGrab.grab(bbox=roi)
                    
                    # === SO SÁNH ẢNH TRƯỚC KHI OCR ===
                    img_bytes = screenshot.tobytes()
                    current_hash = hashlib.md5(img_bytes).hexdigest()
                    
                    if current_hash == last_img_hash:
                        time.sleep(1.5)
                        continue
                        
                    last_img_hash = current_hash
                    
                    # 2. Nhận diện chữ (OCR)
                    text = detect_text(screenshot)
                    
                    # 3. Nếu có chữ mới thì mới dịch (tiết kiệm API/CPU)
                    if text and text != last_text:
                        if text in self.translation_cache:
                            translated = self.translation_cache[text]
                        else:
                            translated = self.translator.translate(text)
                            self.translation_cache[text] = translated
                            
                        # 4. Cập nhật lên giao diện (dùng after để an toàn cho thread)
                        self.ui.root.after(0, self.ui.update_display, text, translated)
                        last_text = text
                except Exception as e:
                    print(f"Lỗi trong vòng lặp: {e}")
            
            time.sleep(1.5) # Quét mỗi 1.5 giây

    def run(self):
        self.ui.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.ui.run()

    def on_closing(self):
        with self.lock:
            self.is_capturing = False
        if self.capture_thread and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=3)
        self.ui.root.destroy()

if __name__ == "__main__":
    app = ScreenTranslatorApp()
    app.run()