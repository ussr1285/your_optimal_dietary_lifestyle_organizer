from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory
import os
import Food_recommend as fr
from werkzeug.utils import secure_filename
import model

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
# app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # 정적 파일 캐시 비활성화

# @app.after_request
# def set_response_headers(response):
#     response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
#     response.headers['Pragma'] = 'no-cache'
#     response.headers['Expires'] = '0'
#     return response

yolo = model.YOLOModel()

import shutil
import os

def delete_folder(path):
    # 폴더가 존재하는지 확인
    if os.path.exists(path):
        # 폴더와 폴더 내 모든 내용 삭제
        shutil.rmtree(path)
        print(f"The folder '{path}' has been deleted.")
    else:
        print(f"The folder '{path}' does not exist.")

def check_directory():
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    for meal in MEALS:
        meal_folder = os.path.join(UPLOAD_FOLDER, meal)
        if not os.path.exists(meal_folder):
            os.makedirs(meal_folder)

@app.route('/')
def home():
    # 삭제할 폴더 경로
    delete_folder("uploads")
    check_directory()
    return render_template('index.html')

MEALS = ['breakfast', 'lunch', 'dinner']
NUTRIENTS = ['kcal', 'protein', 'fat', 'carb', 'sugars', 'sodium']
### image upload section (meal:= breakfast, lunch, dinner)

def get_next_file_index(meal):
    meal_folder = os.path.join(UPLOAD_FOLDER, meal)
    files = os.listdir(meal_folder)
    indices = [int(f.split('_')[1].split('.')[0]) for f in files if f.startswith('file_')]
    return max(indices, default=-1) + 1

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
        print(os.path.splitext(secure_filename(file.filename)))
        file_extension = os.path.splitext(secure_filename(file.filename))[1]
        new_filename = f"file_{next_index}{file_extension}"
        meal_folder = os.path.join(UPLOAD_FOLDER, meal)
        filepath = os.path.join(meal_folder, new_filename)
        file.save(filepath)
        return jsonify({"message": "File uploaded successfully", "filepath": filepath})

@app.route('/uploads/<meal>/<filename>')
def uploaded_file(meal, filename):
    if meal not in MEALS:
        return "Invalid meal type", 400
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], meal), filename)

@app.route('/submit', methods=['POST'])
def submit():
    gender = request.form.get('gender')
    age = request.form.get('age')
    
    image_path = dict()
    food_list = []
    for meal in MEALS:
        meal_folder = os.path.join(UPLOAD_FOLDER, meal)
        if not os.listdir(meal_folder): 
            food_list.append([])
            continue
        last_filename = ''.join((os.listdir(meal_folder)[-1]))
        filepath = '/'.join(['.', UPLOAD_FOLDER, meal, last_filename])
        image_path[f'{meal}'] = filepath
        food_list.append(yolo.img_2_txt(filepath))
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

    for i in range(len(MEALS)):
        food[f'{MEALS[i]}']['name'] = food_list[i]
        for j in range(len(NUTRIENTS)):
            food[f'{MEALS[i]}'][f'{NUTRIENTS[j]}'] = food_nutrient[i][j] if food_nutrient[i][j] == food_nutrient[i][j] else 0.0 # split_Nutrient(food_nutrient[i][j])
    for j in range(len(NUTRIENTS)):
        today = round(food['breakfast'][f'{NUTRIENTS[j]}'] + food['lunch'][f'{NUTRIENTS[j]}'] + food['dinner'][f'{NUTRIENTS[j]}'], 2)
        need = results.get_need_nutrition()[j] if results.get_need_nutrition()[j] == results.get_need_nutrition()[j] else 0.0
        need = round(need, 2)
        food['today'][f'{NUTRIENTS[j]}'] = today
        food['need'][f'{NUTRIENTS[j]}'] = need
    food['recommend']['one'] = results.get_recommend_food()[0]
    food['recommend']['two'] = results.get_recommend_food()[1]
    food['recommend']['three'] = results.get_recommend_food()[2]
    
    return render_template('result.html', food=food, image_path=image_path)

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(host='0.0.0.0', debug=True)

