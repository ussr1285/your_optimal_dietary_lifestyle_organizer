# DataFrame 정규화
def normalize(df, need):
    result = df.copy()
    for feature_name in df.columns:
        max_value = df[feature_name].max()
        min_value = df[feature_name].min()
        result[feature_name] = (df[feature_name] - min_value) / (max_value - min_value)
        need[feature_name] = (need[feature_name] - min_value) / (max_value - min_value)
    return result, need

# numeric age를 categorical하게 변환
def get_age_range(age):
    if 1 <= age <= 2:
        return '1-2 '
    elif 3 <= age <= 5:
        return '3-5 '
    elif 6 <= age <= 11:
        return '6-11 '
    elif 12 <= age <= 18:
        return '12-18 '
    elif 19 <= age <= 29:
        return '19-29 '
    elif 30 <= age <= 49:
        return '30-49 '
    elif 50 <= age <= 64:
        return '50-64 '
    elif age >= 65:
        return '≥ 65 '
    else:
        return 'Invalid age'