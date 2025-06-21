-- Убираем enum, комментарии, внешние ключи после
CREATE TABLE User (
  id INTEGER PRIMARY KEY,
  email TEXT NOT NULL,
  password TEXT NOT NULL,
  role_id INTEGER,
  is_system_generated BOOLEAN,
  created_at DATETIME,
  updated_at DATETIME,
  FOREIGN KEY(role_id) REFERENCES Role(id)
);

CREATE TABLE Role (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL
);

CREATE TABLE Token (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  token TEXT NOT NULL,
  type TEXT,
  expires_at DATETIME,
  created_at DATETIME,
  FOREIGN KEY(user_id) REFERENCES User(id)
);

CREATE TABLE PasswordResetToken (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  token TEXT NOT NULL,
  expires_at DATETIME,
  used BOOLEAN,
  FOREIGN KEY(user_id) REFERENCES User(id)
);

CREATE TABLE AccessRequest (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  requested_role TEXT,
  status TEXT,
  created_at DATETIME,
  FOREIGN KEY(user_id) REFERENCES User(id)
);

CREATE TABLE City (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL
);

CREATE TABLE School (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  city_id INTEGER,
  manual BOOLEAN,
  verified BOOLEAN,
  FOREIGN KEY(city_id) REFERENCES City(id)
);

CREATE TABLE TeacherProfile (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  fio TEXT,
  school_id INTEGER,
  city_id INTEGER,
  FOREIGN KEY(user_id) REFERENCES User(id),
  FOREIGN KEY(school_id) REFERENCES School(id),
  FOREIGN KEY(city_id) REFERENCES City(id)
);

CREATE TABLE StudentProfile (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  fio TEXT,
  school_id INTEGER,
  city_id INTEGER,
  FOREIGN KEY(user_id) REFERENCES User(id),
  FOREIGN KEY(school_id) REFERENCES School(id),
  FOREIGN KEY(city_id) REFERENCES City(id)
);

CREATE TABLE ExpertProfile (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  fio TEXT,
  verified BOOLEAN,
  FOREIGN KEY(user_id) REFERENCES User(id)
);

CREATE TABLE ManualSchoolEntry (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  school_name TEXT,
  city_id INTEGER,
  status TEXT,
  created_at DATETIME,
  FOREIGN KEY(user_id) REFERENCES User(id),
  FOREIGN KEY(city_id) REFERENCES City(id)
);

CREATE TABLE Class (
  id INTEGER PRIMARY KEY,
  school_id INTEGER,
  archived BOOLEAN,
  grade INTEGER,
  name TEXT,
  teacher_profile_id INTEGER,
  FOREIGN KEY(school_id) REFERENCES School(id),
  FOREIGN KEY(teacher_profile_id) REFERENCES TeacherProfile(id)
);

CREATE TABLE ClassStudent (
  id INTEGER PRIMARY KEY,
  class_id INTEGER NOT NULL,
  student_profile_id INTEGER NOT NULL,
  FOREIGN KEY(class_id) REFERENCES Class(id),
  FOREIGN KEY(student_profile_id) REFERENCES StudentProfile(id)
);

CREATE TABLE Section (
  id INTEGER PRIMARY KEY,
  subject TEXT,
  grade_range TEXT,
  title TEXT
);

CREATE TABLE Topic (
  id INTEGER PRIMARY KEY,
  section_id INTEGER,
  title TEXT,
  description TEXT,
  grade_level INTEGER,
  FOREIGN KEY(section_id) REFERENCES Section(id)
);

CREATE TABLE TaskCard (
  id INTEGER PRIMARY KEY,
  topic_id INTEGER,
  title TEXT,
  description TEXT,
  owner_type TEXT,
  expert_profile_id INTEGER,
  teacher_profile_id INTEGER,
  original_task_card_id INTEGER,
  status TEXT,
  FOREIGN KEY(topic_id) REFERENCES Topic(id),
  FOREIGN KEY(expert_profile_id) REFERENCES ExpertProfile(id),
  FOREIGN KEY(teacher_profile_id) REFERENCES TeacherProfile(id),
  FOREIGN KEY(original_task_card_id) REFERENCES TaskCard(id)
);

CREATE TABLE Task (
  id INTEGER PRIMARY KEY,
  task_card_id INTEGER NOT NULL,
  prompt TEXT,
  answer_key TEXT,
  difficulty TEXT,
  is_ai_generated BOOLEAN,
  FOREIGN KEY(task_card_id) REFERENCES TaskCard(id)
);

CREATE TABLE TrainerTaskSet (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  topic_id INTEGER NOT NULL,
  difficulty TEXT,
  generated_at DATETIME,
  expires_at DATETIME,
  task_ids_json TEXT,
  FOREIGN KEY(user_id) REFERENCES User(id),
  FOREIGN KEY(topic_id) REFERENCES Topic(id)
);

CREATE TABLE CardSubmissionRequest (
  id INTEGER PRIMARY KEY,
  teacher_profile_id INTEGER NOT NULL,
  task_card_id INTEGER NOT NULL,
  status TEXT,
  reviewed_by_admin_id INTEGER,
  reviewed_at DATETIME,
  FOREIGN KEY(teacher_profile_id) REFERENCES TeacherProfile(id),
  FOREIGN KEY(task_card_id) REFERENCES TaskCard(id),
  FOREIGN KEY(reviewed_by_admin_id) REFERENCES User(id)
);

