from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory
import os
import shutil
import Food_recommend as fr
from werkzeug.utils import secure_filename
import model

# Flask 애플리케이션 인스턴스 생성
app = Flask(__name__)

# 업로드 파일(사진)이 저장될 서버의 폴더 경로 설정
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# YOLO 모델 로드
yolo = model.YOLOModel()

MEALS = ['breakfast', 'lunch', 'dinner']
NUTRIENTS = ['kcal', 'protein', 'fat', 'carb', 'sugars', 'sodium']

# path 폴더의 내부를 재귀적으로 삭제
# 초기에 선택된 이미지가 없도록 초기화하는 용도
def delete_folder(path):
    if os.path.exists(path):
        shutil.rmtree(path)
        print(f"The folder '{path}' has been deleted.")
    else:
        print(f"The folder '{path}' does not exist.")

# 업로드 폴더 구조 개설
def check_directory():
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    for meal in MEALS:
        meal_folder = os.path.join(UPLOAD_FOLDER, meal)
        if not os.path.exists(meal_folder):
            os.makedirs(meal_folder)

# 메인 페이지
@app.route('/')
def home():
    # 새로고침 시 업로드 폴더 내부 파일 삭제
    delete_folder(UPLOAD_FOLDER)
    check_directory()
    return render_template('index.html')

# 업로드 폴더 내 다음 파일 index를 반환하는 함수
def get_next_file_index(meal):
    meal_folder = os.path.join(UPLOAD_FOLDER, meal)
    files = os.listdir(meal_folder)
    indices = [int(f.split('_')[1].split('.')[0]) for f in files if f.startswith('file_')]
    return max(indices, default=-1) + 1

# @definition : 이미지를 받아 업로드 폴더에 저장
# <meal> : breakfast, lunch, dinner 각 식사에 따라 별도 저장
@app.route('/upload/<meal>', methods=['POST'])
def upload_file(meal):
    if meal not in MEALS:
        return "Invalid meal type", 400
    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400
    if file:
        next_index = get_next_file_index(meal)
        file_extension = os.path.splitext(secure_filename(file.filename))[1]
        new_filename = f"file_{next_index}{file_extension}"
        meal_folder = os.path.join(UPLOAD_FOLDER, meal)
        filepath = os.path.join(meal_folder, new_filename)
        file.save(filepath)
        return jsonify({"message": "File uploaded successfully", "filepath": filepath})

# @definition : 요청받은 이미지를 전송
# <meal> : breakfast, lunch, dinner 업로드 파일 경로 
# <filename> : file_0, file_1, ... 저장된 이미지 번호, 번호가 클 수록 최신의 이미지
@app.route('/uploads/<meal>/<filename>')
def uploaded_file(meal, filename):
    if meal not in MEALS:
        return "Invalid meal type", 400
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], meal), filename)

def check_nan_value(num):
    return num if num == num else 0.0

# 분석 결과 페이지로 연결
@app.route('/submit', methods=['POST'])
def submit():
    # html form에서 입력받은 성별, 나이 정보 저장
    gender = request.form.get('gender')
    age = request.form.get('age')
    
    image_path = dict()
    food_list = []

    # 각 식사별로 업로드된 이미지 파일 처리
    for meal in MEALS:
        meal_folder = os.path.join(UPLOAD_FOLDER, meal)
        if not os.listdir(meal_folder): 
            food_list.append([])
            continue
        last_filename = ''.join((os.listdir(meal_folder)[-1]))
        filepath = '/'.join(['.', UPLOAD_FOLDER, meal, last_filename])
        image_path[f'{meal}'] = filepath
        # 이미지에 해당하는 음식 텍스트로 변환하여 food_list에 저장
        food_list.append(yolo.img_2_txt(filepath))

    # 음식 정보를 바탕으로 영양소 분석
    results = fr.Nutrient(food_list=food_list, gender=gender, age=int(age))
    food_nutrient = results.get_nutrient_ingestion()

    food = dict(
        breakfast=dict(),
        lunch=dict(),
        dinner=dict(),
        today=dict(),
        need=dict(),
        recommend=dict()
    )

    food_need = results.get_need_nutrition()
    food_recommend = results.get_recommend_food()

    # 음식 정보를 food 딕셔너리에 저장
    for i in range(len(MEALS)):
        food[MEALS[i]]['name'] = food_list[i]
        for j in range(len(NUTRIENTS)):
            food[MEALS[i]][NUTRIENTS[j]] = check_nan_value(food_nutrient[i][j])
            if not NUTRIENTS[j] in food['today']:
                food['today'][NUTRIENTS[j]] = 0.0
            food['today'][NUTRIENTS[j]] += check_nan_value(food_nutrient[i][j])
            
    # 오늘 섭취한 영양소와 필요한 영양소 계산
    for j in range(len(NUTRIENTS)):
        today = round(food['today'][NUTRIENTS[j]], 2)
        need = round(check_nan_value(food_need[j]), 2)
        food['today'][NUTRIENTS[j]] = today
        food['need'][NUTRIENTS[j]] = need
    
    # 추천 음식 반환
    food['recommend']['one'] = food_recommend[0]
    food['recommend']['two'] = food_recommend[1]
    food['recommend']['three'] = food_recommend[2]
    
    return render_template('result.html', food=food, image_path=image_path)

# 서버 실행 (python app.py)
if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(host='0.0.0.0', debug=True)

