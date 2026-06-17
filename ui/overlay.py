import tkinter as tk
from PIL import ImageGrab, ImageTk

class ScreenSelector:
    def __init__(self, callback):
        self.callback = callback
        self.root = tk.Toplevel()
        
        # 1. Chụp ảnh màn hình ngay lập tức để làm nền
        # Điều này giúp bạn thấy rõ những gì đang diễn ra bên dưới
        self.screen_snapshot = ImageGrab.grab()
        self.tk_image = ImageTk.PhotoImage(self.screen_snapshot)

        # 2. Cấu hình cửa sổ phủ toàn màn hình
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)
        
        # 3. Tạo Canvas và dán ảnh màn hình lên đó
        self.canvas = tk.Canvas(self.root, cursor="cross", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)

        # Thêm một lớp phủ mờ nhẹ để biết là đang trong chế độ chọn
        self.canvas.create_rectangle(
            0, 0, self.root.winfo_screenwidth(), self.root.winfo_screenheight(),
            fill="black", stipple="gray25", state="disabled" 
        )

        self.start_x = None
        self.start_y = None
        self.rect = None

        # Bind các sự kiện
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.root.bind("<Escape>", lambda e: self.root.destroy())

    def on_button_press(self, event):
        self.start_x, self.start_y = event.x, event.y
        # Vẽ hình chữ nhật với viền đỏ nổi bật
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y, 
            outline='red', width=3
        )

    def on_move_press(self, event):
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    def on_button_release(self, event):
        x1, y1, x2, y2 = self.canvas.coords(self.rect)
        self.root.destroy()
        
        # Đảm bảo x1, y1 luôn là góc trên bên trái
        final_bbox = (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))
        
        if (final_bbox[2] - final_bbox[0]) > 5:
            self.callback(final_bbox)