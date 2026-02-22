from flask import Flask, render_template, request, send_file, redirect, send_from_directory
import os
from werkzeug.utils import secure_filename
from PIL import Image
from PyPDF2 import PdfReader, PdfWriter

# Inisialisasi app hanya satu kali di awal
app = Flask(__name__, template_folder='../templates')
app.secret_key = "secret_aman_sekali"

UPLOAD_FOLDER = '/tmp'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'pdf'}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sitemap.xml')
def sitemap():
    # os.getcwd() akan mengambil direktori utama proyek di Vercel
    return send_from_directory(os.getcwd(), 'sitemap.xml', mimetype='application/xml')

# Rute tambahan untuk PWA
@app.route('/manifest.json')
def manifest():
    return send_from_directory(os.getcwd(), 'manifest.json', mimetype='application/json')

@app.route('/sw.js')
def sw():
    return send_from_directory(os.getcwd(), 'sw.js', mimetype='application/javascript')

# TAMBAHKAN INI: Agar browser bisa membaca ikon di folder static
@app.route('/static/<path:filename>')
def send_static(filename):
    # Mencari folder static di direktori saat ini
    return send_from_directory(os.path.join(app.root_path, '..', 'static'), filename)
    
@app.route('/compress', methods=['POST'])
def compress():
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return "File tidak valid!"

    filename = secure_filename(file.filename)
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    output_path = os.path.join(UPLOAD_FOLDER, "compressed_" + filename)

    file.save(input_path)
    ext = filename.rsplit('.', 1)[1].lower()

    try:
        if ext in ['jpg', 'jpeg', 'png']:
            img = Image.open(input_path)
            if img.mode in ("RGBA", "P"): img = img.convert("RGB")
            img.save(output_path, "JPEG", optimize=True, quality=30)
        elif ext == 'pdf':
            reader = PdfReader(input_path)
            writer = PdfWriter()
            for page in reader.pages:
                writer.add_page(page)
            with open(output_path, "wb") as f:
                writer.write(f)

        return send_file(output_path, as_attachment=True)
    except Exception as e:
        return f"Error: {e}"



