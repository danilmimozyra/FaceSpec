import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import cv2
from deepface import DeepFace
import render_utils


class PhotoWindow:
    def __init__(self, root):
        self.root = root

        self.window = tk.Toplevel()
        self.window.title("Photo Analyzer")
        self.window.geometry("420x320")
        self.window.configure(bg="#1e1e1e")

        self.window.bind("<Escape>", self.close_window)
        self.window.protocol("WM_DELETE_WINDOW", self.close_window)

        self.window.bind("u", lambda e: self.load_photo())
        self.window.bind("s", lambda e: self.save_image())

        self.container = tk.Frame(self.window, bg="#1e1e1e")
        self.container.pack(expand=True)

        self.title = tk.Label(
            self.container,
            text="Photo Analyzer",
            font=("Arial", 18, "bold"),
            fg="#f5c542",
            bg="#1e1e1e"
        )
        self.title.pack(pady=(20, 15))

        self.image_label = tk.Label(self.container, bg="#1e1e1e")
        self.image_label.pack(pady=10)

        btn_style = {
            "font": ("Arial", 12),
            "width": 18,
            "height": 2,
            "bg": "#2b2b2b",
            "fg": "#e0e0e0",
            "activebackground": "#f5c542",
            "activeforeground": "#000000",
            "bd": 0,
            "relief": "flat",
            "cursor": "hand2"
        }

        self.btn_upload = tk.Button(
            self.container,
            text="Upload Photo",
            command=self.load_photo,
            **btn_style
        )
        self.btn_upload.pack(pady=8)

        self.btn_save = tk.Button(
            self.container,
            text="Save Image",
            command=self.save_image,
            state=tk.DISABLED,
            **btn_style
        )
        self.btn_save.pack(pady=8)

        self.result_image = None

    def close_window(self, event=None):
        self.window.destroy()
        self.root.deiconify()

    def load_photo(self):

        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png")]
        )

        if not file_path:
            return

        image = cv2.imread(file_path)

        try:
            scale = 0.6
            small = cv2.resize(image, (0, 0), fx=scale, fy=scale)

            raw = DeepFace.analyze(
                small,
                actions=['age', 'gender', 'emotion'],
                enforce_detection=False,
                silent=True,
                detector_backend='opencv'
            )

            if not isinstance(raw, list):
                raw = [raw]

            for r in raw:
                region = r.get("region", {})

                x1 = max(0, int(region.get("x", 0) / scale))
                y1 = max(0, int(region.get("y", 0) / scale))
                x2 = int((region.get("x", 0) + region.get("w", 0)) / scale)
                y2 = int((region.get("y", 0) + region.get("h", 0)) / scale)

                age = r["age"]
                gender = r["dominant_gender"]
                emotion = r["dominant_emotion"]

                render_utils.draw_face_box(image, x1, y1, x2, y2)

                label = f"{gender}, {age}, {emotion}"

                render_utils.draw_face_label(image, label, x1, y1, x2, y2)

        except Exception as e:
            print("Photo analyze error:", e)

        self.result_image = image

        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb)

        img.thumbnail((800, 600))

        imgtk = ImageTk.PhotoImage(img)

        self.image_label.configure(image=imgtk)
        self.image_label.image = imgtk

        self.window.geometry("900x700")

        self.btn_save.config(state=tk.NORMAL)

    def save_image(self):

        if self.result_image is None:
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".jpg",
            filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png")]
        )

        if file_path:
            cv2.imwrite(file_path, self.result_image)