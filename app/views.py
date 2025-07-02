from flask import Blueprint, jsonify, request
from random import sample
from app.models import Task
from app import db

student = Blueprint('student', __name__)

@student.route('/generate-assessment')
def generate_assessment():
    # Получаем по 1 заданию каждого типа и сложности
    tasks = []
    
    # Легкий уровень
    tasks.append(Task.query.filter_by(category='addition', difficulty='easy').order_by(db.func.random()).first())
    tasks.append(Task.query.filter_by(category='subtraction', difficulty='easy').order_by(db.func.random()).first())
    tasks.append(Task.query.filter_by(category='multiplication', difficulty='easy').order_by(db.func.random()).first())
    tasks.append(Task.query.filter_by(category='division', difficulty='easy').order_by(db.func.random()).first())
    
    # Средний уровень
    tasks.append(Task.query.filter_by(category='addition', difficulty='medium').order_by(db.func.random()).first())
    tasks.append(Task.query.filter_by(category='subtraction', difficulty='medium').order_by(db.func.random()).first())
    tasks.append(Task.query.filter_by(category='multiplication', difficulty='medium').order_by(db.func.random()).first())
    tasks.append(Task.query.filter_by(category='division', difficulty='medium').order_by(db.func.random()).first())
    
    # Сложный уровень
    tasks.append(Task.query.filter_by(category='addition', difficulty='hard').order_by(db.func.random()).first())
    tasks.append(Task.query.filter_by(category='subtraction', difficulty='hard').order_by(db.func.random()).first())
    tasks.append(Task.query.filter_by(category='multiplication', difficulty='hard').order_by(db.func.random()).first())
    tasks.append(Task.query.filter_by(category='division', difficulty='hard').order_by(db.func.random()).first())
    
    # Формируем ответ
    tasks_data = [{
        'id': task.id,
        'text': task.text,
        'answer': task.answer,
        'category': task.category,
        'difficulty': task.difficulty
    } for task in tasks if task]
    
    return jsonify({'tasks': tasks_data})

@student.route('/submit-assessment', methods=['POST'])
def submit_assessment():
    data = request.get_json()
    answers = data.get('answers', [])
    
    score = 0
    for answer in answers:
        if str(answer['answer']) == str(answer['correct_answer']):
            score += 1
    
    return jsonify({'score': score, 'total': len(answers)})