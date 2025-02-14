from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload
from ..db import get_db
from ..database.models import Group, Word, WordGroup, StudySession, WordReviewItem, StudyActivity
from ..models import (
    GroupListResponse, GroupDetail, GroupStats, GroupInList,
    WordInList, WordListResponse, StudySessionInList, StudySessionListResponse
)
from ..utils import (
    create_paginated_response, 
    validate_entity_exists,
    create_success_response,
    PaginationParams
)

router = APIRouter(prefix="/api/groups", tags=["groups"])

@router.get("/", response_model=GroupListResponse)
async def get_groups(
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db)
):
    total_count = await db.scalar(select(func.count()).select_from(Group))
    
    result = await db.execute(
        select(Group)
        .offset((pagination.page - 1) * pagination.items_per_page)
        .limit(pagination.items_per_page)
    )
    groups = result.scalars().all()
    
    # Get word count for each group
    group_list = []
    for group in groups:
        word_count = await db.scalar(
            select(func.count())
            .select_from(WordGroup)
            .where(WordGroup.group_id == group.id)
        )
        group_list.append(
            GroupInList(
                id=group.id,
                name=group.name,
                word_count=word_count or 0
            )
        )
    
    return create_paginated_response(group_list, total_count, pagination)

@router.get("/{group_id}", response_model=GroupDetail)
async def get_group(group_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Group).options(joinedload(Group.words)).where(Group.id == group_id)
    result = await db.execute(query)
    group = result.unique().scalar_one_or_none()
    validate_entity_exists(group, "Group")
    
    word_count = await db.scalar(
        select(func.count())
        .select_from(WordGroup)
        .where(WordGroup.group_id == group_id)
    )
    
    return GroupDetail(
        id=group.id,
        name=group.name,
        stats=GroupStats(total_word_count=word_count or 0)
    )

@router.get("/{group_id}/words", response_model=WordListResponse)
async def get_group_words(
    group_id: int,
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db)
):
    group = await db.scalar(select(Group).where(Group.id == group_id))
    validate_entity_exists(group, "Group")
    
    total_count = await db.scalar(
        select(func.count())
        .select_from(Word)
        .join(WordGroup)
        .where(WordGroup.group_id == group_id)
    )
    
    result = await db.execute(
        select(Word)
        .join(WordGroup)
        .where(WordGroup.group_id == group_id)
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

@router.get("/{group_id}/study_sessions", response_model=StudySessionListResponse)
async def get_group_study_sessions(
    group_id: int,
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db)
):
    group = await db.scalar(select(Group).where(Group.id == group_id))
    validate_entity_exists(group, "Group")
    
    total_count = await db.scalar(
        select(func.count())
        .select_from(StudySession)
        .where(StudySession.group_id == group_id)
    )
    
    result = await db.execute(
        select(StudySession, StudyActivity)
        .join(StudyActivity)
        .where(StudySession.group_id == group_id)
        .offset((pagination.page - 1) * pagination.items_per_page)
        .limit(pagination.items_per_page)
    )
    sessions = result.all()
    
    session_list = []
    for session, activity in sessions:
        review_count = await db.scalar(
            select(func.count())
            .select_from(WordReviewItem)
            .where(WordReviewItem.study_session_id == session.id)
        )
        session_list.append(
            StudySessionInList(
                id=session.id,
                activity_name=activity.name,
                group_name=group.name,
                group_id=session.group_id,
                study_activity_id=session.study_activity_id,
                created_at=session.created_at,
                start_time=session.created_at,
                end_time=session.created_at,
                review_items_count=review_count or 0
            )
        )
    
    return create_paginated_response(session_list, total_count, pagination) 