from flask import Blueprint, current_app, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app_main.models import User, Class, db
from app_main.utils import send_email

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'admin':
        flash('Доступ запрещен', 'danger')
        return redirect(url_for('auth.login'))
    
    users = User.query.all()
    classes = Class.query.all()
    # feedback_list = Feedback.query.order_by(Feedback.created_at.desc()).all()
    
    return render_template('admin_dashboard.html',
                         name=f"{current_user.first_name} {current_user.middle_name}",
                         users=users,
                         classes=classes)
                        #  feedback_list=feedback_list)

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
