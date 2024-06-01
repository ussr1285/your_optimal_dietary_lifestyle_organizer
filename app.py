from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory
import os
import sys
import Food_recommend as fr
from werkzeug.utils import secure_filename
import model

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # 정적 파일 캐시 비활성화

@app.after_request
def set_response_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

yolo = model.YOLOModel()

# 파일 확장자 확인
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def home():
    return render_template('index.html')

### image upload section (meal:= breakfast, lunch, dinner)
@app.route('/uploadtest')
def upload_test():
    return render_template('uploadtest.html')

MEALS = ['breakfast', 'lunch', 'dinner']
for meal in MEALS:
    meal_folder = os.path.join(UPLOAD_FOLDER, meal)
    if not os.path.exists(meal_folder):
        os.makedirs(meal_folder)

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
### /image upload section

# def render_food_template(food_list, food_nutrient, results):
#     template_data = {'user_result': results}

#     for i in range(min(len(food_list), len(MEALS))):
#         meal = MEALS[i]
#         template_data[meal] = food_list[i]
#         template_data[f'{meal}_nutrient'] = food_nutrient[i]

#     return render_template('result.html', **template_data)

@app.route('/submit', methods=['POST'])
def submit():
    gender = request.form.get('gender')
    age = request.form.get('age')

    food_list = []
    for meal in MEALS:
        meal_folder = os.path.join(UPLOAD_FOLDER, meal)
        last_filename = ''.join((os.listdir(meal_folder)[:-1]))
        filepath = '/'.join(['.', UPLOAD_FOLDER, meal, last_filename])
        food_list.append(yolo.img_2_txt(filepath))

    results = fr.Nutrient(food_list=food_list, gender=gender, age=int(age))
    food_nutrient = results.get_nutrient_ingestion()
    # print(food_nutrient)

    template_data = {'user_result': results}

    for i in range(min(len(food_list), len(MEALS))):
        meal = MEALS[i]
        template_data[meal] = food_list[i]
        template_data[f'{meal}_nutrient'] = food_nutrient[i]

    return render_template('result.html', **template_data)
    # return render_food_template(food_list, food_nutrient, results)

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(host='0.0.0.0', debug=True)


# @app.route('/test')
# def testhome():
#     return render_template('index_test.html')



# @app.route('/submit_test', methods=['POST'])
# def submit_test():
#     gender = request.form.get('gender')
#     age = request.form.get('age')

#     food_list = yolo.img_2_txt("./uploads/dinner/file_0.jpg") 
    
#     results = fr.Nutrient((food_list), gender=gender, age=int(age))
#     return render_template('result_test.html', food=food_list, user_result=results)
