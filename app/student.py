import random
from datetime import datetime, timezone
from flask import Blueprint, abort, flash, json, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from app.models import AssessmentResult, FinalAssessment, InitialAssessment, LearningProgress, StudentAnalysis, StudentProgress, Task, db

student_bp = Blueprint('student', __name__)

def get_random_task(category, difficulty):
    """Получает случайное задание по категории и сложности"""
    tasks = Task.query.filter_by(category=category, difficulty=difficulty).all()
    return random.choice(tasks) if tasks else None

@student_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('student_dashboard.html')

@student_bp.route('/learning')
@login_required
def learning():
    # Проверяем или создаем запись о прогрессе
    progress = StudentProgress.query.filter_by(student_id=current_user.id).first()
    if not progress:
        progress = StudentProgress(student_id=current_user.id)
        db.session.add(progress)
        db.session.commit()
    
    return render_template('student_learning.html', progress=progress)

@student_bp.route('/analytics')
@login_required
def analytics():
    # Получаем последний анализ для текущего ученика
    analysis = StudentAnalysis.query.filter_by(
        student_id=current_user.id
    ).order_by(StudentAnalysis.created_at.desc()).first()
    
    # Получаем входной и выходной контроль для вычисления процентов
    initial_assessment = InitialAssessment.query.filter_by(
        student_id=current_user.id
    ).order_by(InitialAssessment.completed_at.desc()).first()
    
    final_assessment = FinalAssessment.query.filter_by(
        student_id=current_user.id
    ).order_by(FinalAssessment.completed_at.desc()).first()
    
    # Вычисляем проценты
    initial_percentage = initial_assessment.percentage if initial_assessment else 0
    final_percentage = final_assessment.percentage if final_assessment else 0
    
    # Анализ по категориям
    categories_analysis = []
    if analysis and analysis.initial_assessment_data and analysis.final_assessment_data:
        initial_data = json.loads(analysis.initial_assessment_data) if isinstance(analysis.initial_assessment_data, str) else analysis.initial_assessment_data
        final_data = json.loads(analysis.final_assessment_data) if isinstance(analysis.final_assessment_data, str) else analysis.final_assessment_data
        
        categories = {
            'addition': 'Сложение',
            'subtraction': 'Вычитание',
            'multiplication': 'Умножение',
            'division': 'Деление'
        }
        
        for category, name in categories.items():
            initial_cat = [t for t in initial_data if t['category'] == category]
            final_cat = [t for t in final_data if t['category'] == category]
            
            if initial_cat and final_cat:
                init_score = sum(t['score'] for t in initial_cat) / len(initial_cat) * 100
                final_score = sum(t['score'] for t in final_cat) / len(final_cat) * 100
                progress = final_score - init_score
                
                # Простой анализ по категориям
                if progress > 20:
                    cat_analysis = "Отличный прогресс!"
                elif progress > 0:
                    cat_analysis = "Небольшое улучшение"
                elif progress == 0:
                    cat_analysis = "Без изменений"
                else:
                    cat_analysis = "Требуется повторение темы"
                
                categories_analysis.append({
                    'name': name,
                    'initial_score': init_score,
                    'final_score': final_score,
                    'progress': progress,
                    'analysis': cat_analysis
                })
    
    return render_template('student_analytics.html', 
                         analysis=analysis,
                         initial_percentage=initial_percentage,
                         final_percentage=final_percentage,
                         categories_analysis=categories_analysis)

@student_bp.route('/chat')
@login_required
def chat():
    return render_template('student_chat.html')

@student_bp.route('/settings')
@login_required
def settings():
    return render_template('student_settings.html')

