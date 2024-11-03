from flask import Flask, request, jsonify, render_template, redirect
import os
from docx import Document
import fitz
from summarize import LLMSummarize

url = '' # URL для доступу к модели Ollama

summary = LLMSummarize(url)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST']) # функция для загрузки файла
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        input_text = ''
        if file.filename.endswith('.txt'):
            with open(file_path, 'r') as f:
                input_text = f.read()
        elif file.filename.endswith('.docx'):
            doc = Document(file_path)
            for para in doc.paragraphs:
                input_text += para.text + '\n'
        elif file.filename.endswith('.pdf'):
            doc = fitz.open(file_path)
            for page in doc:
                input_text += page.get_text() + '\n'

        return jsonify({'inputText': input_text})


@app.route('/compress', methods=['POST']) # функция для сжатия текста
def compress():
    data = request.json
    input_text = data.get('inputText')
    compression_level = data.get('compressionLevel')

    if compression_level == "strong": # сильное сжатия
        cf = 'strong_summary'
    else:
        cf = 'weak_summary' # слабое сжатие
        
    compressed_text = ''.join(summary.compress(input_text, cf)) # обращение к функции compress

    return jsonify({'compressedText': compressed_text})


if __name__ == '__main__':
    app.run(debug=True)