import tkinter as tk
from PIL import Image, ImageGrab, ImageTk
import threading
import time
import pytesseract
from googletrans import Translator
import cv2
import numpy as np

class ScreenTranslator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Screen Translator")
        self.root.geometry("630x200")
        self.root.attributes('-topmost', True)
        self.always_on_top = True

        self.translator = Translator()
        self.is_capturing = False
        self.roi = None
        self.capture_thread = None

        self.setup_ui()

    # ---------------- Giao diện ----------------
    def setup_ui(self):
        self.left_frame = tk.Frame(self.root)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        self.start_btn = tk.Button(self.left_frame, text="Chọn vùng cần dịch", command=self.start_selection, width=15)
        self.start_btn.pack(pady=5)
        
        self.stop_btn = tk.Button(self.left_frame, text="Dừng capture", command=self.stop_capture, state=tk.DISABLED, width=15)
        self.stop_btn.pack(pady=5)

        self.reload_btn = tk.Button(self.left_frame, text="Reload", command=self.reload_capture, width=15)
        self.reload_btn.pack(pady=5)

        self.toggle_top_btn = tk.Button(self.left_frame, text="Tắt màn hình nổi", command=self.toggle_always_on_top, width=15)
        self.toggle_top_btn.pack(pady=5)

        self.right_frame = tk.Frame(self.root)
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.original_text = tk.Text(self.right_frame, height=5)
        self.original_text.pack(fill=tk.X, pady=2)
        
        self.translated_text = tk.Text(self.right_frame, height=5, bg="#f0f0f0")
        self.translated_text.pack(fill=tk.X, pady=2)

    # ---------------- Chọn vùng ----------------
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
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline='red', width=2
        )

    def on_move_press(self, event):
        self.sel_canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    def on_button_release(self, event):
        x1, y1 = self.start_x, self.start_y
        x2, y2 = event.x, event.y
        self.roi = (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))
        self.sel_window.destroy()
        self.start_capture()

    # ---------------- Capture ----------------
    def start_capture(self):
        if self.capture_thread and self.capture_thread.is_alive():
            return  # tránh tạo nhiều luồng
        self.capture_thread = threading.Thread(target=self.capture_loop, daemon=True)
        self.capture_thread.start()

    def capture_loop(self):
        last_text = ""
        while self.is_capturing:
            if self.roi:
                screenshot = ImageGrab.grab(bbox=self.roi)
                text = self.detect_text_in_roi(screenshot)
                if text and text != last_text:
                    last_text = text
                    self.root.after(0, self.update_translation, text)
            time.sleep(1)

    # ---------------- Phát hiện chữ ----------------
    def detect_text_in_roi(self, image):
        cv_img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        gray = cv2.convertScaleAbs(gray, alpha=1.3, beta=5)  # tăng nhẹ contrast

        data = pytesseract.image_to_data(gray, lang='eng', output_type=pytesseract.Output.DICT)

        lines = []
        for i in range(len(data['text'])):
            if int(data['conf'][i]) > 60:
                text = data['text'][i].strip()
                if text:
                    lines.append(text)
        return " ".join(lines)

    # ---------------- Reload vùng ----------------
    def reload_capture(self):
        if not self.roi:
            self.original_text.delete(1.0, tk.END)
            self.translated_text.delete(1.0, tk.END)
            self.original_text.insert(tk.END, "(Chưa có vùng nào được chọn)")
            return

        screenshot = ImageGrab.grab(bbox=self.roi)
        text = self.detect_text_in_roi(screenshot)
        if text:
            self.update_translation(text)
        else:
            self.original_text.delete(1.0, tk.END)
            self.translated_text.delete(1.0, tk.END)
            self.original_text.insert(tk.END, "(Không phát hiện được chữ)")

    # ---------------- Dịch ----------------
    def update_translation(self, text):
        self.original_text.delete(1.0, tk.END)
        self.translated_text.delete(1.0, tk.END)
        self.original_text.insert(tk.END, text)
        try:
            translated_text = self.translator.translate(text, src='en', dest='vi').text
        except Exception:
            translated_text = "(Lỗi khi dịch)"
        self.translated_text.insert(tk.END, translated_text)

    # ---------------- Các chức năng phụ ----------------
    def stop_capture(self):
        self.is_capturing = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

    def toggle_always_on_top(self):
        self.always_on_top = not self.always_on_top
        self.root.attributes('-topmost', self.always_on_top)
        if self.always_on_top:
            self.toggle_top_btn.config(text="Tắt nổi màn hình")
        else:
            self.toggle_top_btn.config(text="Bật nổi màn hình")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = ScreenTranslator()
    app.run()
