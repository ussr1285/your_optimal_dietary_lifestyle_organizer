import pandas as pd
import numpy as np

selected_cols = ['식품명', '에너지(㎉)', '단백질(g)', '지방(g)', '탄수화물(g)', '총당류(g)', '나트륨(㎎)']
food_df = pd.read_excel('통합 식품영양성분DB.xlsx', skiprows=3, usecols=selected_cols)
food_df.set_index('식품명', inplace=True)
food_df = food_df.apply(pd.to_numeric, errors='coerce')

man_df = pd.read_excel('영양소별 평균 섭취량(남자).xls')
woman_df = pd.read_excel('영양소별 평균 섭취량(여자).xls')

woman_df.set_index('영양소＼연령(세)', inplace=True)
man_df.set_index('영양소＼연령(세)', inplace=True)
woman_df.drop(columns=['전체 평균'], inplace=True)
man_df.drop(columns=['전체 평균'], inplace=True)

woman_df = woman_df.loc[:, ~woman_df.columns.str.contains('표준오차')]
woman_df.columns = [col[:-2] for col in woman_df.columns]

man_df = man_df.loc[:, ~man_df.columns.str.contains('표준오차')]
man_df.columns = [col[:-2] for col in man_df.columns]

index_mapping = {
    '에너지 섭취량(kcal)': '에너지(㎉)',
    '단백질 섭취량(g)': '단백질(g)',
    '지방 섭취량(g)': '지방(g)',
    '탄수화물 섭취량(g)': '탄수화물(g)',
    '당 섭취량(g)': '총당류(g)',
    '나트륨 섭취량(mg)': '나트륨(㎎)'
}

woman_df = woman_df.reset_index()
woman_df = woman_df[woman_df['영양소＼연령(세)'].isin(index_mapping.keys())]
woman_df.set_index('영양소＼연령(세)', inplace=True)
woman_df.rename(index=index_mapping, inplace=True)

man_df = man_df.reset_index()
man_df = man_df[man_df['영양소＼연령(세)'].isin(index_mapping.keys())]
man_df.set_index('영양소＼연령(세)', inplace=True)
man_df.rename(index=index_mapping, inplace=True)

man_df.to_excel('영양소별 평균 섭취량(남자).xlsx')
woman_df.to_excel('영양소별 평균 섭취량(여자).xlsx')
