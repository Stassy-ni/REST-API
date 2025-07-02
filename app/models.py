from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
from flask_sqlalchemy import SQLAlchemy
import json

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)  # Добавляем это поле
    last_name = db.Column(db.String(50), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    middle_name = db.Column(db.String(50))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), nullable=False)  # teacher/expert
    institution = db.Column(db.String(100))
    email_confirmed = db.Column(db.Boolean, default=False)
    email_code = db.Column(db.String(6))  # код подтверждения
    email_code_created_at = db.Column(db.DateTime)
    classes = db.relationship('Class', backref='teacher', lazy=True)
    created_tasks = db.relationship('Task', backref='author', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    def get_id(self):
        return f"user-{self.id}"

class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    grade = db.Column(db.Integer, nullable=False)
    letter = db.Column(db.String(1))
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    students = db.relationship('Student', backref='class', lazy=True)

class Student(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    last_name = db.Column(db.String(50), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    middle_name = db.Column(db.String(50))
    username = db.Column(db.String(50), unique=True, nullable=False)  # Логин
    password_hash = db.Column(db.String(128))  # Хэш пароля
    role = db.Column(db.String(20), default='student')  # Роль пользователя: ученик
    grade = db.Column(db.Integer, nullable=False)  # Номер класса (например, 5, 6, 7 и т.д.)
    letter = db.Column(db.String(1), nullable=False)  # Буква класса (например, "А", "Б")
    student_number = db.Column(db.Integer)  # Порядковый номер ученика в классе
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    plain_password = db.Column(db.String(128))  # Добавляем это поле для временного хранения пароля

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    def get_id(self):
        return f"student-{self.id}"
    
    def get_progress_percentage(self):
        progress = StudentProgress.query.filter_by(student_id=self.id).first()
        if not progress or not progress.initial_test_completed:
            return 0
        elif not progress.learning_completed:
            return 33
        elif not progress.final_test_completed:
            return 66
        else:
            return 100
    
    @property
    def is_active(self):
        return True  # Или другая логика, если нужно управлять активностью

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    last_name = db.Column(db.String(50), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    middle_name = db.Column(db.String(50))
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    is_processed = db.Column(db.Boolean, default=False)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(20), nullable=False)  # addition/subtraction/multiplication/division
    difficulty = db.Column(db.String(10), nullable=False)  # easy/medium/hard
    text = db.Column(db.Text, nullable=False)  # Текст задания
    answer = db.Column(db.Text, nullable=False)  # Ответ к заданию
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Связь с тестами/работами (можно добавить позже)
    # tests = db.relationship('Test', secondary='test_tasks', back_populates='tasks')
    
    def __repr__(self):
        return f'<Task {self.id} - {self.category} - {self.difficulty}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'category': self.category,
            'difficulty': self.difficulty,
            'text': self.text,
            'answer': self.answer,
            'created_at': self.created_at.strftime('%d.%m.%Y %H:%M'),
            'author': self.author.username
        }
    
class AssessmentResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Integer, nullable=False)
    percentage = db.Column(db.Float, nullable=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    student = db.relationship('Student', backref='assessment_results')

class StudentProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    initial_test_completed = db.Column(db.Boolean, default=False)
    learning_completed = db.Column(db.Boolean, default=False)
    final_test_completed = db.Column(db.Boolean, default=False)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    student = db.relationship('Student', backref='progress')

class InitialAssessment(db.Model):
    """Входной контроль знаний"""
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    tasks_data = db.Column(db.JSON, nullable=False)
    score = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Integer, nullable=False, default=12)
    percentage = db.Column(db.Float, nullable=False)
    completed_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    student = db.relationship('Student', backref='initial_assessments')
    
    def __init__(self, student_id, tasks_data, score=None, total=None, percentage=None):
        self.student_id = student_id
        self.tasks_data = tasks_data
        self.score = score if score is not None else sum(task['score'] for task in (json.loads(tasks_data) if isinstance(tasks_data, str) else tasks_data))
        self.total = total if total is not None else len(json.loads(tasks_data) if isinstance(tasks_data, str) else len(tasks_data))
        self.percentage = percentage if percentage is not None else (self.score * 100 // self.total)

class LearningProgress(db.Model):
    """Прогресс обучения"""
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    learning_completed = db.Column(db.Boolean, default=False)
    last_updated = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    student = db.relationship('Student', backref='learning_progress')

class FinalAssessment(db.Model):
    """Выходной контроль знаний"""
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    tasks_data = db.Column(db.JSON, nullable=False)
    score = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Integer, nullable=False, default=12)
    percentage = db.Column(db.Float, nullable=False)
    completed_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    student = db.relationship('Student', backref='final_assessments')
    
    def __init__(self, student_id, tasks_data, score=None, total=None, percentage=None):
        self.student_id = student_id
        self.tasks_data = tasks_data
        self.score = score if score is not None else sum(task['score'] for task in (json.loads(tasks_data) if isinstance(tasks_data, str) else tasks_data))
        self.total = total if total is not None else len(json.loads(tasks_data) if isinstance(tasks_data, str) else len(tasks_data))
        self.percentage = percentage if percentage is not None else (self.score / self.total) * 100

class StudentAnalysis(db.Model):
    """Анализ прогресса ученика"""
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    initial_assessment_data = db.Column(db.JSON)
    learning_completed = db.Column(db.Boolean)
    final_assessment_data = db.Column(db.JSON)
    percentage_difference = db.Column(db.Float)
    analysis_text = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    student = db.relationship('Student', backref='analyses')
    
    def generate_analysis(self):
        """Генерирует текстовый анализ прогресса ученика"""
        initial_data = json.loads(self.initial_assessment_data) if self.initial_assessment_data else []
        final_data = json.loads(self.final_assessment_data) if self.final_assessment_data else []
        
        analysis = []
        
        # Общий прогресс
        initial_percentage = sum(task['score'] for task in initial_data) / len(initial_data) * 100 if initial_data else 0
        final_percentage = sum(task['score'] for task in final_data) / len(final_data) * 100 if final_data else 0
        progress = final_percentage - initial_percentage
        
        analysis.append(f"Общий прогресс: {progress:.1f}%")
        
        # Анализ по категориям заданий
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
                cat_progress = final_score - init_score
                
                analysis.append(f"\n{name}: было {init_score:.1f}%, стало {final_score:.1f}% (изменение: {cat_progress:+.1f}%)")
        
        # Ошибки и успехи
        if final_data:
            incorrect = [t for t in final_data if t['score'] == 0]
            if incorrect:
                analysis.append("\n\nОшибки в следующих типах заданий:")
                for task in incorrect:
                    analysis.append(f"- {categories.get(task['category'], task['category'])}: {task['text']} (Ваш ответ: {task['user_answer']}, Правильный: {task['correct_answer']})")
            
            correct = [t for t in final_data if t['score'] == 1]
            if correct:
                analysis.append("\n\nУспешно выполнены:")
                for task in correct:
                    analysis.append(f"- {categories.get(task['category'], task['category'])}: {task['text']}")
        
        self.analysis_text = "\n".join(analysis)
        return self.analysis_text