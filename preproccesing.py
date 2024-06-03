import pandas as pd
import numpy as np
import yaml
import os
import json
import glob

def DataFrame_Preproccessing():
    # 필요한 영양소 col만 불러오기
    selected_cols = ['식품명', '에너지(㎉)', '단백질(g)', '지방(g)', '탄수화물(g)', '총당류(g)', '나트륨(㎎)']
    food_df = pd.read_excel('data/통합 식품영양성분DB.xlsx', skiprows=3, usecols=selected_cols)
    # 음식 종류는 인덱스로 구분
    food_df.set_index('식품명', inplace=True)
    food_df = food_df.apply(pd.to_numeric, errors='coerce')

    man_df = pd.read_excel('data/영양소별 평균 섭취량(남자).xls')
    woman_df = pd.read_excel('data/영양소별 평균 섭취량(여자).xls')

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
    # 남성 여성 권장 섭취량 데이터 프레임도 원하는 col만 남겨두고 삭제
    woman_df = woman_df.reset_index()
    woman_df = woman_df[woman_df['영양소＼연령(세)'].isin(index_mapping.keys())]
    woman_df.set_index('영양소＼연령(세)', inplace=True)
    woman_df.rename(index=index_mapping, inplace=True)

    man_df = man_df.reset_index()
    man_df = man_df[man_df['영양소＼연령(세)'].isin(index_mapping.keys())]
    man_df.set_index('영양소＼연령(세)', inplace=True)
    man_df.rename(index=index_mapping, inplace=True)

    man_df.to_excel('data/영양소별 평균 섭취량(남자).xlsx')
    woman_df.to_excel('data/영양소별 평균 섭취량(여자).xlsx')
    food_df.to_excel('data/통합 식품영양성분DB.xlsx')
    # 최종 데이터 프레임 저장.

new_img_base_directory = 'data/images/train/'
if os.path.exists(new_img_base_directory):
    # 총 음식 클래스의 종류들을 리스트로 반환
    folders_list = os.listdir(new_img_base_directory)
     
def Fix_Yaml():
    yaml_file_path = 'data.yaml'

    with open(yaml_file_path, 'r', encoding='utf-8') as file:
        yaml_content = yaml.safe_load(file)

    # yaml file dataset 경로 수정 및 Custom data로 맞춤
    yaml_content['names'] = folders_list
    yaml_content['val'] = 'data/images/valid/'
    yaml_content['train'] = 'data/images/train/'
    yaml_content['test'] = 'data/images/test/'
    yaml_content['nc'] = len(folders_list)

    with open(yaml_file_path, 'w', encoding='utf-8') as file:
        yaml.dump(yaml_content, file, allow_unicode=True, sort_keys=False)
        

def Json_to_txt():
    label_dir = 'data/labels/test/'
    image_dir = 'data/images/test/'

    # Function to convert JSON to YOLO format
    def convert_json_to_yolo(json_file_path, output_dir):
        with open(json_file_path, 'r', encoding='utf-8') as f:
            # json 파일 load
            data = json.load(f)
        
        # 같은 파일 이름으로 txt 파일 open
        file_name = os.path.basename(json_file_path).replace('.json', '.txt')
        output_file_path = os.path.join(output_dir, file_name)

        with open(output_file_path, 'w', encoding='utf-8') as file:
            # label x y w h 정보 추출
            for item in data:
                label = item["Label"]
                # 안 적혀있는 파일도 있기 때문에 예외처리로 일괄적으로 처리하는데 문제 없게끔 설정
                try:
                    x_center, y_center = map(float, item["Point(x,y)"].split(','))
                    width = float(item["W"])
                    height = float(item["H"])
                except ValueError as e:
                    print(f"Error processing item in {json_file_path}: {item}")
                    print(f"ValueError: {e}")
                    return False  # Indicate failure to process this file

                yolo_line = f"{label} {x_center} {y_center} {width} {height}\n"
                file.write(yolo_line)
                # txt 파일애 작성

        return True  # Indicate successful processing

    # 각 디렉토리르 추적하며 JSON 파일을 처리
    for class_folder in os.listdir(label_dir):
        class_folder_path = os.path.join(label_dir, class_folder)

        if os.path.exists(class_folder_path) and os.path.isdir(class_folder_path):
            for json_file in os.listdir(class_folder_path):
                # json 파일 인식
                if json_file.endswith('.json'):
                    json_file_path = os.path.join(class_folder_path, json_file)
                    # 함수의 반환 값이 False라면 예외 처리를 통해 올바르지 않은 라벨링이라는 뜻
                    if not convert_json_to_yolo(json_file_path, class_folder_path):
                        # 에러가 발생하므로 파일을 지워준다.
                        print(f"Deleting files related to {json_file_path}")
                        os.remove(json_file_path)
                        # 같은 파일 이름의 이미지도 지워준다.
                        image_file_name = json_file.replace('.json', '.jpg')  # Assuming the images are .jpg files
                        image_file_path = os.path.join(image_dir, class_folder, image_file_name)
                        if os.path.exists(image_file_path):
                            os.remove(image_file_path)
                            print(f"Deleted image file: {image_file_path}")

                        # txt파일이 만들어졌다면, 그것 또한 지워준다.
                        txt_file_path = json_file_path.replace('.json', '.txt')
                        if os.path.exists(txt_file_path):
                            os.remove(txt_file_path)
                            print(f"Deleted label file: {txt_file_path}")
                    else: print(f"Converted {json_file_path} to YOLO format.")

    print("Conversion completed.")  


def class_label_Edit():
    # 음식 클래스와 인덱스를 mapping하는 작업 (딕셔러니 구조로 변환)
    class_to_index = {folder:index for index, folder in enumerate(folders_list)}

    base_dir = '/content/drive/MyDrive/fix_data/labels/test/'

    # folder 구조를 iterate한다.
    for class_name, class_index in class_to_index.items():
        folder_path = os.path.join(base_dir, class_name)
        if os.path.isdir(folder_path):
            # 음식 class안에 있는 모든 txt파일을 가져온다.
            txt_files = glob.glob(os.path.join(folder_path, '*.txt'))

            for txt_file in txt_files:
                with open(txt_file, 'r', encoding='utf-8') as file:
                    lines = file.readlines()

                # 각 줄에 대해서 label 값을 올바른 인덱스로 mapping해준다.
                updated_lines = []
                for line in lines:
                    parts = line.strip().split()
                    if parts:
                        parts[0] = str(class_index)  # Update the label
                        updated_lines.append(' '.join(parts))

                with open(txt_file, 'w', encoding='utf-8') as file:
                    file.write('\n'.join(updated_lines))

        print(f"{class_name} label files updated successfully.")