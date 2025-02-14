from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Word(Base):
    __tablename__ = "words"
    
    id = Column(Integer, primary_key=True)
    japanese = Column(String, nullable=False)
    romaji = Column(String, nullable=False)
    english = Column(String, nullable=False)
    
    # Relationships
    groups = relationship("Group", secondary="words_groups", back_populates="words")
    review_items = relationship("WordReviewItem", back_populates="word")

class Group(Base):
    __tablename__ = "groups"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    
    # Relationships
    words = relationship("Word", secondary="words_groups", back_populates="groups")
    study_sessions = relationship("StudySession", back_populates="group")

class WordGroup(Base):
    __tablename__ = "words_groups"
    
    id = Column(Integer, primary_key=True)
    word_id = Column(Integer, ForeignKey("words.id"), nullable=False)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)

class StudyActivity(Base):
    __tablename__ = "study_activities"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    thumbnail_url = Column(String)
    description = Column(String)
    
    # Relationships
    sessions = relationship("StudySession", back_populates="activity")

class StudySession(Base):
    __tablename__ = "study_sessions"
    
    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    study_activity_id = Column(Integer, ForeignKey("study_activities.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    
    # Relationships
    group = relationship("Group", back_populates="study_sessions")
    activity = relationship("StudyActivity", back_populates="sessions")
    review_items = relationship("WordReviewItem", back_populates="study_session")

class WordReviewItem(Base):
    __tablename__ = "word_review_items"
    
    id = Column(Integer, primary_key=True)
    word_id = Column(Integer, ForeignKey("words.id"), nullable=False)
    study_session_id = Column(Integer, ForeignKey("study_sessions.id"), nullable=False)
    correct = Column(Boolean, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    word = relationship("Word", back_populates="review_items")
    study_session = relationship("StudySession", back_populates="review_items") 