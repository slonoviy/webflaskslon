from flask import Flask, render_template, request, redirect, url_for, abort
from PIL import Image
import os
from werkzeug.utils import secure_filename
import numpy as np
from forms import MyForm
import matplotlib.pyplot as plt

app = Flask(__name__, static_folder='static')
app.config['UPLOAD_FOLDER'] = 'upload'
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['RECAPTCHA_PUBLIC_KEY'] = '6LeSKD8mAAAAAPZABMyviBcTwpd02IemRBLgl418'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6LeSKD8mAAAAALNwk15ctdlMsLHoQPrJhLTtDo-V'
app.config['RECAPTCHA_OPTIONS'] = {'theme': 'white'}

@app.route('/protected')
def protected():
    # Проверяем, решена ли reCAPTCHA
    if not request.args.get('captcha') == 'solved':
        return 'Вы не решили капчу :('  # Возвращает ошибку 403 (Forbidden), если капча не решена
    # Здесь можно разместить содержимое защищенной страницы
    return redirect(url_for('image', captcha='solved'))

@app.route('/', methods=['GET', 'POST'])
def submit():
    form = MyForm()
    if form.validate_on_submit():
        return redirect(url_for('protected', captcha='solved'))

    return render_template('index.html', form=form)

@app.route('/image', methods=['GET', 'POST'])
def image():

    return render_template('upload-image.html')

@app.route('/image/upload', methods=['GET','POST'])
def upload():
    # Получаем загруженный файл из формы
    file = request.files['image']

    # Сохраняем файл на сервере
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    # Выполняем необходимые операции с изображением
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    image_changed_path = "static/changed"
    # Обработка изображения
    swap_and_save(image_path,filename,image_changed_path)
    graname = filename.split('.')[0]+"_graph.png"
    plot_color_distribution(image_path,graname)
    return render_template("changed_image.html",filename = filename, graph_name = graname)

def swap_and_save(image_path, file_name,image_folder):

    img = Image.open(image_path)

    np_img = np.array(img)

    height, width = np_img.shape[:2]
    half_height = height // 2
    half_width = width // 2
    up_left = np_img[:half_height, :half_width]
    up_Right = np_img[:half_height, half_width:]
    down_left = np_img[half_height:, :half_width]
    down_Right = np_img[half_height:, half_width:]

    Up_left = Image.fromarray(up_left)
    Up_Right = Image.fromarray(up_Right)
    Down_left = Image.fromarray(down_left)
    Down_Right = Image.fromarray(down_Right)

    Up_left.save(f"{image_folder}/left_up_{file_name}")
    Up_Right.save(f"{image_folder}/Right_up_{file_name}")
    Down_left.save(f"{image_folder}/left_down_{file_name}")
    Down_Right.save(f"{image_folder}/Right_down_{file_name}")

def plot_color_distribution(image_path,name):
    # Загрузка изображения с помощью Pillow
    image = Image.open(image_path)

    # Преобразование изображения в массив NumPy
    image_array = np.array(image)

    # Получение гистограммы распределения цветов по каналам
    red_hist = np.histogram(image_array[:, :, 0], bins=256, range=(0, 256))
    green_hist = np.histogram(image_array[:, :, 1], bins=256, range=(0, 256))
    blue_hist = np.histogram(image_array[:, :, 2], bins=256, range=(0, 256))

    # Рисование графика распределения цветов
    plt.figure(figsize=(10, 6))
    plt.title('Color Distribution')
    plt.xlabel('Color Intensity')
    plt.ylabel('Frequency')
    plt.xlim(0, 255)
    plt.plot(red_hist[1][:-1], red_hist[0], color='red', label='Red')
    plt.plot(green_hist[1][:-1], green_hist[0], color='green', label='Green')
    plt.plot(blue_hist[1][:-1], blue_hist[0], color='blue', label='Blue')
    plt.legend()

    plt.savefig(f"static/graph/{name}", dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == '__main__':
    app.run()