# app.py
from flask import Flask, render_template, request, jsonify, send_file
import os
import json
from utils import load_document
from question_generator import QwenQuestionGenerator

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

generator = QwenQuestionGenerator()
current_exam = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    global current_exam
    file = request.files['file']
    if not file or not (file.filename.endswith('.pdf') or file.filename.endswith('.docx')):
        return jsonify({"error": "仅支持 PDF 或 Word 文件"}), 400
    
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    
    # 加载文档并生成试题（简化：只取前3段）
    chunks = load_document(filepath)[:3]
    exam = []
    for chunk in chunks:
        q = generator.generate_questions(chunk.page_content)
        if q:
            exam.append(q)
    
    current_exam = exam
    return jsonify({"questions": exam})

@app.route('/submit', methods=['POST'])
def submit_answers():
    user_answers = request.json.get('answers', [])
    score = 0
    results = []
    for i, ans in enumerate(user_answers):
        correct = current_exam[i]['answer']
        is_correct = ans == correct
        if is_correct:
            score += 1
        results.append({
            "question": current_exam[i]['question'],
            "your_answer": ans,
            "correct_answer": correct,
            "explanation": current_exam[i]['explanation'],
            "is_correct": is_correct
        })
    total = len(current_exam)
    return jsonify({
        "score": f"{score}/{total}",
        "results": results
    })

if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.1', port=5000)