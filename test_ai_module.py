import cv2
from ai.pipeline.pipeline import process_frame

def test_ai_module():
    # 加载测试图像
    test_image = cv2.imread('test111.txt')
    if test_image is None:
        print("无法加载测试图像，使用默认测试")
        # 创建一个简单的测试图像
        test_image = cv2.imread('https://img.freepik.com/free-photo/close-up-car-license-plate_23-2149034620.jpg')
    
    # 测试process_frame函数
    print("测试AI识别模块...")
    plate_numbers = process_frame(test_image)
    print(f"识别到的车牌号: {plate_numbers}")
    print("测试完成！")

if __name__ == "__main__":
    test_ai_module()