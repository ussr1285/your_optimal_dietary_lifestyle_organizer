import Food_recommend as fr


## 사용 방법

# 객체 생성 (생성자 매개변수: 먹은 음식(2차원 리스트), 성별, 나이)
user = fr.Nutrient([['바나나'], ['라면', '배추김치'], ['돈까스', '우동']], gender='남', age=24)

# 추천 음식 반환 코드 (반환 형테: 1차원 리스트)
print(user.get_recommend_food())

# 섭취한 영양소 반환 코드 (반환 형테: 2차원 리스트)
print(user.get_nutrient_ingestion())

# 필요한 영양소 반환 코드 (반환 형테: Series)
print(user.get_need_nutrition())