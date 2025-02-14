from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload
from ..db import get_db
from ..database.models import StudySession, StudyActivity, Group, Word, WordReviewItem
from ..models import (
    StudySessionResponse,
    StudySessionInList,
    StudySessionListResponse,
    WordInList,
    WordListResponse,
    ReviewWordRequest
)
from ..utils import (
    create_paginated_response,
    validate_entity_exists,
    create_success_response,
    PaginationParams
)

router = APIRouter(prefix="/api/study_sessions", tags=["study_sessions"])

@router.get("/", response_model=StudySessionListResponse)
async def get_sessions(
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db)
):
    total_count = await db.scalar(select(func.count()).select_from(StudySession))
    
    result = await db.execute(
        select(StudySession)
        .options(joinedload(StudySession.activity), joinedload(StudySession.group))
        .offset((pagination.page - 1) * pagination.items_per_page)
        .limit(pagination.items_per_page)
    )
    sessions = result.unique().scalars().all()
    
    session_list = []
    for session in sessions:
        review_count = await db.scalar(
            select(func.count())
            .select_from(WordReviewItem)
            .where(WordReviewItem.study_session_id == session.id)
        )
        session_list.append(
            StudySessionInList(
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
        )
    
    return create_paginated_response(session_list, total_count, pagination)

@router.get("/{session_id}", response_model=StudySessionResponse)
async def get_session(session_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(StudySession)
        .options(joinedload(StudySession.activity), joinedload(StudySession.group))
        .where(StudySession.id == session_id)
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
        group_id=session.group.id,
        study_activity_id=session.activity.id,
        created_at=session.created_at,
        start_time=session.created_at,
        end_time=session.created_at,
        review_items_count=review_count or 0
    )

@router.get("/{session_id}/words", response_model=WordListResponse)
async def get_session_words(
    session_id: int,
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db)
):
    session = await db.scalar(select(StudySession).where(StudySession.id == session_id))
    validate_entity_exists(session, "Study session")
    
    total_count = await db.scalar(
        select(func.count())
        .select_from(Word)
        .join(WordReviewItem)
        .where(WordReviewItem.study_session_id == session_id)
    )
    
    result = await db.execute(
        select(Word)
        .join(WordReviewItem)
        .where(WordReviewItem.study_session_id == session_id)
        .offset((pagination.page - 1) * pagination.items_per_page)
        .limit(pagination.items_per_page)
    )
    words = result.scalars().all()
    
    word_list = []
    for word in words:
        correct_count = await db.scalar(
            select(func.count())
            .select_from(WordReviewItem)
            .where(WordReviewItem.word_id == word.id)
            .where(WordReviewItem.correct == True)
        )
        wrong_count = await db.scalar(
            select(func.count())
            .select_from(WordReviewItem)
            .where(WordReviewItem.word_id == word.id)
            .where(WordReviewItem.correct == False)
        )
        word_list.append(
            WordInList(
                japanese=word.japanese,
                romaji=word.romaji,
                english=word.english,
                correct_count=correct_count or 0,
                wrong_count=wrong_count or 0
            )
        )
    
    return create_paginated_response(word_list, total_count, pagination)

@router.post("/{session_id}/words/{word_id}/review")
async def review_word(
    session_id: int,
    word_id: int,
    review: ReviewWordRequest,
    db: AsyncSession = Depends(get_db)
):
    session = await db.scalar(select(StudySession).where(StudySession.id == session_id))
    validate_entity_exists(session, "Study session")
    
    word = await db.scalar(select(Word).where(Word.id == word_id))
    validate_entity_exists(word, "Word")
    
    review_item = WordReviewItem(
        word_id=word_id,
        study_session_id=session_id,
        correct=review.correct
    )
    db.add(review_item)
    await db.commit()
    await db.refresh(review_item)
    
    return create_success_response(
        "Review recorded successfully",
        {
            "word_id": word_id,
            "study_session_id": session_id,
            "correct": review.correct,
            "created_at": review_item.created_at
        }
    ) 