CREATE TABLE Assignment (
  id INTEGER PRIMARY KEY,
  task_card_id INTEGER NOT NULL,
  class_id INTEGER NOT NULL,
  teacher_profile_id INTEGER NOT NULL,
  assigned_at DATETIME,
  due_date DATETIME,
  FOREIGN KEY(task_card_id) REFERENCES TaskCard(id),
  FOREIGN KEY(class_id) REFERENCES Class(id),
  FOREIGN KEY(teacher_profile_id) REFERENCES TeacherProfile(id)
);

CREATE TABLE Submission (
  id INTEGER PRIMARY KEY,
  assignment_id INTEGER NOT NULL,
  student_profile_id INTEGER NOT NULL,
  submitted_at DATETIME,
  result_json TEXT,
  attempt_count INTEGER,
  time_spent INTEGER,
  FOREIGN KEY(assignment_id) REFERENCES Assignment(id),
  FOREIGN KEY(student_profile_id) REFERENCES StudentProfile(id)
);

CREATE TABLE DiagnosticTemplate (
  id INTEGER PRIMARY KEY,
  grade_level INTEGER,
  subject TEXT,
  type TEXT,
  created_at DATETIME
);

CREATE TABLE DiagnosticTemplateTask (
  id INTEGER PRIMARY KEY,
  template_id INTEGER NOT NULL,
  prompt TEXT,
  answer_key TEXT,
  difficulty TEXT,
  FOREIGN KEY(template_id) REFERENCES DiagnosticTemplate(id)
);

CREATE TABLE InitialAssessment (
  id INTEGER PRIMARY KEY,
  student_profile_id INTEGER NOT NULL,
  conducted_at DATETIME,
  FOREIGN KEY(student_profile_id) REFERENCES StudentProfile(id)
);

CREATE TABLE FinalAssessment (
  id INTEGER PRIMARY KEY,
  student_profile_id INTEGER NOT NULL,
  conducted_at DATETIME,
  FOREIGN KEY(student_profile_id) REFERENCES StudentProfile(id)
);

CREATE TABLE DiagnosticResult (
  id INTEGER PRIMARY KEY,
  assessment_id INTEGER NOT NULL,
  topic_id INTEGER NOT NULL,
  score INTEGER,
  details_json TEXT,
  FOREIGN KEY(assessment_id) REFERENCES InitialAssessment(id),
  FOREIGN KEY(topic_id) REFERENCES Topic(id)
);

CREATE TABLE LearningProgress (
  id INTEGER PRIMARY KEY,
  student_profile_id INTEGER NOT NULL,
  topic_id INTEGER NOT NULL,
  progress_percent REAL,
  last_updated DATETIME,
  FOREIGN KEY(student_profile_id) REFERENCES StudentProfile(id),
  FOREIGN KEY(topic_id) REFERENCES Topic(id)
);

CREATE TABLE ActivityLog (
  id INTEGER PRIMARY KEY,
  student_profile_id INTEGER NOT NULL,
  action_type TEXT,
  entity_type TEXT,
  assignment_id INTEGER,
  topic_id INTEGER,
  submission_id INTEGER,
  timestamp DATETIME,
  FOREIGN KEY(student_profile_id) REFERENCES StudentProfile(id)
);

CREATE TABLE ExperiencePoint (
  id INTEGER PRIMARY KEY,
  student_profile_id INTEGER NOT NULL,
  points INTEGER,
  reason TEXT,
  related_entity_type TEXT,
  assignment_id INTEGER,
  topic_id INTEGER,
  submission_id INTEGER,
  awarded_at DATETIME,
  FOREIGN KEY(student_profile_id) REFERENCES StudentProfile(id)
);

CREATE TABLE Badge (
  id INTEGER PRIMARY KEY,
  student_profile_id INTEGER NOT NULL,
  badge_type TEXT,
  awarded_at DATETIME,
  FOREIGN KEY(student_profile_id) REFERENCES StudentProfile(id)
);

CREATE TABLE MVPTag (
  id INTEGER PRIMARY KEY,
  student_profile_id INTEGER NOT NULL,
  assignment_id INTEGER NOT NULL,
  timestamp DATETIME,
  FOREIGN KEY(student_profile_id) REFERENCES StudentProfile(id),
  FOREIGN KEY(assignment_id) REFERENCES Assignment(id)
);

CREATE TABLE Rank (
  id INTEGER PRIMARY KEY,
  student_profile_id INTEGER NOT NULL,
  rank_name TEXT,
  awarded_at DATETIME,
  FOREIGN KEY(student_profile_id) REFERENCES StudentProfile(id)
);

CREATE TABLE TheoryMaterial (
  id INTEGER PRIMARY KEY,
  topic_id INTEGER NOT NULL,
  content TEXT,
  "order" INTEGER,
  FOREIGN KEY(topic_id) REFERENCES Topic(id)
);

CREATE TABLE Conversation (
  id INTEGER PRIMARY KEY,
  type TEXT,
  related_entity_type TEXT,
  related_entity_id INTEGER,
  created_at DATETIME
);

CREATE TABLE Message (
  id INTEGER PRIMARY KEY,
  conversation_id INTEGER NOT NULL,
  sender_user_id INTEGER NOT NULL,
  content TEXT,
  timestamp DATETIME,
  FOREIGN KEY(conversation_id) REFERENCES Conversation(id),
  FOREIGN KEY(sender_user_id) REFERENCES User(id)
);

CREATE TABLE Feedback (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  text TEXT,
  email_at_time TEXT,
  fio_at_time TEXT,
  created_at DATETIME,
  FOREIGN KEY(user_id) REFERENCES User(id)
);

CREATE TABLE SchoolGroup (
  id INTEGER PRIMARY KEY,
  name TEXT,
  description TEXT
);
