#import secrets
from datetime import datetime
import random
import string
from flask import Blueprint, abort, json, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from app.models import FinalAssessment, InitialAssessment, StudentAnalysis, StudentProgress, Class, Student, db
#from app.utils import send_email

teacher_bp = Blueprint('teacher', __name__)

def generate_username(fio):
    """Генерация логина из ФИО"""
    parts = fio.split()
    base = (parts[0] + parts[1][0]).lower()
    return base + str(random.randint(100, 999))

def generate_random_password(length=10):
    """Генерация случайного пароля"""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

@teacher_bp.route('/teacher/dashboard')
@login_required
def dashboard():
    if current_user.role != 'teacher':
        flash('Доступ запрещен', 'danger')
        return redirect(url_for('auth.login'))
    
    classes = Class.query.filter_by(teacher_id=current_user.id).all()
    return render_template('teacher_dashboard.html',
                        name=f"{current_user.first_name} {current_user.middle_name}",
                        classes=classes)

@teacher_bp.route('/teacher/create_class', methods=['POST'])
@login_required
def create_class():
    try:
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400
            
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Отсутствуют данные'}), 400

        grade = data.get('grade')
        letter = data.get('letter', '').upper()[:1]

        if not grade or not grade.isdigit() or int(grade) < 5 or int(grade) > 11:
            return jsonify({'error': 'Некорректный номер класса (должен быть от 5 до 11)'}), 400

        # Проверяем существование такого класса у этого учителя
        existing = Class.query.filter_by(
            grade=int(grade),
            letter=letter,
            teacher_id=current_user.id
        ).first()
        if existing:
            return jsonify({'error': 'Такой класс уже существует'}), 409

        # Создаем новый класс
        new_class = Class(
            grade=int(grade),
            letter=letter,
            teacher_id=current_user.id
        )
        db.session.add(new_class)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'class_id': new_class.id,
            'message': f'Класс {grade}{letter} успешно создан'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': f'Ошибка сервера: {str(e)}'
        }), 500

