from datetime import datetime, timezone
from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from app.models import Task, db

expert_bp = Blueprint('expert', __name__)

@expert_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('expert_dashboard.html')

@expert_bp.route('/create-task')
@login_required
def create_task():
    return render_template('expert_create_task.html')

@expert_bp.route('/task-library')
@login_required
def task_library():
    tasks = Task.query.filter_by(author_id=current_user.id)\
                    .order_by(Task.created_at.desc())\
                    .all()
    
    # Добавим отладочный вывод
    print(f"Найдено заданий для пользователя {current_user.id}: {len(tasks)}")
    for task in tasks:
        print(f"Задание {task.id}: {task.text[:50]}...")
    
    return render_template('expert_task_library.html', 
                         tasks=tasks,
                         current_time=datetime.now(timezone.utc))  # Для отладки

@expert_bp.route('/save-task', methods=['POST'])
@login_required
def save_task():
    try:
        # Проверяем, что данные пришли в JSON формате
        if not request.is_json:
            return jsonify({
                'success': False,
                'message': 'Неверный формат данных. Ожидается JSON'
            }), 400

        data = request.get_json()
        
        # Проверяем обязательные поля
        required_fields = ['category', 'difficulty', 'text', 'answer']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'success': False,
                    'message': f'Не указано обязательное поле: {field}'
                }), 400
        
        # Создаем новое задание
        new_task = Task(
            category=data['category'],
            difficulty=data['difficulty'],
            text=data['text'],
            answer=data['answer'],
            author_id=current_user.id
        )
        
        db.session.add(new_task)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Задача успешно сохранена',
            'task_id': new_task.id,
            'created_at': new_task.created_at.strftime('%d.%m.%Y %H:%M')
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Ошибка сохранения: {str(e)}'
        }), 500
    
@expert_bp.route('/delete-task/<int:task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    try:
        task = Task.query.get_or_404(task_id)
        
        # Проверяем, что текущий пользователь - автор задачи
        if task.author_id != current_user.id:
            return jsonify({
                'success': False,
                'message': 'Вы не можете удалить чужую задачу'
            }), 403
            
        db.session.delete(task)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Задача успешно удалена'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Ошибка при удалении: {str(e)}'
        }), 500
    