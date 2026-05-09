"""
主控制器模块
职责：连接UI与线程、调度AI接口与业务接口、管理系统生命周期
数据流：frame → process_frame → handle_plate → UI显示
"""
from PyQt5.QtCore import QObject, pyqtSlot

from ui.main_window import MainWindow
from threads.video_thread import VideoThread
from threads.camera_thread import CameraThread


class MainController(QObject):
    """
    控制器严格遵循接口规范：
      - AI接口: process_frame(frame) → List[str]     （成员A实现）
      - 业务接口: handle_plate(plate) → dict          （成员B实现）
    """

    def __init__(self, process_frame_func, handle_plate_func):
        """
        :param process_frame_func: 成员A提供的AI识别接口
        :param handle_plate_func: 成员B提供的业务处理接口
        """
        super().__init__()
        self.process_frame = process_frame_func
        self.handle_plate = handle_plate_func

        self.window = MainWindow()
        self.video_thread = None
        self.camera_thread = None

        self._connect_ui_signals()

    def _connect_ui_signals(self):
        """连接UI按钮事件"""
        self.window.btn_start_video.clicked.connect(self.on_start_video)
        self.window.btn_open_camera.clicked.connect(self.on_open_camera)
        self.window.btn_stop.clicked.connect(self.on_stop)

    def show(self):
        self.window.show()

    # ========== 按钮响应 ==========

    @pyqtSlot()
    def on_start_video(self):
        """开始播放视频文件"""
        video_path = self.window.get_video_path()
        if not video_path:
            return

        self._stop_all_threads()

        self.window.update_status("正在播放视频...")
        self.window.btn_start_video.setEnabled(False)
        self.window.btn_open_camera.setEnabled(False)
        self.window.btn_stop.setEnabled(True)

        # 创建视频线程，注入AI与业务接口
        self.video_thread = VideoThread(
            video_path=video_path,
            process_frame_func=self.process_frame,
            handle_plate_func=self.handle_plate
        )

        # 信号连接：帧 → UI显示 | 结果 → UI展示 | 停止 → 状态重置
        self.video_thread.frame_signal.connect(self.window.update_frame)
        self.video_thread.result_signal.connect(self.window.update_results)
        self.video_thread.stopped_signal.connect(self._on_thread_stopped)

        self.video_thread.start()

    @pyqtSlot()
    def on_open_camera(self):
        """打开摄像头"""
        self._stop_all_threads()

        self.window.update_status("摄像头实时识别中...")
        self.window.btn_start_video.setEnabled(False)
        self.window.btn_open_camera.setEnabled(False)
        self.window.btn_stop.setEnabled(True)

        self.camera_thread = CameraThread(
            process_frame_func=self.process_frame,
            handle_plate_func=self.handle_plate,
            camera_id=0
        )

        self.camera_thread.frame_signal.connect(self.window.update_frame)
        self.camera_thread.result_signal.connect(self.window.update_results)
        self.camera_thread.stopped_signal.connect(self._on_thread_stopped)

        self.camera_thread.start()

    @pyqtSlot()
    def on_stop(self):
        """停止当前所有任务"""
        self._stop_all_threads()
        self.window.update_status("已停止")
        self.window.reset_ui_state()

    # ========== 线程管理 ==========

    def _stop_all_threads(self):
        """安全停止所有运行中的线程"""
        if self.video_thread and self.video_thread.isRunning():
            self.video_thread.frame_signal.disconnect(self.window.update_frame)
            self.video_thread.result_signal.disconnect(self.window.update_results)
            self.video_thread.stop()
            self.video_thread = None

        if self.camera_thread and self.camera_thread.isRunning():
            self.camera_thread.frame_signal.disconnect(self.window.update_frame)
            self.camera_thread.result_signal.disconnect(self.window.update_results)
            self.camera_thread.stop()
            self.camera_thread = None

    @pyqtSlot()
    def _on_thread_stopped(self):
        """线程自然结束回调（如视频播放完毕）"""
        self.window.reset_ui_state()
        self.window.update_status("播放结束")