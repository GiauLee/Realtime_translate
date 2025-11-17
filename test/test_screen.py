import tkinter as tk
from PIL import Image, ImageGrab, ImageTk, ImageOps, ImageEnhance
import threading
import time
import pytesseract
from googletrans import Translator

class ScreenTranslator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Screen Translator")
        self.root.geometry("630x180")
        self.root.attributes('-topmost', True)
        self.always_on_top = True

        self.translator = Translator()
        self.is_capturing = False
        self.roi = None
        self.capture_thread = None

        self.setup_ui()

    # --- Setup UI ---
    def setup_ui(self):
        # Khung nút bên trái
        self.left_frame = tk.Frame(self.root)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        self.start_btn = tk.Button(self.left_frame, text="Bắt đầu chọn vùng", command=self.start_selection, width=15)
        self.start_btn.pack(pady=5)

        self.stop_btn = tk.Button(self.left_frame, text="Dừng capture", command=self.stop_capture, state=tk.DISABLED, width=15)
        self.stop_btn.pack(pady=5)

        self.toggle_top_btn = tk.Button(self.left_frame, text="Tắt nổi màn hình", command=self.toggle_always_on_top, width=15)
        self.toggle_top_btn.pack(pady=5)

        # Khung ô hiển thị bên phải
        self.right_frame = tk.Frame(self.root)
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.original_text = tk.Text(self.right_frame, height=5)
        self.original_text.pack(fill=tk.X, pady=2)

        self.translated_text = tk.Text(self.right_frame, height=5, bg="#f0f0f0")
        self.translated_text.pack(fill=tk.X, pady=2)

    # --- Khoanh vùng ---
    def start_selection(self):
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.is_capturing = True

        screen = ImageGrab.grab()
        self.screen_img = ImageTk.PhotoImage(screen)

        self.sel_window = tk.Toplevel(self.root)
        self.sel_window.attributes('-fullscreen', True)
        self.sel_window.attributes('-topmost', True)
        self.sel_canvas = tk.Canvas(self.sel_window, cursor="cross")
        self.sel_canvas.pack(fill=tk.BOTH, expand=True)
        self.sel_canvas.create_image(0, 0, anchor="nw", image=self.screen_img)

        self.sel_canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.sel_canvas.bind("<B1-Motion>", self.on_move_press)
        self.sel_canvas.bind("<ButtonRelease-1>", self.on_button_release)

        self.rect = None
        self.start_x = self.start_y = 0

    def on_button_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.rect = self.sel_canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y, outline='red', width=2
        )

    def on_move_press(self, event):
        self.sel_canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    def on_button_release(self, event):
        x1, y1 = self.start_x, self.start_y
        x2, y2 = event.x, event.y
        self.roi = (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))
        self.sel_window.destroy()
        self.start_capture()

    # --- Capture loop ---
    def start_capture(self):
        self.capture_thread = threading.Thread(target=self.capture_loop, daemon=True)
        self.capture_thread.start()

    def capture_loop(self):
        last_text = ""
        while self.is_capturing:
            if self.roi:
                screenshot = ImageGrab.grab(bbox=self.roi)
                text = self.preprocess_and_ocr(screenshot)
                if text and text != last_text:
                    last_text = text
                    self.root.after(0, self.update_translation, text)
            time.sleep(1)

    # --- Preprocess for OCR (optimized for dynamic background, minimal distortion) ---
    def preprocess_and_ocr(self, image):
        # 1. Grayscale
        gray = ImageOps.grayscale(image)
        # 2. Enhance contrast vừa phải
        gray = ImageEnhance.Contrast(gray).enhance(1.8)
        # 3. Resize nếu chữ nhỏ
        scale = 2
        w, h = gray.size
        gray = gray.resize((w*scale, h*scale), Image.LANCZOS)
        # 4. OCR với config chuẩn
        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(gray, lang='eng', config=custom_config).strip()
        return text

    # --- Update UI ---
    def update_translation(self, text):
        self.original_text.delete(1.0, tk.END)
        self.translated_text.delete(1.0, tk.END)
        self.original_text.insert(tk.END, text)
        translated_text = self.translator.translate(text, src='en', dest='vi').text
        self.translated_text.insert(tk.END, translated_text)

    # --- Control buttons ---
    def stop_capture(self):
        self.is_capturing = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

    def toggle_always_on_top(self):
        self.always_on_top = not self.always_on_top
        self.root.attributes('-topmost', self.always_on_top)
        self.toggle_top_btn.config(text="Tắt nổi màn hình" if self.always_on_top else "Bật nổi màn hình")

    # --- Run app ---
    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = ScreenTranslator()
    app.run()
