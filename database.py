from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime
import os
from config import Config

Base = declarative_base()

class MedicalImage(Base):
    __tablename__ = 'medical_images'
    
    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False, unique=True)
    filepath = Column(String(512), nullable=False)
    url_path = Column(String(512), nullable=False)  # URL path for frontend access
    description = Column(Text, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationship with quiz questions
    quiz_questions = relationship("QuizQuestion", back_populates="image")

class QuizQuestion(Base):
    __tablename__ = 'quiz_questions'
    
    id = Column(Integer, primary_key=True)
    image_id = Column(Integer, ForeignKey('medical_images.id'), nullable=False)
    correct_answer = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationship with the image
    image = relationship("MedicalImage", back_populates="quiz_questions")
    
    # Relationship with options
    options = relationship("QuizOption", back_populates="question")

class QuizOption(Base):
    __tablename__ = 'quiz_options'
    
    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey('quiz_questions.id'), nullable=False)
    option_text = Column(Text, nullable=False)
    is_correct = Column(Integer, default=0)  # 0 = false, 1 = true
    
    # Relationship with the question
    question = relationship("QuizQuestion", back_populates="options")

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)

# Database setup
def setup_database():
    engine = create_engine(Config.DATABASE_URI)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

# Create a session
db_session = setup_database() 