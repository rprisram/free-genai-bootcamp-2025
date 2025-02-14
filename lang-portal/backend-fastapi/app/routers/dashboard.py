from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta
from ..db import get_db
from ..database.models import StudySession, StudyActivity, Group, Word, WordReviewItem
from ..models import (
    StudySessionResponse,
    StudyProgressResponse,
    QuickStatsResponse
)
from ..utils import validate_entity_exists
from sqlalchemy.orm import joinedload

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("/last_study_session", response_model=StudySessionResponse)
async def get_last_study_session(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(StudySession)
        .options(joinedload(StudySession.activity), joinedload(StudySession.group))
        .order_by(StudySession.created_at.desc())
        .limit(1)
    )
    session = result.unique().scalar_one_or_none()
    validate_entity_exists(session, "Study session")
    
    review_count = await db.scalar(
        select(func.count())
        .select_from(WordReviewItem)
        .where(WordReviewItem.study_session_id == session.id)
    )
    
    return StudySessionResponse(
        id=session.id,
        activity_name=session.activity.name,
        group_name=session.group.name,
        group_id=session.group_id,
        study_activity_id=session.study_activity_id,
        created_at=session.created_at,
        start_time=session.created_at,
        end_time=session.created_at,
        review_items_count=review_count or 0
    )

@router.get("/study_progress", response_model=StudyProgressResponse)
async def get_study_progress(db: AsyncSession = Depends(get_db)):
    # Get total available words
    total_words = await db.scalar(select(func.count()).select_from(Word))
    
    # Get total studied words (unique words with reviews)
    studied_words = await db.scalar(
        select(func.count(Word.id.distinct()))
        .select_from(Word)
        .join(WordReviewItem)
    )
    
    return StudyProgressResponse(
        total_words_studied=studied_words or 0,
        total_available_words=total_words or 0
    )

@router.get("/quick-stats", response_model=QuickStatsResponse)
async def get_quick_stats(db: AsyncSession = Depends(get_db)):
    # Get total correct and wrong reviews
    correct_reviews = await db.scalar(
        select(func.count())
        .select_from(WordReviewItem)
        .where(WordReviewItem.correct == True)
    )
    total_reviews = await db.scalar(
        select(func.count())
        .select_from(WordReviewItem)
    )
    
    # Calculate success rate
    success_rate = (correct_reviews / total_reviews * 100) if total_reviews > 0 else 0
    
    # Get total study sessions
    total_sessions = await db.scalar(
        select(func.count())
        .select_from(StudySession)
    )
    
    # Get total active groups (groups with study sessions)
    active_groups = await db.scalar(
        select(func.count(StudySession.group_id.distinct()))
        .select_from(StudySession)
    )
    
    # Calculate study streak (consecutive days with sessions)
    today = datetime.utcnow().date()
    streak = 0
    current_date = today
    
    while True:
        has_session = await db.scalar(
            select(StudySession)
            .where(func.date(StudySession.created_at) == current_date)
        )
        if not has_session:
            break
        streak += 1
        current_date -= timedelta(days=1)
    
    return QuickStatsResponse(
        success_rate=round(success_rate, 1),
        total_study_sessions=total_sessions or 0,
        total_active_groups=active_groups or 0,
        study_streak_days=streak
    ) 