from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory
import os
import Food_recommend as fr
from werkzeug.utils import secure_filename
import model

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

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

@app.route('/submit', methods=['POST'])
def submit():
    gender = request.form.get('gender')
    age = request.form.get('age')
    # breakfast = request.form.getlist('breakfast')
    # lunch = request.form.getlist('lunch')
    # dinner = request.form.getlist('dinner')
    # food_list = [breakfast, lunch, dinner]
    # yolo.img_2_txt('uploads/' + request.form.get('filename'), food_list)
    food_list = yolo.img_2_txt('uploads/A220132XX_33201.jpg')
    user = fr.Nutrient(food_list, gender=gender, age=int(age))
    return render_template('result.html', food=food_list, user_result=user)

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(host='0.0.0.0', debug=True)
