from flask import Flask, render_template, request, send_file, flash, redirect
import os
import time
import threading
from werkzeug.utils import secure_filename
from PIL import Image
from PyPDF2 import PdfReader, PdfWriter

app = Flask(__name__)
app.secret_key = "secret_super_aman" # Diperlukan untuk fitur pesan error (flash)

UPLOAD_FOLDER = 'uploads'
COMPRESSED_FOLDER = 'compressed'
# Batasi format file yang diizinkan
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'docx', 'xlsx'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(COMPRESSED_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Thread pembersih otomatis tetap sama
def auto_delete_files():
    while True:
        time.sleep(600)
        now = time.time()
        for folder in [UPLOAD_FOLDER, COMPRESSED_FOLDER]:
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                if os.stat(file_path).st_mtime < now - 1800:
                    try:
                        os.remove(file_path)
                    except:
                        pass

threading.Thread(target=auto_delete_files, daemon=True).start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compress', methods=['POST'])
def compress():
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    
    if file.filename == '':
        return "Tidak ada file yang dipilih"

    if file and allowed_file(file.filename):
        # Membersihkan nama file dari karakter berbahaya
        filename = secure_filename(file.filename)
        input_path = os.path.join(UPLOAD_FOLDER, filename)
        output_filename = "compressed_" + filename
        output_path = os.path.join(COMPRESSED_FOLDER, output_filename)
        
        file.save(input_path)
        filesize = os.path.getsize(input_path)
        ext = filename.rsplit('.', 1)[1].lower()

        try:
            # PROSES GAMBAR
            if ext in ['jpg', 'jpeg', 'png']:
                img = Image.open(input_path)
                if img.mode in ("RGBA", "P"): img = img.convert("RGB")
                q = 20 if filesize <= 5 * 1024 * 1024 else 40
                img.save(output_path, "JPEG", optimize=True, quality=q)

            # PROSES PDF
            elif ext == 'pdf':
                reader = PdfReader(input_path)
                writer = PdfWriter()
                for page in reader.pages:
                    writer.add_page(page)
                with open(output_path, "wb") as f:
                    writer.write(f)
            
            # (Tambahkan logika Word/Excel di sini jika diperlukan library tambahan)
            else:
                return "Format ini akan segera didukung!"

            return send_file(output_path, as_attachment=True)
        except Exception as e:
            return f"Error: {e}"
    
    return "Tipe file tidak diizinkan!"
