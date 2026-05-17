import argparse
import math
import os
import time
from dataclasses import dataclass
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
MPL_CACHE_DIR = PROJECT_DIR / ".matplotlib"
MPL_CACHE_DIR.mkdir(exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MPL_CACHE_DIR))

import cv2
import mediapipe as mp
import numpy as np


COLORS = ((30, 210, 255), (80, 220, 120), (255, 120, 80), (230, 90, 230), (255, 255, 255))
PINCH = 0.34
FINGER_MARGIN = 0.015
THUMB_MARGIN = 0.025
SMOOTHING = 0.65


@dataclass(slots=True)
class Hand:
    label: str
    score: float
    index_tip: tuple[int, int]
    origin: tuple[int, int]
    pointer: bool
    control_action: str
    pinches: tuple[bool, bool, bool, bool]


@dataclass(slots=True)
class State:
    color_id: int = 0
    brush: int = 8
    mode: str = "ready"
    last_tool_time: float = 0.0
    last_clear_time: float = 0.0
    last_draw: tuple[int, int] | None = None
    last_erase: tuple[int, int] | None = None
    point: tuple[int, int] | None = None

    @property
    def color(self):
        return COLORS[self.color_id]

    def reset_line(self):
        self.last_draw = self.last_erase = self.point = None

    def smooth(self, point):
        if self.point is None:
            self.point = point
            return point
        x, y = self.point
        px, py = point
        self.point = (int(x * SMOOTHING + px * (1 - SMOOTHING)), int(y * SMOOTHING + py * (1 - SMOOTHING)))
        return self.point


def parse_args():
    parser = argparse.ArgumentParser(description="Two-hand gesture drawing.")
    parser.add_argument("--camera", type=int, default=0)
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--height", type=int, default=720)
    parser.add_argument("--max-hands", type=int, default=2)
    parser.add_argument("--model-complexity", type=int, choices=(0, 1), default=0)
    parser.add_argument("--min-detection-confidence", type=float, default=0.7)
    parser.add_argument("--min-tracking-confidence", type=float, default=0.6)
    parser.add_argument("--hide-landmarks", action="store_true")
    parser.add_argument("--draw-hand", choices=("Left", "Right"), default="Right")
    parser.add_argument("--control-hand", choices=("Left", "Right"), default="Left")
    return parser.parse_args()


def mediapipe_solutions():
    try:
        return mp.solutions.hands, mp.solutions.drawing_utils, mp.solutions.drawing_styles
    except AttributeError as error:
        version = getattr(mp, "__version__", "unknown")
        raise RuntimeError(
            f"mediapipe {version} does not provide mp.solutions. Use Python 3.12 and reinstall:\n"
            "  deactivate\n  rm -rf .venv\n  python3.12 -m venv .venv\n"
            "  source .venv/bin/activate\n  python -m pip install -r requirements.txt"
        ) from error


def dist(points, a, b):
    pa, pb = points[a], points[b]
    return math.hypot(pa.x - pb.x, pa.y - pb.y)


def analyze(hand_landmarks, handedness, width, height):
    lm = hand_landmarks.landmark
    category = handedness.classification[0]
    label = category.label
    thumb = lm[4].x < lm[3].x - THUMB_MARGIN if label == "Right" else lm[4].x > lm[3].x + THUMB_MARGIN
    fingers = (
        thumb,
        lm[8].y < lm[6].y - FINGER_MARGIN,
        lm[12].y < lm[10].y - FINGER_MARGIN,
        lm[16].y < lm[14].y - FINGER_MARGIN,
        lm[20].y < lm[18].y - FINGER_MARGIN,
    )
    palm = max(dist(lm, 0, 9), 0.001)
    pinches = tuple(dist(lm, 4, tip) / palm < PINCH for tip in (8, 12, 16, 20))
    control_action = "none"
    if pinches[0]:
        control_action = "draw"
    elif pinches[1]:
        control_action = "erase"
    elif pinches[2]:
        control_action = "color"
    elif pinches[3]:
        control_action = "clear"
    elif fingers[0] and not any(fingers[1:]):
        control_action = "brush+"
    elif fingers[4] and not any(fingers[:4]):
        control_action = "brush-"

    x0 = max(0, int(min(p.x for p in lm) * width) - 16)
    y0 = max(32, int(min(p.y for p in lm) * height) - 16)
    return Hand(label, category.score, (int(lm[8].x * width), int(lm[8].y * height)), (x0, y0), fingers[1], control_action, pinches)


def text(frame, value, origin, size=0.62, color=(255, 255, 255), thickness=1):
    cv2.putText(frame, value, origin, cv2.FONT_HERSHEY_SIMPLEX, size, color, thickness, cv2.LINE_AA)


def draw_info(frame, hand, role):
    names = "IMRP"
    closed = "".join(name for name, is_closed in zip(names, hand.pinches) if is_closed) or "-"
    pointer = "pointer" if hand.pointer else "-"
    text(frame, f"{role}: {hand.label} | {pointer} | closed {closed} | {hand.control_action}", hand.origin, 0.65, (20, 220, 120), 2)


