from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime

# Base Models
class PaginationResponse(BaseModel):
    current_page: int
    total_pages: int
    total_items: int
    items_per_page: int

# Request Models
class ReviewWordRequest(BaseModel):
    correct: bool

# Response Models
class StudySessionResponse(BaseModel):
    id: int
    activity_name: str
    group_name: str
    group_id: int
    study_activity_id: int
    created_at: datetime
    start_time: datetime
    end_time: datetime
    review_items_count: int

class StudyProgressResponse(BaseModel):
    total_words_studied: int
    total_available_words: int

class QuickStatsResponse(BaseModel):
    success_rate: float
    total_study_sessions: int
    total_active_groups: int
    study_streak_days: int

# Add these models
class WordBase(BaseModel):
    japanese: str
    romaji: str
    english: str
    correct_count: int = 0
    wrong_count: int = 0

class WordInList(WordBase):
    pass

class WordStats(BaseModel):
    correct_count: int
    wrong_count: int

class GroupInWord(BaseModel):
    id: int
    name: str

class WordDetail(WordBase):
    stats: WordStats
    groups: list[GroupInWord]

class WordListResponse(BaseModel):
    items: list[WordInList]
    pagination: PaginationResponse

# Add these models
class GroupBase(BaseModel):
    id: int
    name: str

class GroupInList(GroupBase):
    word_count: int

class GroupStats(BaseModel):
    total_word_count: int

class GroupDetail(GroupBase):
    stats: GroupStats

class GroupListResponse(BaseModel):
    items: list[GroupInList]
    pagination: PaginationResponse

# Add these models for study activities
class StudyActivityBase(BaseModel):
    id: int
    name: str
    thumbnail_url: str
    description: str

class StudyActivityDetail(StudyActivityBase):
    pass

class StudyActivityCreate(BaseModel):
    group_id: int
    study_activity_id: int

class StudyActivityCreateResponse(BaseModel):
    id: int
    group_id: int

class StudySessionInList(BaseModel):
    id: int
    activity_name: str
    group_name: str
    group_id: int
    study_activity_id: int
    created_at: datetime
    start_time: datetime
    end_time: datetime
    review_items_count: int

class StudySessionListResponse(BaseModel):
    items: list[StudySessionInList]
    pagination: PaginationResponse 