"""
系统入口文件
职责：组装各模块，注入AI接口与业务接口，启动应用
"""
import sys
from PyQt5.QtWidgets import QApplication

from controller.main_controller import MainController

# ==========================================
# TODO: 由成员A、B提供真实实现后，取消下面注释
# ==========================================
# from ai.pipeline.pipeline import process_frame
# from service.parking_service import handle_plate


# ========== Mock 接口（开发联调阶段使用）==========
def mock_process_frame(frame):
    """
    Mock AI接口：process_frame(frame) → List[str]
    实际由成员A替换为真实实现
    """
    # 开发阶段返回空列表，避免报错
    return []


def mock_handle_plate(plate):
    """
    Mock 业务接口：handle_plate(plate) → dict
    实际由成员B替换为真实实现
    """
    from datetime import datetime
    return {
        "plate": plate,
        "status": "entry",
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "duration": None
    }


# ==========================================


def main():
    app = QApplication(sys.argv)

    # 注入接口：联调时替换为真实接口
    controller = MainController(
        process_frame_func=mock_process_frame,   # ← 替换为 process_frame
        handle_plate_func=mock_handle_plate      # ← 替换为 handle_plate
    )

    controller.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()