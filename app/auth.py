from flask import Blueprint, jsonify, request, flash, redirect, session, url_for, render_template
from datetime import datetime
from flask_login import login_user, logout_user, login_required
from app.models import Feedback, Student, User
from app import db, login_manager, Config
from app.utils import send_email, send_confirmation_code
from werkzeug.security import generate_password_hash 

auth_bp = Blueprint('auth', __name__)

@login_manager.user_loader
def load_user(user_id):
    if user_id.startswith('user-'):
        return User.query.get(int(user_id.replace('user-', '')))
    elif user_id.startswith('student-'):
        return Student.query.get(int(user_id.replace('student-', '')))
    return None

@auth_bp.route('/')
def index():
    return render_template('index.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # 1. Сначала проверяем учителей/админов (User)
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        # 2. Если не нашли, проверяем учеников (Student)
        if not user:
            user = Student.query.filter_by(username=username).first()
            if user:
                # Явно указываем роль для ученика
                user.role = 'student'
        
        if user and user.check_password(password):
            login_user(user)
            
            # Для учеников сразу редирект в кабинет
            if hasattr(user, 'role'):
                if user.role == 'teacher':
                    return redirect(url_for('teacher.dashboard'))
                elif user.role == 'expert':
                    return redirect(url_for('expert.dashboard'))
                elif user.role == 'admin':
                    return redirect(url_for('admin.dashboard'))
            
            # Все остальные (ученики) - в student.dashboard
            return redirect(url_for('student.dashboard'))
        
        flash('Неверные учетные данные', 'danger')
    
    return render_template('index.html')

@auth_bp.route('/request-code', methods=['GET', 'POST'])
def request_code():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            send_login_code(user)
            flash('Код отправлен на вашу почту', 'info')
            return redirect(url_for('auth.verify_code', email=email))
        flash('Пользователь с такой почтой не найден', 'danger')
    
    return render_template('request_code.html')


@auth_bp.route('/verify-code', methods=['GET', 'POST'])
def verify_code():
    email = request.args.get('email')
    user = User.query.filter_by(email=email).first_or_404()

    if request.method == 'POST':
        input_code = request.form.get('code')
        now = datetime.utcnow()
        if (
            user.email_code == input_code and
            (now - user.email_code_created_at).seconds < 300
        ):
            login_user(user)
            user.email_code = None
            user.email_code_created_at = None
            db.session.commit()
            flash('Успешный вход', 'success')
            return redirect(url_for(f"{user.role}.dashboard"))
        else:
            flash('Неверный или просроченный код', 'danger')

    return render_template('verify_code.html', email=email)

@auth_bp.route('/confirm-email', methods=['GET', 'POST'])
def confirm_email():
    # return 'We are here'
    email = request.args.get('email')
    user = User.query.filter_by(email=email).first_or_404()

    if request.method == 'POST':
        code = request.form.get('code')
        now = datetime.utcnow()
        if (
            user.email_code == code and
            (now - user.email_code_created_at).seconds < 300
        ):
            user.email_confirmed = True
            user.email_code = None
            user.email_code_created_at = None
            db.session.commit()

            login_user(user)
            flash('Почта подтверждена, вы вошли в систему!', 'success')
            return redirect(url_for(f"{user.role}.dashboard"))

        else:
            flash('Неверный или просроченный код', 'danger')

    return render_template('confirm_email.html', email=email)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']

        # Проверяем, совпадают ли пароли
        if request.form['password'] != request.form['confirm']:
            flash('Пароли не совпадают!', 'danger')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(email=email).first():
            flash('Пользователь с такой почтой уже существует', 'danger')
            return redirect(url_for('auth.register'))
            
        user = User(
            last_name=request.form['last_name'],
            first_name=request.form['first_name'],
            middle_name=request.form.get('middle_name', ''),
            email=email,
            role=request.form['role'],
            institution=request.form.get('institution', ''),
            email_confirmed = True
            
        )
        user.set_password(request.form['password'])
        
        db.session.add(user)
        db.session.commit()
        
        send_confirmation_code(user)
        flash('На почту отправлен код подтверждения. Введите его, чтобы завершить регистрацию.', 'info')
        return redirect(url_for('auth.confirm_email', email=user.email))
    
    return render_template('registration_form.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы успешно вышли', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/contact')    # Отправка письма обратной связи
def contact():
    return redirect(url_for('auth.feedback'))

@auth_bp.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        # Логика отправки письма
        try:
            feedback = Feedback(
                last_name=request.form.get('last_name'),
                first_name=request.form.get('first_name'),
                middle_name=request.form.get('middle_name', ''),  # Добавляем значение по умолчанию
                email=request.form.get('email'),
                message=request.form.get('message')
            )
            db.session.add(feedback)
            db.session.commit()
            
            admin_emails = [user.email for user in User.query.filter_by(role='admin').all()]
            for email in admin_emails:
                send_email(
                    email,
                    'Новое сообщение обратной связи',
                    f"""<h3>Новое сообщение от {feedback.first_name} {feedback.last_name}</h3>
                    <p>Email: {feedback.email}</p>
                    <p>Сообщение: {feedback.message}</p>"""
                )
            
            flash('Сообщение отправлено!', 'success')
            return redirect(url_for('auth.feedback'))
            
        except Exception as e:
            flash(f'Ошибка: {str(e)}', 'danger')
    
    # Для GET запроса просто рендерим шаблон
    return render_template('feedback.html')

@auth_bp.route('/test-mail')
def test_mail():
    success = send_email(
        to="dinaraakberova4493@gmail.com",  # Замените на реальный email
        subject="Тест отправки письма",
        body="<h1>Проверка работы Flask-Mail!</h1><p>Если вы видите это письмо, отправка работает корректно.</p>"
    )
    if success:
        return "Письмо отправлено! Проверьте почту (включая папку 'Спам')."
    else:
        return "Ошибка отправки. Проверьте логи сервера."
    
@auth_bp.route('/mail-config')
def mail_config():
    from flask import current_app, jsonify
    return jsonify({
        'MAIL_SERVER': current_app.config['MAIL_SERVER'],
        'MAIL_PORT': current_app.config['MAIL_PORT'],
        'MAIL_USERNAME': current_app.config['MAIL_USERNAME'],
        'MAIL_USE_TLS': current_app.config['MAIL_USE_TLS'],
        'MAIL_USE_SSL': current_app.config['MAIL_USE_SSL']
    })