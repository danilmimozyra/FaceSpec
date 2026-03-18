import cv2
import numpy as np


def draw_face_box(frame, x1, y1, x2, y2):

    w = x2 - x1
    h = y2 - y1

    thickness = max(2, int(min(w, h) / 120))

    cv2.rectangle(
        frame,
        (x1, y1),
        (x2, y2),
        (0, 255, 255),
        thickness
    )


def draw_face_label(frame, text, x1, y1, x2, y2):

    box_width = x2 - x1

    font = cv2.FONT_HERSHEY_SIMPLEX

    font_scale = max(0.5, box_width / 300)

    thickness = max(1, int(font_scale * 2))

    (text_w, text_h), _ = cv2.getTextSize(text, font, font_scale, thickness)

    if text_w > box_width:
        font_scale = font_scale * (box_width / text_w)
        (text_w, text_h), _ = cv2.getTextSize(text, font, font_scale, thickness)

    text_x = x1 + (box_width - text_w) // 2

    if y1 - text_h - 10 > 0:
        text_y = y1 - 10
    else:
        text_y = y2 + text_h + 10

    cv2.putText(
        frame,
        text,
        (text_x, text_y),
        font,
        font_scale,
        (0, 255, 255),
        thickness,
        cv2.LINE_AA
    )
