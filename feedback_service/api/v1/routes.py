from flask import Blueprint, request, jsonify
from datetime import datetime, timezone, timedelta
from app_main.models import User
from ...service import notify_admins_about_feedback, notify_user_reply


from flask.views import MethodView
from flask_smorest import Blueprint
from feedback_service.models import Feedback
from feedback_service.db import db
from feedback_service.api.v1.schemas import FeedbackSchema


from flask import abort

import time


blp = Blueprint("feedback", "feedback", url_prefix="/api", description="Feedback operations")

@blp.route("/")
class FeedbackList(MethodView):

    @blp.response(200, FeedbackSchema(many=True))
    def get(self):
        return Feedback.query.order_by(Feedback.created_at.desc()).all()

    @blp.arguments(FeedbackSchema)
    @blp.response(201)
    def post(self, data):
        # Ограничение длины сообщения (для надёжности)
        if len(data.get('message', '').strip()) > 2000:
            return {"error": "Сообщение слишком длинное (максимум 2000 символов)"}, 400

        feedback = Feedback(
            user_id=None,
            last_name=data['last_name'],
            first_name=data['first_name'],
            middle_name=data.get('middle_name'),
            email=data['email'],
            message=data['message'],
            answer_method=data.get('answer_method'),
            created_at=datetime.now(timezone.utc),
            role_at_time=data.get('role_at_time')  # не обязательно
        )

        db.session.add(feedback)
        db.session.commit()

        return {
            "success": True,
            "message": "Ваше обращение отправлено!"
        }, 201




@blp.route("/<int:feedback_id>")
class FeedbackDetail(MethodView):

    @blp.response(200, FeedbackSchema)
    def get(self, feedback_id):
        """Получить обращение по ID"""
        return Feedback.query.get_or_404(feedback_id)

    @blp.arguments(FeedbackSchema(partial=True))
    @blp.response(200, FeedbackSchema)
    def patch(self, data, feedback_id):
        """Обновить обращение"""
        feedback = Feedback.query.get_or_404(feedback_id)
        for key, value in data.items():
            setattr(feedback, key, value)
        db.session.commit()
        return feedback



# # 1. Оставить обращение (отзыв)
# @api_feedback_bp.route('/', methods=['POST'])
# def create_feedback():
#     """
#     Любой пользователь (авторизованный или гость) может оставить обращение.
#     Оповещение всех админов на email.
#     """
#     now = time.time()
#     last_post = session.get('last_feedback_post')
#     if last_post and now - last_post < 60:
#         return jsonify({'error': 'Можно отправлять не чаще одного обращения в минуту'}), 429

#     try:
#         data = request.get_json()
#         required_fields = ['last_name', 'first_name', 'email', 'message']
#         if not all(data.get(field) for field in required_fields):
#             return jsonify({'error': 'Не все обязательные поля заполнены'}), 400

#         # Простейшая валидация email
#         email = data.get('email', '').strip()
#         if '@' not in email or '.' not in email.split('@')[-1]:
#             return jsonify({'error': 'Проверьте правильность email'}), 400

#         # Ограничение длины сообщения
#         if len(data.get('message', '')) > 2000:
#             return jsonify({'error': 'Сообщение слишком длинное (максимум 2000 символов)'}), 400

#         # Ошибка неавторизованного пользователя при выборе ответа "на платформе"
#         answer_method = data.get('answer_method')
#         if answer_method == "platform" and not current_user.is_authenticated:
#             return jsonify({
#                 "error": "AUTH_REQUIRED",
#                 "user_message": "Для получения ответа на платформе, пожалуйста, зарегистрируйтесь или войдите в свой аккаунт. Выберите 'на почту' или перейдите к регистрации.",
#             }), 403

#         # Если пользователь залогинен — берем его user_id и роль
#         user_id = current_user.id if current_user.is_authenticated else None
#         role_at_time = data.get('role_at_time')
#         if current_user.is_authenticated and not role_at_time:
#             role_at_time = getattr(current_user, 'role', 'user')

