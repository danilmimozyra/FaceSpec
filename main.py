import tkinter as tk
import camera
import photo
import video

root = tk.Tk()
root.title("Face Analyzer")
root.geometry("420x320")
root.configure(bg="#1e1e1e")


def open_camera():
    root.withdraw()
    camera.run_camera()
    root.deiconify()


def open_photo():
    root.withdraw()
    photo.PhotoWindow(root)


def open_video():
    root.withdraw()
    video.run_video()
    root.deiconify()


label = tk.Label(
    root,
    text="Face Analyzer",
    font=("Arial", 20, "bold"),
    fg="#f5c542",
    bg="#1e1e1e"
)
label.pack(pady=(30, 20))

btn_style = {
    "font": ("Arial", 12),
    "width": 20,
    "height": 2,
    "bg": "#2b2b2b",
    "fg": "#e0e0e0",
    "activebackground": "#f5c542",
    "activeforeground": "#000000",
    "bd": 0,
    "relief": "flat",
    "cursor": "hand2"
}


btn_camera = tk.Button(root, text="Camera", command=open_camera, **btn_style)
btn_camera.pack(pady=8)

btn_photo = tk.Button(root, text="Photo", command=open_photo, **btn_style)
btn_photo.pack(pady=8)

btn_video = tk.Button(root, text="Video", command=open_video, **btn_style)
btn_video.pack(pady=8)


root.mainloop()