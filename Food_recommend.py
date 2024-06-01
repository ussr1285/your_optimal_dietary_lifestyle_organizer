import pandas as pd
import numpy as np
from utils import get_age_range, normalize

food_df = pd.read_excel('통합 식품영양성분DB.xlsx', index_col='식품명')
man_df = pd.read_excel('영양소별 평균 섭취량(남자).xlsx', index_col='영양소＼연령(세)')
woman_df = pd.read_excel('영양소별 평균 섭취량(여자).xlsx', index_col='영양소＼연령(세)')

class Nutrient:
    def __init__(self, food_list: list, gender: str, age: int):
        self.age = get_age_range(age)
        self.gender = gender
        self.food_list = food_list
        self.nutrient_columns = ['에너지(㎉)', '단백질(g)', '지방(g)', '탄수화물(g)', '총당류(g)', '나트륨(㎎)']
    
    def get_nutrient_ingestion(self):
        meal_nutrient = []
        # print("@@@@@@@@@@@@@@@@@@@@@@@@@")
        # print(food_df.index[0])
        # for food in self.food_list:
        #     for chara in food:
        #         print(chara)
        for a_meal in self.food_list:
            meal_totals = {nutrient: 0 for nutrient in self.nutrient_columns}
            for food in a_meal:
                # print("@@@@@@@@@@@@@@@@@@@@@@@@@")
                # print("food : {0} == {1}".format(food, 1 if food in food_df.index else 0))
                # print(food)
                # print(food in food_df.index)
                if food in food_df.index:  # food_df에 있는지 확인
                    food_nutrients = food_df.loc[food, self.nutrient_columns]
                    food_nutrients = food_nutrients.apply(pd.to_numeric, errors='coerce')

                    if isinstance(food_nutrients, pd.Series):
                        for nutrient in self.nutrient_columns:
                            meal_totals[nutrient] += food_nutrients[nutrient]
                    else:
                        for nutrient in self.nutrient_columns:
                            meal_totals[nutrient] += food_nutrients[nutrient].mean()

            meal_nutrient.append([meal_totals[nutrient] for nutrient in self.nutrient_columns])
        return meal_nutrient
    
    def get_need_nutrition(self):
        data = pd.DataFrame(self.get_nutrient_ingestion(), columns=self.nutrient_columns).T
        if self.gender=='남':
            need_nutrition = man_df.loc[:, self.age] - data.sum(axis=1)
        else:
            need_nutrition = woman_df.loc[:, self.age] - data.T.sum(axis=1)
        return need_nutrition
    
    def get_recommend_food(self):
        normalized_food_df, need_nutrition = normalize(food_df, self.get_need_nutrition())
        distances = ((normalized_food_df - need_nutrition) ** 2).sum(axis=1)

        first_nearest_index = distances.idxmin()
        selected_indices = [first_nearest_index]

        remaining_distances = distances.drop(first_nearest_index)
        second_nearest_index = remaining_distances[~remaining_distances.index.str.contains(first_nearest_index)].idxmin()
        selected_indices.append(second_nearest_index)

        remaining_distances = remaining_distances.drop(second_nearest_index)
        third_nearest_index = remaining_distances[~remaining_distances.index.str.contains('|'.join(selected_indices))].idxmin()
        selected_indices.append(third_nearest_index)
        
        return selected_indices

# ## 사용 방법

# # 객체 생성 (생성자 매개변수: 먹은 음식(2차원 리스트), 성별, 나이)
# user = Nutrient([['바나나'], ['라면', '배추김치'], ['돈까스', '우동']], gender='남', age=24)

# # 추천 음식 반환 코드 (반환 형태: 1차원 리스트)
# print(user.get_recommend_food())

# # 섭취한 영양소 반환 코드 (반환 형태: 2차원 리스트)
# print(user.get_nutrient_ingestion())

# # 필요한 영양소 반환 코드 (반환 형태: Series)
# print(user.get_need_nutrition())
