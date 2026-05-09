"""
主界面模块
职责：布局管理、视频渲染、结果展示、按钮交互
"""
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit, QFileDialog, QMessageBox,
    QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
import cv2


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("车牌识别停车场管理系统")
        self.setMinimumSize(1200, 750)
        self._setup_ui()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        # ========== 主布局 ==========
        main_layout = QHBoxLayout(central)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # ========== 左侧：视频显示区 ==========
        left_layout = QVBoxLayout()

        # 视频画面
        self.video_label = QLabel("等待视频源...")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setStyleSheet("""
            QLabel {
                background-color: #1e1e1e;
                color: #ffffff;
                font-size: 18px;
                border: 2px solid #444;
                border-radius: 6px;
            }
        """)
        left_layout.addWidget(self.video_label)

        # 控制按钮区
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        self.btn_start_video = QPushButton("📁 开始视频")
        self.btn_open_camera = QPushButton("📷 打开摄像头")
        self.btn_stop = QPushButton("⏹ 停止")
        self.btn_stop.setEnabled(False)

        # 按钮样式
        btn_style = """
            QPushButton {
                font-size: 14px;
                padding: 10px 20px;
                border-radius: 5px;
                background-color: #2d8cf0;
                color: white;
                border: none;
            }
            QPushButton:hover { background-color: #1a7de0; }
            QPushButton:disabled { background-color: #999; }
            QPushButton#stop { background-color: #ed4014; }
            QPushButton#stop:hover { background-color: #d9360e; }
        """
        self.btn_start_video.setStyleSheet(btn_style)
        self.btn_open_camera.setStyleSheet(btn_style)
        self.btn_stop.setStyleSheet(btn_style.replace("QPushButton {", "QPushButton { background-color: #ed4014;"))
        self.btn_stop.setObjectName("stop")

        btn_layout.addWidget(self.btn_start_video)
        btn_layout.addWidget(self.btn_open_camera)
        btn_layout.addWidget(self.btn_stop)
        btn_layout.addStretch()

        left_layout.addLayout(btn_layout)
        main_layout.addLayout(left_layout, stretch=3)

        # ========== 右侧：结果展示区 ==========
        right_layout = QVBoxLayout()

        # 实时识别日志
        log_group = QGroupBox("📝 实时识别记录")
        log_layout = QVBoxLayout(log_group)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setStyleSheet("""
            QTextEdit {
                font-size: 13px;
                font-family: "Microsoft YaHei", "SimHei", sans-serif;
                background-color: #f8f9fa;
                border: 1px solid #d9d9d9;
                border-radius: 4px;
                padding: 8px;
                line-height: 1.6;
            }
        """)
        log_layout.addWidget(self.result_text)
        right_layout.addWidget(log_group, stretch=1)

        # 在场车辆表格
        table_group = QGroupBox("🚗 当前在场车辆")
        table_layout = QVBoxLayout(table_group)

        self.table_active = QTableWidget()
        self.table_active.setColumnCount(3)
        self.table_active.setHorizontalHeaderLabels(["车牌号", "入场时间", "状态"])
        self.table_active.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_active.setStyleSheet("""
            QTableWidget {
                font-size: 13px;
                border: 1px solid #d9d9d9;
                border-radius: 4px;
            }
            QHeaderView::section {
                background-color: #fafafa;
                padding: 6px;
                border: 1px solid #d9d9d9;
                font-weight: bold;
            }
        """)
        table_layout.addWidget(self.table_active)
        right_layout.addWidget(table_group, stretch=1)

        # 状态栏
        self.status_label = QLabel("就绪 | 等待操作...")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 12px;
                padding: 6px;
                background-color: #f0f0f0;
                border-radius: 4px;
            }
        """)
        right_layout.addWidget(self.status_label)

        main_layout.addLayout(right_layout, stretch=2)

    # ========== 公共接口（供Controller调用） ==========

    @pyqtSlot(object)
    def update_frame(self, frame):
        """将OpenCV帧渲染到QLabel"""
        if frame is None:
            return

        # BGR → RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w

        qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)

        # 等比例缩放适应显示区域
        scaled = pixmap.scaled(
            self.video_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.video_label.setPixmap(scaled)

    @pyqtSlot(list)
    def update_results(self, results):
        """
        批量更新识别结果
        :param results: List[dict]  handle_plate返回的结果列表
        """
        for data in results:
            self._append_single_result(data)

    def _append_single_result(self, data: dict):
        """单条结果格式化显示"""
        plate = data.get("plate", "未知")
        status = data.get("status", "")
        time_str = data.get("time", "")
        duration = data.get("duration")

        if status == "entry":
            msg = f"[{time_str}] 🚗 <b>车辆入场</b> | 车牌: <span style='color:#2d8cf0;'>{plate}</span>"
            self._add_active_vehicle(plate, time_str)
        elif status == "exit":
            if duration is not None:
                msg = (f"[{time_str}] 🚙 <b>车辆出场</b> | 车牌: <span style='color:#19be6b;'>{plate}</span> "
                       f"| 停车时长: <b>{duration:.2f}</b> 小时")
            else:
                msg = f"[{time_str}] 🚙 <b>车辆出场</b> | 车牌: {plate}"
            self._remove_active_vehicle(plate)
        else:
            msg = f"[{time_str}] ⚠ 未知状态 | 车牌: {plate}"

        self.result_text.append(msg)

    def _add_active_vehicle(self, plate: str, entry_time: str):
        """添加到在场车辆表"""
        row = self.table_active.rowCount()
        self.table_active.insertRow(row)
        self.table_active.setItem(row, 0, QTableWidgetItem(plate))
        self.table_active.setItem(row, 1, QTableWidgetItem(entry_time))
        status_item = QTableWidgetItem("在场")
        status_item.setForeground(Qt.red)
        self.table_active.setItem(row, 2, status_item)

    def _remove_active_vehicle(self, plate: str):
        """从在场车辆表移除"""
        for row in range(self.table_active.rowCount()):
            item = self.table_active.item(row, 0)
            if item and item.text() == plate:
                self.table_active.removeRow(row)
                break

    @pyqtSlot(str)
    def update_status(self, text: str):
        self.status_label.setText(text)

    def get_video_path(self) -> str:
        """弹出视频选择对话框"""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "选择视频文件",
            "",
            "视频文件 (*.mp4 *.avi *.mkv *.mov);;所有文件 (*)"
        )
        return path

    def reset_ui_state(self):
        """重置按钮状态"""
        self.btn_start_video.setEnabled(True)
        self.btn_open_camera.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.video_label.setText("等待视频源...")
        self.video_label.setPixmap(QPixmap())  # 清空画面

    def show_error(self, title: str, message: str):
        QMessageBox.critical(self, title, message)