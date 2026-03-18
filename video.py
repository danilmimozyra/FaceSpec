import cv2
from tkinter import filedialog
from concurrent.futures import ThreadPoolExecutor
from deepface import DeepFace
import render_utils
import time

analysis_results = []
analyzing = False
paused = False

_executor = ThreadPoolExecutor(max_workers=1)

_face_cache = {}
_CACHE_TTL = 1.5


def _get_cache_key(x1, y1, x2, y2, tolerance=20):
    return (x1 // tolerance, y1 // tolerance, x2 // tolerance, y2 // tolerance)


def analyze_faces(frame):

    global analysis_results, analyzing, _face_cache

    analyzing = True
    results = []

    try:
        now = time.time()

        for k in list(_face_cache.keys()):
            _, ts = _face_cache[k]
            if now - ts > _CACHE_TTL:
                del _face_cache[k]

        scale = 0.6
        small_frame = cv2.resize(frame, (0, 0), fx=scale, fy=scale)

        raw = DeepFace.analyze(
            small_frame,
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

            cache_key = _get_cache_key(x1, y1, x2, y2)

            cached = _face_cache.get(cache_key)

            if cached:
                data, ts = cached

                if now - ts < _CACHE_TTL:
                    results.append({
                        "region": (x1, y1, x2, y2),
                        "age": data["age"],
                        "gender": data["gender"],
                        "emotion": data["emotion"]
                    })
                    continue

            age = r["age"]
            gender = r["dominant_gender"]
            emotion = r["dominant_emotion"]

            _face_cache[cache_key] = ({
                "age": age,
                "gender": gender,
                "emotion": emotion
            }, now)

            results.append({
                "region": (x1, y1, x2, y2),
                "age": age,
                "gender": gender,
                "emotion": emotion
            })

    except Exception as e:
        print("Video analyze error:", e)

    if results:
        analysis_results = results

    analyzing = False


def draw_loading_screen(frame):

    ui_height = 80
    h, w = frame.shape[:2]

    canvas = cv2.copyMakeBorder(
        frame,
        0, ui_height, 0, 0,
        cv2.BORDER_CONSTANT,
        value=(30, 30, 30)
    )

    cv2.putText(
        canvas,
        "Loading AI...",
        (w//2 - 120, h//2),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (200, 200, 200),
        2
    )

    return canvas


def warmup_models():
    import numpy as np

    dummy = np.zeros((224, 224, 3), dtype="uint8")

    DeepFace.analyze(
        dummy,
        actions=['age', 'gender', 'emotion'],
        enforce_detection=False,
        silent=True
    )


def run_video():

    global paused

    video_path = filedialog.askopenfilename(
        filetypes=[("Video files", "*.mp4 *.avi *.mov")]
    )

    if not video_path:
        return

    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    ret, frame = cap.read()
    if not ret:
        cap.release()
        return

    loading_screen = draw_loading_screen(frame)

    cv2.imshow("Video Analyzer", loading_screen)
    cv2.waitKey(1)

    warmup_models()

    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    analysis_future = None

    while True:

        if not paused:

            ret, new_frame = cap.read()

            if ret:
                frame = new_frame
            else:
                paused = True

            if analysis_future is None or analysis_future.done():
                analysis_future = _executor.submit(analyze_faces, frame.copy())

        display_frame = frame.copy()

        for face in analysis_results:

            x1, y1, x2, y2 = face["region"]

            render_utils.draw_face_box(display_frame, x1, y1, x2, y2)

            label = f"{face['gender']}, {face['age']}, {face['emotion']}"

            render_utils.draw_face_label(display_frame, label, x1, y1, x2, y2)

        """UI"""

        ui_height = 80
        h, w = display_frame.shape[:2]

        canvas = cv2.copyMakeBorder(
            display_frame,
            0, ui_height, 0, 0,
            cv2.BORDER_CONSTANT,
            value=(30, 30, 30)
        )

        current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))

        progress = current_frame / total_frames if total_frames > 0 else 0

        bar_width = int(w * 0.8)
        bar_x = (w - bar_width) // 2
        bar_y = h + 20

        cv2.rectangle(canvas,
                      (bar_x, bar_y),
                      (bar_x + bar_width, bar_y + 10),
                      (80, 80, 80),
                      -1)

        cv2.rectangle(canvas,
                      (bar_x, bar_y),
                      (bar_x + int(bar_width * progress), bar_y + 10),
                      (0, 255, 255),
                      -1)

        import numpy as np

        cx = w // 2
        cy = h + 55
        size = 12

        if paused:
            pts = np.array([
                (cx - size, cy - size),
                (cx - size, cy + size),
                (cx + size, cy)
            ], np.int32)

            cv2.fillConvexPoly(canvas, pts, (200, 200, 200))
        else:
            cv2.rectangle(canvas, (cx - 10, cy - 12), (cx - 3, cy + 12), (200, 200, 200), -1)
            cv2.rectangle(canvas, (cx + 3, cy - 12), (cx + 10, cy + 12), (200, 200, 200), -1)

        cv2.imshow("Video Analyzer", canvas)

        key = cv2.waitKey(30) & 0xFF

        if key == 27:
            break

        elif key == 32:
            paused = not paused

        elif key == ord("s"):
            paused = True
            file_path = filedialog.asksaveasfilename(
                defaultextension=".jpg",
                filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png")]
            )

            if file_path:
                cv2.imwrite(file_path, display_frame)
                print("Frame saved")

        elif key == ord("d"):
            current = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
            cap.set(cv2.CAP_PROP_POS_FRAMES, min(current + 30, total_frames))
            analysis_results.clear()

        elif key == ord("a"):
            current = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
            cap.set(cv2.CAP_PROP_POS_FRAMES, max(current - 30, 0))
            analysis_results.clear()

        if cv2.getWindowProperty("Video Analyzer", cv2.WND_PROP_VISIBLE) < 1:
            break

    cap.release()
    cv2.destroyAllWindows()