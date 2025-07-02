from flask import current_app
from flask_mail import Message
from app import mail, db
from datetime import datetime
import random

def send_email(to, subject, body):
    try:
        # Проверка и нормализация email
        if not to or not isinstance(to, str):
            raise ValueError("Email должен быть строкой")
        
        to = to.strip().lower()  # Удаляем пробелы и приводим к нижнему регистру
        if '@' not in to:
            raise ValueError(f"Неверный формат email: {to}")

        # Разделяем email на локальную часть и домен
        local_part, domain = to.split('@', 1)
        
        # Проверяем домен на корректность
        if not domain or '.' not in domain:
            raise ValueError(f"Неверный домен в email: {domain}")

        msg = Message(
            subject=subject,
            recipients=[to],  # Используем нормализованный email
            html=body,
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        mail.send(msg)
        current_app.logger.info(f"Email успешно отправлен на {to}")
        return True
    except Exception as e:
        current_app.logger.error(f"Ошибка при отправке письма на {to}: {str(e)}", exc_info=True)
        return False
    
def send_confirmation_code(user):
    code = str(random.randint(100000, 999999))
    user.email_code = code
    user.email_code_created_at = datetime.utcnow()
    db.session.commit()

    html = f"""
        <h3>Подтверждение регистрации</h3>
        <p>Введите этот код на сайте для подтверждения:</p>
        <h2>{code}</h2>
        <p>Код действует 5 минут.</p>
    """
    return send_email(user.email, "Код подтверждения регистрации", html)
