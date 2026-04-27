from PyQt5.QtWidgets import QFileDialog
from ui.main_window import MainWindow
from threads.video_thread import VideoThread
from threads.camera_thread import CameraThread

class MainController:
    def __init__(self):
        self.view = MainWindow()
        self.video_thread = None
        self.camera_thread = None

        # 按钮绑定
        self.view.btn_video.clicked.connect(self.open_video)
        self.view.btn_camera.clicked.connect(self.open_camera)
        self.view.btn_stop.clicked.connect(self.stop_all)
        self.view.btn_clear.clicked.connect(self.view.clear_table)

    def open_video(self):
        path, _ = QFileDialog.getOpenFileName()
        if not path: return
        self.stop_all()

        self.video_thread = VideoThread(path)
        self.video_thread.frame_signal.connect(self.view.update_frame)
        self.video_thread.result_signal.connect(self.view.update_result)
        self.video_thread.result_signal.connect(self.view.add_record)
        self.video_thread.fps_signal.connect(self.view.update_fps)
        self.video_thread.start()

        self.view.set_video_status("播放中")
        self.view.set_recognize_status("识别中")

    def open_camera(self):
        self.stop_all()
        self.camera_thread = CameraThread()
        self.camera_thread.frame_signal.connect(self.view.update_frame)
        self.camera_thread.result_signal.connect(self.view.update_result)
        self.camera_thread.result_signal.connect(self.view.add_record)
        self.camera_thread.fps_signal.connect(self.view.update_fps)
        self.camera_thread.start()

        self.view.set_video_status("摄像头已打开")
        self.view.set_recognize_status("识别中")

    def stop_all(self):
        if self.video_thread:
            self.video_thread.stop()
        if self.camera_thread:
            self.camera_thread.stop()
        self.view.set_video_status("已停止")
        self.view.set_recognize_status("已停止")

    def show(self):
        self.view.show()