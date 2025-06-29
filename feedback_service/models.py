from datetime import datetime, timezone
from .db import db

class Feedback(db.Model):
    __tablename__ = 'feedback'

    id = db.Column(db.Integer, primary_key=True)

    # Кто оставил
    user_id = db.Column(db.Integer, nullable=True)
    last_name = db.Column(db.String(50), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    middle_name = db.Column(db.String(50), nullable=True)
    role_at_time = db.Column(db.String(20), nullable=True)  # 'teacher', 'student', 'admin', 'expert', 'guest'

    # Email для ответа (обязательно)
    email = db.Column(db.String(120), nullable=False)

    # Сообщение
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Статус обработки
    is_processed = db.Column(db.Boolean, default=False)
    processed_at = db.Column(db.DateTime, nullable=True)
    is_read = db.Column(db.Boolean, default=False)        # <-- Новое поле!

    # Ответ админа
    answer_text = db.Column(db.Text, nullable=True)
    answer_method = db.Column(db.String(20), nullable=True)  # 'email', 'support_chat'
    answered_by = db.Column(db.Integer, nullable=True)
    answered_at = db.Column(db.DateTime, nullable=True)

    # Архивация
    is_archived = db.Column(db.Boolean, default=False)
    archived_at = db.Column(db.DateTime, nullable=True)

    # Привязка к support_chat (тикет)
    support_chat_id = db.Column(db.Integer, nullable=True)

    # Примечание админа
    admin_note = db.Column(db.String(200), nullable=True)

    # Проперти для полного ФИО (на лету, не в БД)
    @property
    def fio(self):
        return f"{self.last_name} {self.first_name} {self.middle_name or ''}".strip()
