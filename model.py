import unicodedata
from ultralytics import YOLO

class YOLOModel:
    # 학습되어있는 best.pt 불러와서 적용
    def __init__(self):
        self.model = YOLO("model/best.pt")
    
    # 이미지 경로를 입력받아 음식 클래스를 텍스트로 반환
    def img_2_txt(self, image_path: str):
        results = self.model(image_path)
        dict_class = results[0].names
        food_cls = []
        for result in results:
            food = set()
            for cls in result.boxes.cls:
                cls_index = int(cls)
                class_name = dict_class[cls_index]
                # 문자열을 NFC 형태로 정규화
                normalized_name = unicodedata.normalize('NFC', class_name)
                food.add(normalized_name)
            food_cls.append(list(food))
        return sum(food_cls, [])
