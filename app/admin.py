from flask import Blueprint, current_app, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models import Feedback, User, Class, db
from app.utils import send_email

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'admin':
        flash('Доступ запрещен', 'danger')
        return redirect(url_for('auth.login'))
    
    users = User.query.all()
    classes = Class.query.all()
    feedback_list = Feedback.query.order_by(Feedback.created_at.desc()).all()
    
    return render_template('admin_dashboard.html',
                        name=f"{current_user.first_name} {current_user.middle_name}",
                        users=users,
                        classes=classes,
                        feedback_list=feedback_list)

@admin_bp.route('/users/<int:user_id>/update_role', methods=['POST'])
@login_required
def update_user_role(user_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Доступ запрещен'}), 403
    
    user = User.query.get_or_404(user_id)
    new_role = request.form.get('role')
    
    if new_role not in ['teacher', 'student', 'admin', 'expert']:
        return jsonify({'error': 'Некорректная роль'}), 400
    
    user.role = new_role
    db.session.commit()
    
    return jsonify({'success': True, 'new_role': new_role})

@admin_bp.route('/classes/<int:class_id>')
@login_required
def class_details(class_id):
    if current_user.role != 'admin':
        flash('Доступ запрещен', 'danger')
        return redirect(url_for('auth.login'))
    
    class_ = Class.query.get_or_404(class_id)
    return render_template('admin_class_details.html',
                         class_=class_,
                         students=class_.students)

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Доступ запрещен'}), 403
    
    user = User.query.get_or_404(user_id)
    
    # Предотвращаем удаление самого себя
    if user.id == current_user.id:
        return jsonify({'error': 'Нельзя удалить самого себя'}), 400
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'success': True})

@admin_bp.route('/feedback')    # Обратная связь
@login_required
def view_feedback():
    if current_user.role != 'admin':
        flash('Доступ запрещен', 'danger')
        return redirect(url_for('auth.login'))
    
    feedback_list = Feedback.query.order_by(Feedback.created_at.desc()).all()
    return render_template('admin_feedback.html', feedback_list=feedback_list)

@admin_bp.route('/feedback/<int:feedback_id>/reply', methods=['POST'])
@login_required
def reply_to_feedback(feedback_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Доступ запрещен'}), 403
    
    feedback = Feedback.query.get_or_404(feedback_id)
    message = request.form.get('reply_message', '').strip()
    
    # Проверка email
    if not feedback.email:
        return jsonify({'error': 'У этого отзыва нет email для ответа'}), 400
    
    # Нормализация email
    email = feedback.email.strip()
    if '@' not in email or '.' not in email.split('@')[-1]:
        return jsonify({'error': f'Неверный формат email: {email}'}), 400
    
    try:
        # Подготавливаем email
        subject = "Ответ на ваш отзыв"
        email_body = f"""
        <h3>Ответ на ваш отзыв</h3>
        <p><strong>Администратор:</strong> Математическая платформа</p>
        <p><strong>Ваше сообщение:</strong> {feedback.message}</p>
        <p><strong>Ответ:</strong></p>
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px;">
            {message}
        </div>
        """
        
        # Логирование перед отправкой
        current_app.logger.info(f"Attempting to send email to: {email}")
        
        # Отправляем email
        if not send_email(
            to=email,
            subject=subject,
            body=email_body
        ):
            return jsonify({'error': 'Не удалось отправить письмо (функция вернула False)'}), 500
        
        # Помечаем как обработанное
        feedback.is_processed = True
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        current_app.logger.error(f"Ошибка отправки письма: {str(e)}")
        return jsonify({'error': f'Не удалось отправить письмо: {str(e)}'}), 500