#         feedback = Feedback(
#             user_id=user_id,
#             last_name=data.get('last_name'),
#             first_name=data.get('first_name'),
#             middle_name=data.get('middle_name', ''),
#             role_at_time=role_at_time,
#             email=data.get('email'),
#             message=data.get('message'),
#             created_at=datetime.now(timezone.utc)
#         )
#         from app import db
#         from app.models import User  # Импортируем здесь, чтобы избежать циклических импортов
#         db.session.add(feedback)
#         db.session.commit()

#         session['last_feedback_post'] = now

#         # Оповещаем админов на почту
#         notify_admins_about_feedback(feedback, User)

#         return jsonify({'success': True, 'message': 'Ваше обращение отправлено!'}), 201

#     except Exception as e:
#         print("EXCEPTION:", e)
#         return jsonify({'error': 'INTERNAL_ERROR', 'user_message': 'Внутренняя ошибка сервера'}), 500


# # 2. Список моих обращений (активные)
# @api_feedback_bp.route('/my', methods=['GET'])
# @login_required
# def get_my_feedback():
#     """
#     Возвращает все активные (неархивные) обращения пользователя.
#     Если есть необработанные с ответом, помечаем их как прочитанные.
#     """
#     feedbacks = Feedback.query.filter_by(
#         user_id=current_user.id,
#         is_archived=False
#     ).order_by(Feedback.created_at.desc()).all()

#     results = [{
#         'id': fb.id,
#         'message': fb.message,
#         'created_at': fb.created_at.isoformat(),
#         'answer_text': fb.answer_text,
#         'answer_method': fb.answer_method,
#         'is_processed': fb.is_processed,
#         'answered_at': fb.answered_at.isoformat() if fb.answered_at else None,
#         'is_archived': fb.is_archived,
#         'is_read': fb.is_read
#     } for fb in feedbacks]
#     return jsonify({'results': results, 'count': len(results)}), 200

# # 3. Список всех обращений для админа (активные и архив)
# @api_feedback_bp.route('/admin', methods=['GET'])
# @login_required
# def get_feedback_admin():
#     """
#     Админ: получает список всех обращений (по умолчанию активные).
#     Добавить ?archived=true для просмотра архива.
#     """
#     if getattr(current_user, 'role', None) != 'admin':
#         return jsonify({'error': 'Доступ запрещен'}), 403

#     archived = request.args.get('archived', 'false').lower() == 'true'

#     # --- автоархивация: любые обращения с ответом старше 30 дней ---

#     now = datetime.now(timezone.utc)
#     threshold = now - timedelta(days=30)
#     to_archive = Feedback.query.filter(
#         Feedback.is_processed == True,
#         Feedback.is_archived == False,
#         Feedback.answered_at != None,
#         Feedback.answered_at < threshold
#     ).all()
#     for fb in to_archive:
#         fb.is_archived = True
#         fb.archived_at = now
#     if to_archive:
#         from app import db
#         db.session.commit()

#     # --- выдаём нужные отзывы ---
#     feedbacks = Feedback.query.filter_by(is_archived=archived).order_by(Feedback.created_at.desc()).all()
#     results = [{
#         'id': fb.id,
#         'last_name': fb.last_name,
#         'first_name': fb.first_name,
#         'middle_name': fb.middle_name,
#         'role_at_time': fb.role_at_time,
#         'email': fb.email,
#         'message': fb.message,
#         'created_at': fb.created_at.isoformat(),
#         'is_processed': fb.is_processed,
#         'answer_text': fb.answer_text,
#         'answer_method': fb.answer_method,
#         'answered_at': fb.answered_at.isoformat() if fb.answered_at else None,
#         'answered_by': fb.answered_by,
#         'is_archived': fb.is_archived,
#         'archived_at': fb.archived_at.isoformat() if fb.archived_at else None,
#     } for fb in feedbacks]
#     return jsonify({'results': results, 'count': len(results)}), 200

# # 4. Получить детали одного обращения (модалка/детальный просмотр)
# @api_feedback_bp.route('/<int:feedback_id>', methods=['GET'])
# @login_required
# def get_feedback_detail(feedback_id):
#     """
#     Детали обращения доступны админу или автору обращения.
#     При просмотре помечает обращение как прочитанное.
#     """
#     fb = Feedback.query.get_or_404(feedback_id)