@teacher_bp.route('/teacher/add_students', methods=['POST'])
@login_required
def add_students():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Отсутствуют данные'}), 400

        class_id = data.get('class_id')
        students_data = data.get('students', [])

        if not class_id or not students_data:
            return jsonify({'error': 'Некорректные данные'}), 400

        # Проверяем существование класса и права доступа
        class_ = Class.query.get(class_id)
        if not class_ or class_.teacher_id != current_user.id:
            return jsonify({'error': 'Класс не найден или нет прав доступа'}), 403

        new_students = []
        for student_data in students_data:
            fio_parts = student_data['fio'].split()
            if len(fio_parts) < 2:
                continue  # Пропускаем некорректные ФИО

            # Генерация учетных данных
            username = student_data.get('login') or generate_username(student_data['fio'])
            password = student_data.get('password') or generate_random_password()

            student = Student(
                last_name=fio_parts[0],
                first_name=fio_parts[1],
                middle_name=fio_parts[2] if len(fio_parts) > 2 else None,
                username=username,
                password_hash=generate_password_hash(password),
                grade=class_.grade,
                letter=class_.letter,
                class_id=class_id,
                user_id=current_user.id,
                plain_password=password  # Сохраняем пароль в открытом виде для отображения
            )
            db.session.add(student)
            new_students.append({
                'fio': student_data['fio'],
                'login': username,
                'password': password
            })

        db.session.commit()
        return jsonify({
            'status': 'success',
            'count': len(new_students),
            'students': new_students,
            'message': f'Успешно добавлено {len(new_students)} учеников'
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

#@teacher_bp.route('/users')
#@login_required
#def users():
#    userlist = User.query.all()
#    return render_template('users.html', userlist=userlist)

#@teacher_bp.route('/users/<int:id>/delete')
#@login_required
#def delete_user(id):
#    user = User.query.get_or_404(id)
#    if user is None:
#        flash('Такого пользователя не существует', 'warning')
#        return redirect(url_for('teacher.users'))
#    db.session.delete(user)
#    db.session.commit()
#    flash('Пользователь успешно удален', 'success')
#    return redirect(url_for('teacher.users'))
@teacher_bp.route('/classes')
@login_required
def classes():
    if current_user.role != 'teacher':
        flash('Доступ запрещен', 'danger')
        return redirect(url_for('auth.login'))

    classes = Class.query.filter_by(teacher_id=current_user.id).all()
    total_students = sum(len(class_.students) for class_ in classes)  # Добавляем подсчет учеников
    
    return render_template('teacher_classes.html', 
                         classes=classes,
                         total_students=total_students)

@teacher_bp.route('/class/<int:class_id>')
@login_required
def view_class(class_id):
    class_ = Class.query.get_or_404(class_id)

    if class_.teacher_id != current_user.id:
        flash('Нет доступа к этому классу', 'danger')
        return redirect(url_for('teacher.classes'))

    students = Student.query.filter_by(class_id=class_id).all()
    return render_template('teacher_view_class.html', class_=class_, students=students)

@teacher_bp.route('/class/<int:class_id>/add_student', methods=['POST'])
@login_required
def add_student(class_id):
    class_ = Class.query.get_or_404(class_id)
    if class_.teacher_id != current_user.id:
        flash('Нет доступа к этому классу', 'danger')
        return redirect(url_for('teacher.classes'))

    last_name = request.form.get('last_name')
    first_name = request.form.get('first_name')
    middle_name = request.form.get('middle_name')

    if not last_name or not first_name:
        flash('Фамилия и имя обязательны', 'danger')
        return redirect(url_for('teacher.view_class', class_id=class_id))

    # Генерация учетных данных
    username = generate_username(f"{last_name} {first_name}")
    password = generate_random_password()
    
    # Создаем студента
    student = Student(
        last_name=last_name,
        first_name=first_name,
        middle_name=middle_name,
        username=username,
        password_hash=generate_password_hash(password),
        grade=class_.grade,
        letter=class_.letter,
        class_id=class_id,
        user_id=current_user.id
    )
    
    # Добавляем студента в сессию
    db.session.add(student)
    
    # Фиксируем изменения, чтобы получить ID студента
    db.session.flush()
    
    # Создаем запись о прогрессе для нового ученика
    progress = StudentProgress(
        student_id=student.id,
        initial_test_completed=False,
        learning_completed=False,
        final_test_completed=False,
        last_updated=datetime.utcnow()
    )
    db.session.add(progress)
    
    # Устанавливаем plain_password после создания объекта
    student.plain_password = password
    
    # Фиксируем все изменения
    db.session.commit()
    
    flash(f'Ученик {last_name} {first_name} добавлен. Логин: {username}, Пароль: {password}', 'success')
    return redirect(url_for('teacher.view_class', class_id=class_id))

@teacher_bp.route('/class/<int:class_id>/update', methods=['POST'])
@login_required
def update_class(class_id):
    class_ = Class.query.get_or_404(class_id)
    
    if class_.teacher_id != current_user.id:
        flash('Нет доступа к этому классу', 'danger')
        return redirect(url_for('teacher.classes'))

    grade = request.form.get('grade')
    letter = request.form.get('letter', '').upper()[:1]

    if not grade or not grade.isdigit() or int(grade) < 5 or int(grade) > 11:
        flash('Некорректный номер класса (должен быть от 5 до 11)', 'danger')
        return redirect(url_for('teacher.view_class', class_id=class_id))

    class_.grade = int(grade)
    class_.letter = letter
    db.session.commit()

    flash('Класс успешно обновлен', 'success')
    return redirect(url_for('teacher.view_class', class_id=class_id))

# ТЕСТОВЫЕ УЧЕНИКИ
#@teacher_bp.route('/debug_fill_class/<int:class_id>')
#def debug_fill_class(class_id):
#    from app.models import Student, db
#    import random

#    first_names = ['Иван', 'Анна', 'Мария', 'Дмитрий', 'Сергей']
#    last_names = ['Иванов', 'Петрова', 'Сидоров', 'Кузнецова', 'Смирнов']
#    domains = ['yopmail.com', 'test.ru', 'example.com']

#    for i in range(5):
#        s = Student(
#            first_name=random.choice(first_names),
#            last_name=random.choice(last_names),
#            middle_name='Тестович',
#            email=f'testuser{i}@{random.choice(domains)}',
#            class_id=class_id,
#            status='active',
#            invitation_token='debug-token',
#            progress_completed=random.randint(0, 7),
#            progress_total=7,
#            last_active='Сегодня'
#        )
#        db.session.add(s) 
#    db.session.commit()
#    return f'Добавлено 5 учеников в класс {class_id}'

@teacher_bp.route('/results')
@login_required
def results():
    if current_user.role != 'teacher':
        flash('Доступ запрещен', 'danger')
        return redirect(url_for('auth.login'))

    # Получаем всех учеников всех классов учителя
    classes = Class.query.filter_by(teacher_id=current_user.id).all()
    students = []
    for class_ in classes:
        students.extend(class_.students)
    
    return render_template('teacher_results.html', students=students)

@teacher_bp.route('/student/<int:student_id>/results')
@login_required
def student_results(student_id):
    if current_user.role != 'teacher':
        flash('Доступ запрещен', 'danger')
        return redirect(url_for('auth.login'))

    student = Student.query.get_or_404(student_id)
    # Проверяем, что ученик принадлежит классу учителя
    class_ = Class.query.get(student.class_id)
    if not class_ or class_.teacher_id != current_user.id:
        abort(403)

    # Получаем последний анализ для ученика
    analysis = StudentAnalysis.query.filter_by(
        student_id=student_id
    ).order_by(StudentAnalysis.created_at.desc()).first()
    
    # Получаем входной и выходной контроль для вычисления процентов
    initial_assessment = InitialAssessment.query.filter_by(
        student_id=student_id
    ).order_by(InitialAssessment.completed_at.desc()).first()
    
    final_assessment = FinalAssessment.query.filter_by(
        student_id=student_id
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
    
    return render_template('teacher_student_results.html', 
                         student=student,
                         analysis=analysis,
                         initial_percentage=initial_percentage,
                         final_percentage=final_percentage,
                         categories_analysis=categories_analysis)