@student_bp.route('/assessment', methods=['GET', 'POST'])
@login_required
def assessment():
    if request.method == 'POST':
        # Обработка отправки формы
        tasks_data = []
        score = 0
        total = 12
        
        # Сохраняем порядок задач для последующего анализа
        task_order = request.form.getlist('task_order[]')
        
        for i, task_id in enumerate(task_order, start=1):
            user_answer = request.form.get(f'answer-{task_id}')
            task = Task.query.get(task_id)
            
            is_correct = task and user_answer.strip() == task.answer.strip()
            task_score = 1 if is_correct else 0
            score += task_score
            
            tasks_data.append({
                'task_number': i,
                'task_id': task_id,
                'text': task.text,
                'user_answer': user_answer,
                'correct_answer': task.answer,
                'score': task_score,
                'category': task.category,
                'difficulty': task.difficulty
            })
        
        # Создаем запись о тестировании
        assessment = InitialAssessment(
            student_id=current_user.id,
            tasks_data=tasks_data,
            score=score,
            total=total,
            percentage=(score/total)*100
        )
        db.session.add(assessment)
        
        # Обновляем прогресс студента
        progress = StudentProgress.query.filter_by(student_id=current_user.id).first()
        if progress:
            progress.initial_test_completed = True
            progress.last_updated = datetime.now(timezone.utc)
        
        db.session.commit()
        
        flash(f'Тестирование завершено! Ваш результат: {score} из {total}', 'success')
        return redirect(url_for('student.assessment_result', result_id=assessment.id))
    
    # GET запрос - отображение формы
    tasks = []
    # Сначала все простые задания
    tasks.append(get_random_task('addition', 'easy'))
    tasks.append(get_random_task('subtraction', 'easy'))
    tasks.append(get_random_task('multiplication', 'easy'))
    tasks.append(get_random_task('division', 'easy'))
    
    # Затем все средние задания
    tasks.append(get_random_task('addition', 'medium'))
    tasks.append(get_random_task('subtraction', 'medium'))
    tasks.append(get_random_task('multiplication', 'medium'))
    tasks.append(get_random_task('division', 'medium'))
    
    # Затем все сложные задания
    tasks.append(get_random_task('addition', 'hard'))
    tasks.append(get_random_task('subtraction', 'hard'))
    tasks.append(get_random_task('multiplication', 'hard'))
    tasks.append(get_random_task('division', 'hard'))
    
    # Проверяем, что все задания получены
    if None in tasks:
        flash('Не удалось загрузить все задания для тестирования', 'danger')
        return redirect(url_for('student.dashboard'))
    
    # Сохраняем порядок задач для последующего анализа
    task_order = [str(task.id) for task in tasks]
    
    return render_template('student_assessment.html', tasks=tasks, task_order=task_order)

@student_bp.route('/assessment_result/<int:result_id>')
@login_required
def assessment_result(result_id):
    # Сначала проверяем FinalAssessment, так как это более поздние результаты
    result = FinalAssessment.query.get(result_id)
    if not result:
        # Если не найден в FinalAssessment, ищем в InitialAssessment
        result = InitialAssessment.query.get(result_id)
    
    if not result:
        abort(404)
    if result.student_id != current_user.id:
        abort(403)
    
    # Преобразуем JSON строку в список словарей
    tasks_data = json.loads(result.tasks_data) if isinstance(result.tasks_data, str) else result.tasks_data
    
    return render_template('assessment_result.html', 
                         result=result,
                         tasks_data=tasks_data)

@student_bp.route('/learning-materials')
@login_required
def learning_materials():
    progress = StudentProgress.query.filter_by(student_id=current_user.id).first()
    if not progress:
        flash('Сначала необходимо пройти входной контроль знаний', 'warning')
        return redirect(url_for('student.learning'))
    
    if not progress.initial_test_completed:
        flash('Сначала необходимо пройти входной контроль знаний', 'warning')
        return redirect(url_for('student.learning'))
    
    return render_template('learning_materials.html', progress=progress)  # Добавили progress в контекст

@student_bp.route('/learning-page/<int:page_id>')
@login_required
def learning_page(page_id):
    progress = StudentProgress.query.filter_by(student_id=current_user.id).first()
    if not progress or not progress.initial_test_completed:
        flash('Сначала необходимо пройти входной контроль знаний', 'warning')
        return redirect(url_for('student.learning'))
    
    template_name = f"page_{page_id}.html"
    return render_template(template_name, progress=progress)  # Добавили progress

@student_bp.route('/complete-learning', methods=['POST'])
@login_required
def complete_learning():
    progress = StudentProgress.query.filter_by(student_id=current_user.id).first()
    if progress and not progress.learning_completed:
        progress.learning_completed = True
        db.session.commit()
        flash('Этап изучения материалов завершен! Теперь вы можете пройти выходной контроль.', 'success')
    return redirect(url_for('student.learning'))

