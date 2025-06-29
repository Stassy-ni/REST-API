# app/api/feedback/service.py
# from app.utils import send_email

def notify_admins_about_feedback(feedback, UserModel):
    """
    Отправляет письмо всем администраторам о новом отзыве.
    """
    admin_emails = [user.email for user in UserModel.query.filter_by(role='admin').all() if user.email]
    for email in admin_emails:
        try:
            send_email(
                email,
                'Новое сообщение обратной связи',
                f"""<h3>Новое сообщение от {feedback.first_name} {feedback.last_name}</h3>
                <p>Email: {feedback.email}</p>
                <p>Сообщение: {feedback.message}</p>"""
            )
        except Exception as mail_error:
            print(f"[WARN] Не удалось отправить email администратору {email}: {mail_error}")

def notify_user_reply(feedback):
    """
    Отправляет ответ пользователю, если выбран способ 'email'.
    """
    try:
        subject = "Ответ на ваш отзыв"
        email_body = f"""
        <h3>Ответ на ваш отзыв</h3>
        <p><strong>Администратор:</strong> Математическая платформа</p>
        <p><strong>Ваше сообщение:</strong> {feedback.message}</p>
        <p><strong>Ответ:</strong></p>
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px;">
            {feedback.answer_text}
        </div>
        """
        send_email(to=feedback.email, subject=subject, body=email_body)
    except Exception as mail_error:
        print(f"[WARN] Не удалось отправить email пользователю {feedback.email}: {mail_error}")
