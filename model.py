from ultralytics import YOLO
from Food_recommend import Nutrient

class YOLOModel:
    def __init__(self):
        self.model = YOLO("model/best.pt")

    def img_2_txt(self, image_path: str):
        results = self.model(image_path)

        dict_class = results[0].names
        food_cls = []
        for result in results:
            food = set()
            for cls in result.boxes.cls:
                cls_index = int(cls)
                class_name = dict_class[cls_index]  # 클래스 인덱스에 해당하는 클래스 이름을 얻음
                food.add(class_name)  # 클래스 이름 출력
            food_cls.append(list(food))
        
        return sum(food_cls, [])

# # 테스트 코드
# if __name__ == "__main__":
#     yolo_model = YOLOModel()
#     image_path = 'uploads/A220132XX_33201.jpg'  # 테스트 이미지 경로
#     food_cls = yolo_model.img_2_txt(image_path)
#     print(food_cls)

# # 이미지 경로와 저장 경로 설정
# image_path = 'uploads/A220132XX_33201.jpg' # 이미지 경로 
# # save_dir = 'save/' # 저장할 경로 

# # 결과 저장
# results = model(image_path)
# # results.save(save_dir)

# # 음식 목록 추출
# dict_class = results[0].names
# food_cls = []
# for result in results:
#     food = set()
#     for cls in result.boxes.cls:
#         cls_index = int(cls)
#         class_name = dict_class[cls_index]  # 클래스 인덱스에 해당하는 클래스 이름을 얻음
#         food.add(class_name)  # 클래스 이름 출력
#     food_cls.append(list(food))

# print(food_cls)

# # 성별, 나이 입력
# gender = '남'
# age = 25

# ## 사용 방법

# # 객체 생성 (생성자 매개변수: 먹은 음식(2차원 리스트), 성별, 나이)
# user = Nutrient(food_cls, gender='남', age=24)

# # 추천 음식 반환 코드 (반환 형테: 1차원 리스트)
# user.get_recommend_food()

# # 섭취한 영양소 반환 코드 (반환 형테: 2차원 리스트)
# user.get_nutrient_ingestion()

# # 필요한 영양소 반환 코드 (반환 형테: Series)
# user.get_need_nutrition()
    