import sys
from types import ModuleType

# Android FMOD Mock (prevents Error 500)
if 'fmod_toolkit' not in sys.modules:
    mock = ModuleType('fmod_toolkit')
    sys.modules['fmod_toolkit'] = mock
    mock.get_pyfmodex_system_instance = lambda *a, **k: None
    mock.raw_to_wav = lambda *a, **k: None
    mock.sound_to_wav = lambda *a, **k: None
    mock.subsound_to_wav = lambda *a, **k: None

import io, base64, UnityPy, texture2ddecoder
from flask import Flask, render_template_string, request, send_file
from PIL import Image

app = Flask(__name__)
s = {'env': None, 'tex': {}, 'name': None, 'msg': None, 'err': False}

H = '''
<!DOCTYPE html><html><head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>NOT UABE</title>
<style>
    body { font-family: monospace; background: #0a0a0a; color: #888; margin: 0; padding: 15px; font-size: 13px; }
    .container { max-width: 600px; margin: 0 auto; }
    .top-bar { border-bottom: 1px solid #222; padding-bottom: 15px; margin-bottom: 20px; }
    .title { color: #fff; font-weight: bold; font-size: 18px; letter-spacing: 2px; }
    .btn-flat { background: transparent; border: 1px solid #333; color: #ccc; padding: 7px 15px; cursor: pointer; font-family: inherit; display: inline-block; text-decoration: none; }
    .btn-flat:hover { border-color: #555; color: #fff; }
    .target-info { color: #4a90e2; margin-left: 10px; }
    .status { margin-top: 15px; padding: 5px 10px; display: inline-block; font-weight: bold; }
    .status.ok { color: #2ea043; border: 1px solid #1a3a1a; }
    .status.bad { color: #da3633; border: 1px solid #67060c; }
    .asset-row { display: flex; align-items: flex-start; padding: 20px 0; border-bottom: 1px solid #151515; }
    .preview { width: 64px; height: 64px; background: #000; border: 1px solid #222; display: flex; align-items: center; justify-content: center; overflow: hidden; flex-shrink: 0; }
    img { max-width: 100%; max-height: 100%; image-rendering: pixelated; }
    .meta { margin-left: 20px; flex-grow: 1; }
    .name { color: #ddd; font-weight: bold; font-size: 14px; display: block; margin-bottom: 5px; }
    .details { font-size: 11px; color: #555; line-height: 1.4; margin-bottom: 10px; }
    .actions { display: flex; gap: 10px; }
    .export-box { margin-top: 40px; border: 1px solid #1a3a1a; padding: 20px; text-align: center; }
    .export-link { color: #2ea043; text-decoration: none; font-weight: bold; font-size: 14px; }
</style></head><body>
<div class="container">
    <div class="top-bar">
        <div class="title">NOT UABE</div>
        <div style="margin-top:15px;">
            <form action="/up" method="post" enctype="multipart/form-data">
                <label class="btn-flat">Upload Bundle<input type="file" name="f" onchange="this.form.submit()" style="display:none"></label>
                {% if name %}<span class="target-info">{{name}}</span>{% endif %}
            </form>
        </div>
        {% if msg %}<div class="status {{ 'bad' if err else 'ok' }}">{{ msg }}</div>{% endif %}
    </div>
    {% if tex %}{% for id, t in tex.items() %}
    <div class="asset-row">
        <div class="preview">{% if t.img %}<img src="data:image/png;base64,{{t.img}}">{% else %}N/A{% endif %}</div>
        <div class="meta">
            <span class="name">{{t.n}}</span>
            <div class="details">PID: {{id}} | Res: {{t.r}} | Fmt: {{t.f}}</div>
            <div class="actions">
                <form action="/rep" method="post" enctype="multipart/form-data">
                    <input type="hidden" name="id" value="{{id}}">
                    <label class="btn-flat" style="font-size:10px; padding: 4px 8px;">Replace Texture<input type="file" name="i" onchange="this.form.submit()" style="display:none"></label>
                </form>
                <a href="/exp/{{id}}" class="btn-flat" style="font-size:10px; padding: 4px 8px;">Export PNG</a>
            </div>
        </div>
    </div>
    {% endfor %}
    <div class="export-box"><a href="/dl" class="export-link">BUILD & DOWNLOAD MODDED BUNDLE</a></div>
    {% endif %}
</div>
</body></html>
'''

