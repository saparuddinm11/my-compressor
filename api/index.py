from flask import Flask, render_template, request, send_file, flash, redirect
import os
from werkzeug.utils import secure_filename
from PIL import Image
from PyPDF2 import PdfReader, PdfWriter

app = Flask(__name__)
app.secret_key = "secret_super_aman"

# Gunakan folder /tmp karena Vercel hanya mengizinkan penulisan file di sana
UPLOAD_FOLDER = '/tmp'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
        filename = secure_filename(file.filename)
        input_path = os.path.join(UPLOAD_FOLDER, filename)
        output_path = os.path.join(UPLOAD_FOLDER, "compressed_" + filename)
        
        file.save(input_path)
        filesize = os.path.getsize(input_path)
        ext = filename.rsplit('.', 1)[1].lower()

        try:
            if ext in ['jpg', 'jpeg', 'png']:
                img = Image.open(input_path)
                if img.mode in ("RGBA", "P"): img = img.convert("RGB")
                q = 20 if filesize <= 5 * 1024 * 1024 else 40
                img.save(output_path, "JPEG", optimize=True, quality=q)

            elif ext == 'pdf':
                reader = PdfReader(input_path)
                writer = PdfWriter()
                for page in reader.pages:
                    writer.add_page(page)
                with open(output_path, "wb") as f:
                    writer.write(f)
            else:
                return "Format tidak didukung"

            return send_file(output_path, as_attachment=True)
        except Exception as e:
            return f"Error: {e}"
    
    return "Tipe file tidak diizinkan!"