@student_bp.route('/final-assessment', methods=['GET', 'POST'])
@login_required
def final_assessment():
    progress = StudentProgress.query.filter_by(student_id=current_user.id).first()
    if not progress or not progress.learning_completed:
        flash('Сначала необходимо изучить материалы', 'warning')
        return redirect(url_for('student.learning'))

    if request.method == 'POST':
        # Обработка отправки формы выходного контроля
        tasks_data = []
        score = 0
        total = 12
        
        # Сохраняем порядок задач для последующего анализа
        task_order = request.form.getlist('task_order[]')
        
        for i, task_id in enumerate(task_order, start=1):
            user_answer = request.form.get(f'answer-{task_id}')
            task = Task.query.get(task_id)
            
            is_correct = task and user_answer.strip() == task.answer.strip()
            task_score = 1 if is_correct else 0
            score += task_score
            
            tasks_data.append({
                'task_number': i,
                'task_id': task_id,
                'text': task.text,
                'user_answer': user_answer,
                'correct_answer': task.answer,
                'score': task_score,
                'category': task.category,
                'difficulty': task.difficulty
            })
        
        # Создаем запись о выходном контроле
        assessment = FinalAssessment(
            student_id=current_user.id,
            tasks_data=json.dumps(tasks_data),
            score=score,
            total=total,
            percentage=(score/total)*100
        )
        db.session.add(assessment)
        
        # Обновляем прогресс
        progress.final_test_completed = True
        db.session.commit()
        
        # Генерируем анализ результатов
        initial_assessment = InitialAssessment.query.filter_by(
            student_id=current_user.id
        ).order_by(InitialAssessment.completed_at.desc()).first()
        
        initial_data = initial_assessment.tasks_data if initial_assessment else None
        if initial_data and isinstance(initial_data, str):
            initial_data = json.loads(initial_data)

        analysis = StudentAnalysis(
            student_id=current_user.id,
            initial_assessment_data=json.dumps(initial_data) if initial_data else None,
            learning_completed=True,
            final_assessment_data=json.dumps(tasks_data),
            percentage_difference=assessment.percentage - (initial_assessment.percentage if initial_assessment else 0)
        )
        analysis.generate_analysis()  # Генерируем анализ
        db.session.add(analysis)
        db.session.commit()
        
        flash(f'Выходной контроль завершен! Ваш результат: {score} из {total}', 'success')
        return redirect(url_for('student.assessment_result', result_id=assessment.id))
    
    # GET запрос - отображение формы
    tasks = []
    # Легкий уровень (в том же порядке, что и во входном контроле)
    tasks.append(get_random_task('addition', 'easy'))
    tasks.append(get_random_task('subtraction', 'easy'))
    tasks.append(get_random_task('multiplication', 'easy'))
    tasks.append(get_random_task('division', 'easy'))
    
    # Средний уровень
    tasks.append(get_random_task('addition', 'medium'))
    tasks.append(get_random_task('subtraction', 'medium'))
    tasks.append(get_random_task('multiplication', 'medium'))
    tasks.append(get_random_task('division', 'medium'))
    
    # Сложный уровень
    tasks.append(get_random_task('addition', 'hard'))
    tasks.append(get_random_task('subtraction', 'hard'))
    tasks.append(get_random_task('multiplication', 'hard'))
    tasks.append(get_random_task('division', 'hard'))
    
    # Проверяем, что все задания получены
    if None in tasks:
        flash('Не удалось загрузить все задания для тестирования', 'danger')
        return redirect(url_for('student.learning'))
    
    # Сохраняем порядок задач для последующего анализа
    task_order = [str(task.id) for task in tasks]
    
    return render_template('final_assessment.html', tasks=tasks, task_order=task_order)

@student_bp.route('/initial-assessment-details')
@login_required
def initial_assessment_details():
    # Получаем последний входной контроль
    assessment = InitialAssessment.query.filter_by(
        student_id=current_user.id
    ).order_by(InitialAssessment.completed_at.desc()).first_or_404()
    
    tasks_data = json.loads(assessment.tasks_data) if isinstance(assessment.tasks_data, str) else assessment.tasks_data
    return render_template('assessment_result.html', 
                         result=assessment,
                         tasks_data=tasks_data)

@student_bp.route('/final-assessment-details')
@login_required
def final_assessment_details():
    # Получаем последний выходной контроль
    assessment = FinalAssessment.query.filter_by(
        student_id=current_user.id
    ).order_by(FinalAssessment.completed_at.desc()).first_or_404()
    
    tasks_data = json.loads(assessment.tasks_data) if isinstance(assessment.tasks_data, str) else assessment.tasks_data
    return render_template('assessment_result.html', 
                         result=assessment,
                         tasks_data=tasks_data)