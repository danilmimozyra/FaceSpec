import cv2
import threading
from concurrent.futures import ThreadPoolExecutor
from deepface import DeepFace
import render_utils
import time
"""
render_count = 0
render_fps = 0
last_time = time.time()
"""

analysis_results = []
analyzing = False
start_time = None

_executor = ThreadPoolExecutor(max_workers=4)

_face_cache = {}
_CACHE_TTL = 1.5


def _get_cache_key(x1, y1, x2, y2, tolerance=20):
    return (x1 // tolerance, y1 // tolerance, x2 // tolerance, y2 // tolerance)


def analyze_faces(frame):
    global analysis_results, analyzing, render_count, start_time, _face_cache

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

            result = r

            age = result["age"]
            gender = result["dominant_gender"]
            emotion = result["dominant_emotion"]

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
        print("Camera analyze error:", e)

    if results:
        analysis_results = results

        """
        render_count += 1

        if start_time is None:
            start_time = time.time()
        """

    analyzing = False


def run_camera():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    executor = ThreadPoolExecutor(max_workers=1)
    analysis_future = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if analysis_future is None or analysis_future.done():
            analysis_future = executor.submit(analyze_faces, frame.copy())

        for face in analysis_results:
            x1, y1, x2, y2 = face["region"]
            render_utils.draw_face_box(frame, x1, y1, x2, y2)
            label = f"{face['gender']}, {face['age']}, {face['emotion']}"
            render_utils.draw_face_label(frame, label, x1, y1, x2, y2)

        """
        global render_count, render_fps, last_time

        if start_time is not None:
            elapsed = time.time() - start_time

            if elapsed > 0:
                render_fps = render_count / elapsed
        else:
            render_fps = 0
        
        cv2.putText(
            frame,
            f"Render: {render_fps:.2f}/s",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )
        """

        cv2.imshow("Camera", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break
        if cv2.getWindowProperty("Camera", cv2.WND_PROP_VISIBLE) < 1:
            break

    executor.shutdown(wait=False)
    cap.release()
    cv2.destroyAllWindows()