import cv2
from ai.detection.infer.detect import detect_plates
from ai.ocr.ocr import recognize_plate

def process_frame(frame):
    """
    输入：图像帧
    输出：车牌号列表
    """
    plates = detect_plates(frame)
    plate_numbers = []
    
    for plate in plates:
        x1, y1, x2, y2 = plate['bbox']
        plate_image = frame[y1:y2, x1:x2]
        plate_number = recognize_plate(plate_image)
        if plate_number:
            plate_numbers.append(plate_number)
    
    return plate_numbers