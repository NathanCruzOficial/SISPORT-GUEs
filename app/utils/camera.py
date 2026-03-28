import cv2
import threading
import numpy as np


class Camera:
    def __init__(self, index=0):
        self.index = index
        self.cap = None
        self.frame = None
        self.running = False
        self.lock = threading.Lock()

    def start(self):
        self.cap = cv2.VideoCapture(self.index, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            print("❌ Não foi possível abrir a câmera!")
            return

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        self.running = True
        threading.Thread(target=self._read_frames, daemon=True).start()

    def _read_frames(self):
        while self.running and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                with self.lock:
                    self.frame = frame

    def get_frame(self):
        with self.lock:
            if self.frame is None:
                placeholder = np.zeros((480, 640, 3), dtype=np.uint8)
                ret, buffer = cv2.imencode('.jpg', placeholder)
                return buffer.tobytes() if ret else None

            ret, buffer = cv2.imencode('.jpg', self.frame)
            return buffer.tobytes() if ret else None

    def stop(self):
        self.running = False
        if self.cap:
            self.cap.release()


camera = Camera(index=0)