#     user = User.query.get(feedback.user_id) if feedback.user_id else None
#     return jsonify({
#         'id': feedback.id,
#         'message': feedback.message,
#         'user_id': feedback.user_id,
#         'user_name': f"{user.last_name} {user.first_name}" if user else None,
#         'created_at': feedback.created_at.isoformat()
#     })
    
#     # Проверка доступа
#     is_admin = getattr(current_user, 'role', None) == 'admin'
#     is_author = fb.user_id == getattr(current_user, 'id', None)
#     if not (is_admin or is_author):
#         abort(403, description="Нет доступа к этому отзыву")
    
#     # Помечаем как прочитанное
#     if fb.is_processed and not fb.is_read and is_author:
#         fb.is_read = True
#         from app import db
#         db.session.commit()
    
#     return jsonify({
#         'id': fb.id,
#         'last_name': fb.last_name,
#         'first_name': fb.first_name,
#         'middle_name': fb.middle_name,
#         'role_at_time': fb.role_at_time,
#         'email': fb.email,
#         'message': fb.message,
#         'created_at': fb.created_at.isoformat(),
#         'is_processed': fb.is_processed,
#         'answer_text': fb.answer_text,
#         'answer_method': fb.answer_method,
#         'answered_at': fb.answered_at.isoformat() if fb.answered_at else None,
#         'answered_by': fb.answered_by,
#         'is_archived': fb.is_archived,
#         'archived_at': fb.archived_at.isoformat() if fb.archived_at else None,
#     }), 200


# # 5. Ответ на обращение
# @api_feedback_bp.route('/<int:feedback_id>/admin/reply', methods=['POST'])
# @login_required
# def reply_to_feedback(feedback_id):
#     """
#     Админ отправляет ответ (может выбрать: 'email' или 'platform').
#     Если выбран email — письмо отправляется, иначе только сохраняется в платформе.
#     """
#     # Проверяем права
#     if getattr(current_user, 'role', None) != 'admin':
#         return jsonify({'error': 'Доступ запрещен'}), 403

#     from app import db  # Импортим здесь, чтобы не было циклических ошибок
#     fb = Feedback.query.get_or_404(feedback_id)
#     data = request.get_json()
#     reply_text = data.get('reply_text')
#     answer_method = data.get('answer_method')  # 'email' или 'platform'

#     # Проверяем, что есть и текст, и способ ответа
#     if not reply_text or answer_method not in ('email', 'platform'):
#         return jsonify({'error': 'Требуются текст ответа и способ (email или platform)'}), 400

#     # Если ответить по email, проверяем корректность email
#     if answer_method == 'email':
#         if not fb.email:
#             return jsonify({'error': 'У этого обращения нет email для ответа'}), 400
#         email = fb.email.strip()
#         if '@' not in email or '.' not in email.split('@')[-1]:
#             return jsonify({'error': f'Неверный формат email: {email}'}), 400

#     try:
#         # Сохраняем ответ в БД
#         fb.answer_text = reply_text
#         fb.answer_method = answer_method
#         fb.answered_by = current_user.id
#         fb.answered_at = datetime.now(timezone.utc)
#         fb.is_processed = True
#         fb.processed_at = datetime.now(timezone.utc)

#         # Если выбран email — отправляем письмо
#         if answer_method == 'email':
#             subject = "Ответ на ваш отзыв"
#             email_body = f"""
#             <h3>Ответ на ваш отзыв</h3>
#             <p><strong>Администратор:</strong> Математическая платформа</p>
#             <p><strong>Ваше сообщение:</strong> {fb.message}</p>
#             <p><strong>Ответ:</strong></p>
#             <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px;">
#                 {reply_text}
#             </div>
#             """
#             # send_email — реализуй свою функцию! Если ещё нет — пока оставь pass
#             send_email(to=email, subject=subject, body=email_body)

#         db.session.commit()
#         return jsonify({'success': True, 'message': 'Ответ отправлен'}), 200

#     except Exception as e:
#         # Логируем ошибку (можно current_app.logger.error(...) если хочешь)
#         return jsonify({'error': f'Не удалось отправить ответ: "Внутренняя ошибка сервера"'}), 500




