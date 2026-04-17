import os
import base64
from flask import Flask, render_template_string, request, send_file
import UnityPy
from PIL import Image
import io

app = Flask(__name__)
UPLOAD_FOLDER = '/sdcard/Download'
CURRENT_ENV = None
CURRENT_TEXTURES = {}

# HTML-шаблон (интерфейс)
HTML = '''
<!view>
<html>
<head>
    <title>Unity Texture Modder</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: sans-serif; background: #1a1a1a; color: white; padding: 20px; }
        .card { background: #2a2a2a; padding: 15px; border-radius: 10px; margin-bottom: 10px; border: 1px solid #444; }
        img { max-width: 100px; display: block; margin-top: 10px; border: 1px solid #555; }
        button { background: #4CAF50; color: white; border: none; padding: 10px; border-radius: 5px; cursor: pointer; }
        input { background: #333; color: white; border: 1px solid #555; padding: 5px; }
    </style>
</head>
<body>
    <h1>Unity Modder GUI</h1>
    
    <div class="card">
        <h3>Шаг 1: Загрузка бандла</h3>
        <form action="/load" method="post">
            <input type="text" name="path" placeholder="Путь к файлу (напр. /sdcard/Download/Boombot.bundle)" style="width: 80%;">
            <button type="submit">Открыть</button>
        </form>
    </div>

    {% if textures %}
    <div class="card">
        <h3>Шаг 2: Выбор текстуры и замена</h3>
        {% for id, tex in textures.items() %}
        <div style="display: flex; align-items: center; border-bottom: 1px solid #444; padding: 10px;">
            <div style="flex-grow: 1;">
                <b>{{ tex.name }}</b> (ID: {{ id }})
                <img src="data:image/png;base64,{{ tex.img_data }}">
            </div>
            <form action="/replace" method="post" enctype="multipart/form-data">
                <input type="hidden" name="tex_id" value="{{ id }}">
                <input type="file" name="new_img" accept="image/png">
                <button type="submit">Заменить</button>
            </form>
        </div>
        {% endfor %}
    </div>
    <div class="card">
        <h3>Шаг 3: Сохранение</h3>
        <form action="/save" method="post">
            <input type="text" name="out_name" value="modded.bundle">
            <button type="submit" style="background: #2196F3;">Скачать результат</button>
        </form>
    </div>
    {% endif %}
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML, textures=CURRENT_TEXTURES)

@app.route('/load', method=['POST'])
def load_bundle():
    global CURRENT_ENV, CURRENT_TEXTURES
    path = request.form.get('path')
    if not os.path.exists(path): return "Файл не найден"
    
    CURRENT_ENV = UnityPy.load(path)
    CURRENT_TEXTURES = {}
    
    for obj in CURRENT_ENV.objects:
        if obj.type.name == "Texture2D":
            data = obj.read()
            # Генерируем превью
            try:
                img = data.image
                buf = io.BytesIO()
                img.save(buf, format='PNG')
                img_b64 = base64.b64encode(buf.getvalue()).decode()
                CURRENT_TEXTURES[obj.path_id] = {
                    'name': getattr(data, 'name', 'Unknown'),
                    'img_data': img_b64,
                    'obj': data
                }
            except: continue
    return render_template_string(HTML, textures=CURRENT_TEXTURES)

@app.route('/replace', methods=['POST'])
def replace():
    tex_id = int(request.form.get('tex_id'))
    file = request.files['new_img']
    if file and CURRENT_TEXTURES:
        img = Image.open(file.stream)
        target = CURRENT_TEXTURES[tex_id]['obj']
        target.image = img
        target.save()
        return "Текстура заменена! <a href='/'>Назад</a>"
    return "Ошибка"

@app.route('/save', methods=['POST'])
def save():
    out_name = request.form.get('out_name', 'modded.bundle')
    out_path = os.path.join(UPLOAD_FOLDER, out_name)
    with open(out_path, "wb") as f:
        f.write(CURRENT_ENV.file.save())
    return send_file(out_path, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

