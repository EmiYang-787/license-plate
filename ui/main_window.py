from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QTableWidget, QTableWidgetItem,
    QHeaderView
)
from PyQt5.QtCore import Qt, QTimer, QDateTime
from PyQt5.QtGui import QImage, QPixmap, QColor, QBrush

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("车牌识别停车场管理系统")
        self.setFixedSize(1400, 900)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0F1A2B;
                color: #FFFFFF;
            }
            QFrame {
                background-color: #1A2B42;
                border-radius: 8px;
            }
            QLabel {
                color: #E0E6ED;
            }
            QPushButton {
                border: none;
                border-radius: 6px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
                color: white;
            }
            QPushButton#btn_open {
                background-color: #007AFF;
            }
            QPushButton#btn_camera {
                background-color: #34C759;
            }
            QPushButton#btn_stop {
                background-color: #FF9500;
            }
            QPushButton#btn_clear {
                background-color: #636E72;
            }
            QTableWidget {
                background-color: #1A2B42;
                color: #E0E6ED;
                border: none;
                gridline-color: #34495E;
            }
            QHeaderView::section {
                background-color: #2C3E50;
                color: #FFFFFF;
                border: none;
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # ========== 左侧：功能控制 + 状态 ==========
        left_layout = QVBoxLayout()
        control_frame = QFrame()
        control_layout = QVBoxLayout(control_frame)
        control_layout.setContentsMargins(15, 15, 15, 15)
        control_layout.setSpacing(12)

        control_title = QLabel("功能控制")
        control_title.setStyleSheet("color:#4ECDC4; font-size:16px; font-weight:bold;")
        self.btn_video = QPushButton("打开视频")
        self.btn_video.setObjectName("btn_open")
        self.btn_camera = QPushButton("打开摄像头")
        self.btn_camera.setObjectName("btn_camera")
        self.btn_stop = QPushButton("停止")
        self.btn_stop.setObjectName("btn_stop")
        self.btn_clear = QPushButton("清空记录")
        self.btn_clear.setObjectName("btn_clear")

        control_layout.addWidget(control_title)
        control_layout.addWidget(self.btn_video)
        control_layout.addWidget(self.btn_camera)
        control_layout.addWidget(self.btn_stop)
        control_layout.addWidget(self.btn_clear)

        # 状态区
        status_frame = QFrame()
        status_layout = QVBoxLayout(status_frame)
        status_layout.setContentsMargins(15, 15, 15, 15)
        status_title = QLabel("系统状态")
        status_title.setStyleSheet("color:#4ECDC4; font-size:16px; font-weight:bold;")
        self.status_video = QLabel("视频：未打开")
        self.status_recognize = QLabel("识别：未开始")
        self.status_time = QLabel("时间：--")

        status_layout.addWidget(status_title)
        status_layout.addWidget(self.status_video)
        status_layout.addWidget(self.status_recognize)
        status_layout.addWidget(self.status_time)

        left_layout.addWidget(control_frame)
        left_layout.addWidget(status_frame)
        main_layout.addLayout(left_layout, 1)

        # ========== 中间：视频 + 记录表格 ==========
        center_layout = QVBoxLayout()
        video_frame = QFrame()
        video_layout = QVBoxLayout(video_frame)
        video_layout.setContentsMargins(15, 15, 15, 15)
        video_title = QLabel("实时画面")
        video_title.setStyleSheet("color:#4ECDC4; font-size:16px; font-weight:bold;")
        self.video_label = QLabel()
        self.video_label.setStyleSheet("background-color:#000; border-radius:4px;")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setMinimumSize(800, 500)
        self.fps_label = QLabel("FPS: 0.0")
        self.fps_label.setStyleSheet("color:#34C759;")

        video_layout.addWidget(video_title)
        video_layout.addWidget(self.video_label)
        video_layout.addWidget(self.fps_label)

        # 记录表
        record_frame = QFrame()
        record_layout = QVBoxLayout(record_frame)
        record_layout.setContentsMargins(15, 15, 15, 15)
        record_title = QLabel("识别记录")
        record_title.setStyleSheet("color:#4ECDC4; font-size:16px; font-weight:bold;")
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "车牌号", "状态", "入场时间", "出场时间", "时长", "状态"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        record_layout.addWidget(record_title)
        record_layout.addWidget(self.table)

        center_layout.addWidget(video_frame)
        center_layout.addWidget(record_frame)
        main_layout.addLayout(center_layout, 3)

        # ========== 右侧：识别结果 ==========
        right_layout = QVBoxLayout()
        result_frame = QFrame()
        result_layout = QVBoxLayout(result_frame)
        result_layout.setContentsMargins(15, 15, 15, 15)
        result_title = QLabel("识别结果")
        result_title.setStyleSheet("color:#4ECDC4; font-size:16px; font-weight:bold;")
        self.plate_label = QLabel("--")
        self.plate_label.setStyleSheet("font-size:36px; font-weight:bold; color:#fff;")
        self.plate_label.setAlignment(Qt.AlignCenter)
        self.info1 = QLabel("状态：--")
        self.info2 = QLabel("入场时间：--")
        self.info3 = QLabel("停车时长：--")

        result_layout.addWidget(result_title)
        result_layout.addWidget(self.plate_label)
        result_layout.addWidget(self.info1)
        result_layout.addWidget(self.info2)
        result_layout.addWidget(self.info3)

        right_layout.addWidget(result_frame)
        main_layout.addLayout(right_layout, 1)

        # 定时器刷新时间
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000)

    def update_clock(self):
        now = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
        self.status_time.setText(f"时间：{now}")

    def update_frame(self, q_img):
        self.video_label.setPixmap(
            QPixmap.fromImage(q_img).scaled(self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )

    def update_result(self, info: dict):
        self.plate_label.setText(info.get("plate", "--"))
        self.info1.setText(f"状态：{info.get('msg', '--')}")
        self.info2.setText(f"入场时间：{info.get('time', '--')}")
        self.info3.setText(f"停车时长：{info.get('duration', '--')}")

    def add_record(self, info: dict):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(info.get("plate", "")))
        self.table.setItem(row, 1, QTableWidgetItem(info.get("msg", "")))
        self.table.setItem(row, 2, QTableWidgetItem(info.get("entry_time", "")))
        self.table.setItem(row, 3, QTableWidgetItem(info.get("exit_time", "--")))
        self.table.setItem(row, 4, QTableWidgetItem(info.get("duration", "--")))

        item = QTableWidgetItem(info.get("status_text", ""))
        if info.get("status") == 0:
            item.setForeground(QBrush(QColor("#34C759")))
        else:
            item.setForeground(QBrush(QColor("#FF3B30")))
        self.table.setItem(row, 5, item)

    def clear_table(self):
        self.table.setRowCount(0)

    def set_video_status(self, text):
        self.status_video.setText(f"视频：{text}")

    def set_recognize_status(self, text):
        self.status_recognize.setText(f"识别：{text}")

    def update_fps(self, fps):
        self.fps_label.setText(f"FPS: {fps:.1f}")