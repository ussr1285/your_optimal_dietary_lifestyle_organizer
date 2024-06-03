import pandas as pd
import numpy as np
from utils import get_age_range, normalize

# 각 데이터 프레임 불러오기 (영양성분 DB, 남자 권장 섭취량, 여자 권장 섭취량)
food_df = pd.read_excel('data/통합 식품영양성분DB.xlsx', index_col='식품명')
man_df = pd.read_excel('data/영양소별 평균 섭취량(남자).xlsx', index_col='영양소＼연령(세)')
woman_df = pd.read_excel('data/영양소별 평균 섭취량(여자).xlsx', index_col='영양소＼연령(세)')

class Nutrient:
    def __init__(self, food_list: list, gender: str, age: int):
        # 사용자가 먹은 음식 리스트와 성별 나이를 저장.
        self.age = get_age_range(age)
        self.gender = gender
        self.food_list = food_list
        self.nutrient_columns = ['에너지(㎉)', '단백질(g)', '지방(g)', '탄수화물(g)', '총당류(g)', '나트륨(㎎)']
    
    def get_nutrient_ingestion(self):
        meal_nutrient = []
        for a_meal in self.food_list:
            meal_totals = {nutrient: 0 for nutrient in self.nutrient_columns}
            for food in a_meal:
                if food in food_df.index:  # food_df에 있는지 확인
                    food_nutrients = food_df.loc[food, self.nutrient_columns]
                    food_nutrients = food_nutrients.apply(pd.to_numeric, errors='coerce') # 숫자가 아닌 것들이 존재 -> 숫자로 변환

                    if isinstance(food_nutrients, pd.Series):
                        for nutrient in self.nutrient_columns:
                            meal_totals[nutrient] += food_nutrients[nutrient]
                    else: # 같은 이름의 제품이 제조사가 다른 경우로 여러 개 존재할 수 있음
                        # 이 경우에 각 제품들의 평균 값으로 계산
                        for nutrient in self.nutrient_columns:
                            meal_totals[nutrient] += food_nutrients[nutrient].mean()

            meal_nutrient.append([meal_totals[nutrient] for nutrient in self.nutrient_columns])
        return meal_nutrient # 사용자가 먹은 음식의 영양소 총합 반환
    
    def get_need_nutrition(self):
        data = pd.DataFrame(self.get_nutrient_ingestion(), columns=self.nutrient_columns).T # 섭취한 영양소 총합을 데이터 프레임으로 변환
        if self.gender=='남': #남성일 경우와 여성일 경우 데이터 프레임이 다름. 구분 필요
            need_nutrition = man_df.loc[:, self.age] - data.sum(axis=1) # 권장 섭취량 데이터 프레임에서 섭취 영양소 정보를 빼주는 작업
        else:
            need_nutrition = woman_df.loc[:, self.age] - data.sum(axis=1) # 여성 기준 필요 영양소 계산
        return need_nutrition # 각 영양소의 차이만큼 반환
    
    def get_recommend_food(self):
        # 필요 영양소와 정규화된 음식 데이터프레임 얻기
        normalized_food_df, need_nutrition = normalize(food_df, self.get_need_nutrition())
        # 필요 영양소와 음식 데이터 간의 거리 계산
        distances = ((normalized_food_df - need_nutrition) ** 2).sum(axis=1).sort_values()

        first_nearest_index = distances.idxmin() # 가장 가까운 음식
        selected_indices = [first_nearest_index]

        remaining_distances = distances.drop(first_nearest_index) # 첫 번째 선택된 음식 제외한 거리 데이터
         # 두 번째 가장 가까운 음식
         # 하지만 이때, 첫 번째로 추천한 음식과 같은 계열의 음식을 경우 제외 (이전 추천 음식과 겹치는 문자열이 들어갈 경우 제외)
        second_nearest_index = remaining_distances[~remaining_distances.index.str.contains(first_nearest_index)].idxmin()
        selected_indices.append(second_nearest_index)

        remaining_distances = remaining_distances.drop(second_nearest_index)
        # 세 번째로 가까운 음식. 마찬가지로 앞서 추천한 음식 제외
        third_nearest_index = remaining_distances[~remaining_distances.index.str.contains('|'.join(selected_indices))].idxmin()
        selected_indices.append(third_nearest_index)
        return selected_indices # 3개의 추천 음식 반환

# 사용 방법

# 객체 생성 (생성자 매개변수: 먹은 음식(2차원 리스트), 성별, 나이)
# user = Nutrient([['바나나'], ['라면', '배추김치'], ['돈까스', '우동']], gender='남', age=24)

# 추천 음식 반환 코드 (반환 형태: 1차원 리스트)
# print(user.get_recommend_food())

# 섭취한 영양소 반환 코드 (반환 형태: 2차원 리스트)
# print(user.get_nutrient_ingestion())

# 필요한 영양소 반환 코드 (반환 형태: Series)
# print(user.get_need_nutrition())