def force_decode(obj):
    try:
        # 🔄 FIX: Remove flip for viewing/export. UnityPy default is correct (logo bottom).
        return obj.image
    except:
        try:
            w, h, data = obj.m_Width, obj.m_Height, obj.image_data
            fmt = str(obj.m_TextureFormat)
            if "ASTC" in fmt: dec = texture2ddecoder.decode_astc(data, w, h, 4, 4)
            elif "ETC2" in fmt: dec = texture2ddecoder.decode_etc2(data, w, h)
            else: dec = texture2ddecoder.decode_etc1(data, w, h)
            # 🔄 FIX: Remove flip here too
            return Image.frombytes("RGBA", (w, h), dec, "raw", "BGRA")
        except: return None

@app.route('/')
def index(): return render_template_string(H, tex=s['tex'], name=s['name'], msg=s['msg'], err=s['err'])

@app.route('/up', methods=['POST'])
def up():
    f = request.files.get('f')
    if not f: return index()
    s.update({'tex': {}, 'name': f.filename, 'msg': 'Bundle loaded', 'err': False})
    try:
        env = UnityPy.load(f.read())
        s['env'] = env
        for obj in env.objects:
            if obj.type.name == "Texture2D":
                try:
                    d = obj.read()
                    img = force_decode(d)
                    b64 = None
                    if img:
                        prev = img.copy()
                        prev.thumbnail((128, 128))
                        buf = io.BytesIO()
                        prev.save(buf, format='PNG')
                        b64 = base64.b64encode(buf.getvalue()).decode()
                    s['tex'][str(obj.path_id)] = {'n': d.m_Name or f"Asset_{obj.path_id}", 'r': f"{d.m_Width}x{d.m_Height}", 'f': str(d.m_TextureFormat).split('.')[-1], 'img': b64, 'obj': d}
                except: continue
    except Exception as e: s['msg'] = f"Load error: {str(e)}"; s['err'] = True
    return index()

@app.route('/rep', methods=['POST'])
def rep():
    tid, f = request.form.get('id'), request.files.get('i')
    if tid and f and s['env']:
        try:
            asset = s['tex'][tid]['obj']
            # ✅ FIX: Replace without flipping. Save "as is" to bundle.
            new_img = Image.open(f.stream)
            asset.image = new_img
            asset.save()
            s['msg'] = f"Success: {asset.m_Name} replaced"; s['err'] = False
            
            # Update Preview (Same view, no additional flip needed if we are uploading 'correct' view)
            p = new_img
            p.thumbnail((128, 128))
            buf = io.BytesIO()
            p.save(buf, format='PNG')
            s['tex'][tid]['img'] = base64.b64encode(buf.getvalue()).decode()
        except Exception as e: s['msg'] = f"Replace error: {str(e)}"; s['err'] = True
    return index()

@app.route('/exp/<tid>')
def exp(tid):
    if tid in s['tex']:
        asset = s['tex'][tid]['obj']
        # ✅ FIX: Export "as is" using force_decode. PNG will be "straight" (logo bottom).
        img = force_decode(asset)
        if img:
            buf = io.BytesIO()
            img.save(buf, format='PNG')
            buf.seek(0)
            return send_file(buf, as_attachment=True, download_name=f"{asset.m_Name}.png")
    return "Error"

@app.route('/dl')
def dl():
    if not s['env']: return "No data"
    return send_file(io.BytesIO(s['env'].file.save()), as_attachment=True, download_name=f"mod_{s['name']}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