def draw_hud(frame, fps, state, args, controller):
    width = frame.shape[1]
    cv2.rectangle(frame, (0, 0), (width, 178), (20, 20, 20), -1)
    text(frame, f"FPS {fps:.1f} | Q quit | R reset | S save", (16, 32), 0.72, thickness=2)
    text(frame, f"{args.draw_hand.upper()}: index finger is the brush pointer", (16, 64), 0.55, (220, 220, 220))
    text(frame, f"{args.control_hand.upper()}: thumb+index draw, +middle erase, +ring color, +pinky clear", (16, 92), 0.55, (220, 220, 220))
    mode = state.mode.upper()
    mode_color = state.color if mode == "DRAW" else (80, 80, 255) if mode == "ERASE" else (180, 180, 180)
    cv2.circle(frame, (42, 151), 14, mode_color, -1)
    text(frame, f"MODE: {mode}", (66, 146), 0.7, (255, 255, 255), 2)
    ctrl = controller.control_action.upper() if controller and controller.control_action != "none" else "NONE"
    text(frame, f"CTRL: {ctrl}", (66, 170), 0.52, (220, 220, 220))
    cv2.circle(frame, (width - 130, 92), state.brush, state.color, -1)
    text(frame, f"brush {state.brush}", (width - 100, 98), 0.55, (220, 220, 220))


def choose_roles(hands, args):
    drawer = max((hand for hand in hands if hand.label == args.draw_hand), key=lambda hand: hand.score, default=None)
    controller = max((hand for hand in hands if hand.label == args.control_hand), key=lambda hand: hand.score, default=None)
    return drawer, controller


def apply_draw(canvas, hand, state):
    if hand is None or not hand.pointer or state.mode == "ready":
        state.reset_line()
        return

    point = state.smooth(hand.index_tip)
    if state.mode == "draw":
        if state.last_draw:
            cv2.line(canvas, state.last_draw, point, state.color, state.brush, cv2.LINE_AA)
        state.last_draw, state.last_erase = point, None
    else:
        size = max(state.brush * 4, 28)
        if state.last_erase:
            cv2.line(canvas, state.last_erase, point, (0, 0, 0), size, cv2.LINE_AA)
        cv2.circle(canvas, point, size // 2, (0, 0, 0), -1)
        state.last_erase, state.last_draw = point, None


def apply_control(canvas, hand, state):
    if hand is None or hand.control_action == "none":
        state.mode = "ready"
        return

    now = time.time()
    action = hand.control_action
    if action in ("draw", "erase"):
        state.mode = action
    elif action == "clear" and now - state.last_clear_time > 1.2:
        state.mode = "ready"
        canvas.fill(0)
        state.reset_line()
        state.last_clear_time = now
    elif action != "clear" and now - state.last_tool_time > 0.55:
        state.mode = "ready"
        if action == "color":
            state.color_id = (state.color_id + 1) % len(COLORS)
        elif action == "brush+":
            state.brush = min(32, state.brush + 2)
        elif action == "brush-":
            state.brush = max(2, state.brush - 2)
        state.last_tool_time = now


def camera(args):
    cap = cv2.VideoCapture(args.camera)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, args.width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    if not cap.isOpened():
        raise RuntimeError("Could not open webcam. Try: python main.py --camera 1")
    return cap


def save(canvas):
    path = PROJECT_DIR / "hand_drawing.png"
    cv2.imwrite(str(path), canvas)
    print(f"Saved drawing: {path}")


def main():
    args = parse_args()
    mp_hands, mp_draw, mp_styles = mediapipe_solutions()
    cap = camera(args)
    state = State()
    canvas = None
    last_time = time.perf_counter()
    landmark_style = mp_styles.get_default_hand_landmarks_style()
    connection_style = mp_styles.get_default_hand_connections_style()

    with mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=args.max_hands,
        model_complexity=args.model_complexity,
        min_detection_confidence=args.min_detection_confidence,
        min_tracking_confidence=args.min_tracking_confidence,
    ) as tracker:
        while True:
            ok, frame = cap.read()
            if not ok:
                break

            frame = cv2.flip(frame, 1)
            height, width = frame.shape[:2]
            canvas = np.zeros_like(frame) if canvas is None or canvas.shape[:2] != (height, width) else canvas
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb.flags.writeable = False
            result = tracker.process(rgb)
            hands = []

            if result.multi_hand_landmarks and result.multi_handedness:
                for landmarks, handedness in zip(result.multi_hand_landmarks, result.multi_handedness):
                    hand = analyze(landmarks, handedness, width, height)
                    hands.append(hand)
                    if not args.hide_landmarks:
                        mp_draw.draw_landmarks(frame, landmarks, mp_hands.HAND_CONNECTIONS, landmark_style, connection_style)

            drawer, controller = choose_roles(hands, args)
            apply_control(canvas, controller, state)
            apply_draw(canvas, drawer, state)
            for hand in hands:
                draw_info(frame, hand, "DRAW" if hand is drawer else "CTRL")

            frame = cv2.addWeighted(frame, 1.0, canvas, 0.85, 0)
            now = time.perf_counter()
            draw_hud(frame, 1 / max(now - last_time, 0.0001), state, args, controller)
            last_time = now
            cv2.imshow("Hand Tracking", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            if key == ord("r"):
                canvas.fill(0)
                state.reset_line()
            if key == ord("s"):
                save(canvas)

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as error:
        print(f"Error: {error}")
        raise SystemExit(1) from error
