from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage
import cv2
import time

# 兼容队友接口
try:
    from ai.pipeline.pipeline import process_frame
    from service.parking_service import handle_plate
except:
    def process_frame(frame):
        return []
    def handle_plate(p):
        return {
            "plate": p,
            "msg": "测试识别",
            "time": "2025-01-01 00:00:00",
            "entry_time": "2025-01-01 00:00:00",
            "exit_time": "--",
            "duration": "--",
            "status": 0,
            "status_text": "在场"
        }

class VideoThread(QThread):
    frame_signal = pyqtSignal(QImage)
    result_signal = pyqtSignal(dict)
    fps_signal = pyqtSignal(float)

    def __init__(self, path):
        super().__init__()
        self.path = path
        self.running = True

    def run(self):
        cap = cv2.VideoCapture(self.path)
        last_time = time.time()

        while self.running:
            ret, frame = cap.read()
            if not ret:
                break

            # 计算FPS
            now = time.time()
            fps = 1 / (now - last_time) if (now - last_time) > 0 else 0
            last_time = now
            self.fps_signal.emit(fps)

            # 车牌识别流程
            plates = process_frame(frame)
            for plate in plates:
                info = handle_plate(plate)
                self.result_signal.emit(info)

            # 画面转换
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            q_img = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
            self.frame_signal.emit(q_img)
            time.sleep(0.03)

        cap.release()

    def stop(self):
        self.running = False
        self.wait()