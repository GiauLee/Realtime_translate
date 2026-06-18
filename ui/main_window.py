import tkinter as tk
from tkinter import scrolledtext, ttk

class MainWindow:
    def __init__(self, on_start, on_stop, on_reload, on_toggle_top, on_engine_change=None):
        self.root = tk.Tk()
        self.root.title("Realtime Screen Translator")
        self.root.geometry("650x300")
        self.root.minsize(400, 200)
        self.root.attributes('-topmost', True)
        self.is_always_on_top = True

        # Lưu lại các hàm xử lý từ main.py
        self.on_start = on_start
        self.on_stop = on_stop
        self.on_reload = on_reload
        self.on_toggle_top = on_toggle_top
        self.on_engine_change = on_engine_change

        self.is_collapsed = False
        self.saved_geometry = None
        self.is_compact = False

        self._setup_ui()

    def _setup_ui(self):
        # --- Cột trái: Các nút điều khiển ---
        self.left_frame = tk.Frame(self.root, width=150)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        self.btn_start = tk.Button(self.left_frame, text="Chọn vùng dịch", command=self.on_start, width=15, bg="#4CAF50", fg="white")
        self.btn_start.pack(pady=5)
        
        self.btn_stop = tk.Button(self.left_frame, text="Dừng quét", command=self.on_stop, width=15, state=tk.DISABLED)
        self.btn_stop.pack(pady=5)

        self.btn_reload = tk.Button(self.left_frame, text="Reload", command=self.on_reload, width=15)
        self.btn_reload.pack(pady=5)
        
        # --- Engine selector ---
        self.engine_label = tk.Label(self.left_frame, text="Engine dịch:", font=("Arial", 8))
        self.engine_label.pack(pady=(10, 2))
        self.engine_var = tk.StringVar(value="Argos (Offline)")
        self.engine_combo = ttk.Combobox(
            self.left_frame, textvariable=self.engine_var,
            values=["Argos (Offline)", "Google (Online)"],
            state="readonly", width=15
        )
        self.engine_combo.pack(pady=(0, 5))
        self.engine_combo.bind("<<ComboboxSelected>>", self._on_engine_selected)

        self.btn_top = tk.Button(self.left_frame, text="Tắt ghim cửa sổ", command=self.on_toggle_top, width=15)
        self.btn_top.pack(pady=5)

        self.btn_compact = tk.Button(self.left_frame, text="◀ Compact", command=self.toggle_compact, width=15)
        self.btn_compact.pack(pady=5)

        self.btn_collapse = tk.Button(self.left_frame, text="▼ Thu gọn", command=self.toggle_collapse, width=15)
        self.btn_collapse.pack(pady=5)

        # --- Bottom: Opacity slider ---
        self.bottom_frame = tk.Frame(self.root)
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(0, 5))
        
        tk.Label(self.bottom_frame, text="Opacity:").pack(side=tk.LEFT)
        
        self.opacity_slider = tk.Scale(
            self.bottom_frame, from_=0.2, to=1.0, resolution=0.05,
            orient=tk.HORIZONTAL, showvalue=False, length=150,
            command=self.on_opacity_change
        )
        self.opacity_slider.set(1.0)
        self.opacity_slider.pack(side=tk.LEFT, padx=5)
        
        self.opacity_label = tk.Label(self.bottom_frame, text="100%")
        self.opacity_label.pack(side=tk.LEFT)

        # --- Cột phải: Hiển thị văn bản ---
        self.right_frame = tk.Frame(self.root)
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Nút hamburger - ẩn ban đầu, chỉ hiện khi compact
        self.btn_hamburger = tk.Button(self.right_frame, text="≡", font=("Arial", 12, "bold"),
                                       command=self.toggle_compact, width=2, relief=tk.FLAT)

        self.right_frame.grid_rowconfigure(1, weight=1)
        self.right_frame.grid_rowconfigure(3, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)
        
        tk.Label(self.right_frame, text="Văn bản gốc (EN):").grid(row=0, column=0, sticky="w")
        self.txt_original = scrolledtext.ScrolledText(self.right_frame, height=5, font=("Arial", 10))
        self.txt_original.grid(row=1, column=0, sticky="nsew", pady=2)
        
        self.lbl_translated = tk.Label(self.right_frame, text="Bản dịch (VI) — Argos (Offline):")
        self.lbl_translated.grid(row=2, column=0, sticky="w")
        self.txt_translated = scrolledtext.ScrolledText(self.right_frame, height=5, bg="#f0f8ff", font=("Arial", 10, "bold"))
        self.txt_translated.grid(row=3, column=0, sticky="nsew", pady=2)

    def _on_engine_selected(self, event):
        """Xử lý khi user chọn engine dịch khác"""
        selected = self.engine_var.get()
        engine_name = "argos" if "Argos" in selected else "google"
        self.lbl_translated.config(text=f"Bản dịch (VI) — {selected}:")
        if self.on_engine_change:
            self.on_engine_change(engine_name)

    def on_opacity_change(self, value):
        opacity = float(value)
        self.root.attributes('-alpha', opacity)
        self.opacity_label.config(text=f"{int(opacity * 100)}%")

    def toggle_collapse(self):
        if not self.is_collapsed:
            self.saved_geometry = self.root.geometry()
            self.right_frame.pack_forget()
            self.bottom_frame.pack_forget()
            for widget in self.left_frame.winfo_children():
                if widget != self.btn_collapse:
                    widget.pack_forget()
            self.btn_collapse.config(text="▶ Mở rộng")
            self.root.geometry("")  
            self.is_collapsed = True
        else:
            self.btn_start.pack(pady=5)
            self.btn_stop.pack(pady=5)
            self.btn_reload.pack(pady=5)
            # Re-pack engine selector
            self.engine_label.pack(pady=(10, 2))
            self.engine_combo.pack(pady=(0, 5))
            self.btn_top.pack(pady=5)
            self.btn_compact.pack(pady=5)
            self.btn_collapse.pack(pady=5)
            
            self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(0, 5))
            self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
            if self.saved_geometry:
                self.root.geometry(self.saved_geometry)
            self.btn_collapse.config(text="▼ Thu gọn")
            self.is_collapsed = False

    def toggle_compact(self):
        if not self.is_compact:
            self.left_frame.pack_forget()
            self.btn_hamburger.grid(row=0, column=1, sticky="ne")
            self.is_compact = True
        else:
            self.btn_hamburger.grid_forget()
            self.right_frame.pack_forget()
            self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
            self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
            self.is_compact = False

    def update_display(self, original, translated):
        """Cập nhật dữ liệu vào các ô text"""
        self.txt_original.delete(1.0, tk.END)
        self.txt_original.insert(tk.END, original)
        
        self.txt_translated.delete(1.0, tk.END)
        self.txt_translated.insert(tk.END, translated)
        
        # Tự động cuộn xuống cuối
        self.txt_original.see(tk.END)
        self.txt_translated.see(tk.END)

    def set_button_state(self, scanning=False):
        """Đổi trạng thái nút bấm khi đang chạy hoặc dừng"""
        if scanning:
            self.btn_start.config(state=tk.DISABLED)
            self.btn_stop.config(state=tk.NORMAL)
        else:
            self.btn_start.config(state=tk.NORMAL)
            self.btn_stop.config(state=tk.DISABLED)

    def run(self):
        self.root.mainloop()