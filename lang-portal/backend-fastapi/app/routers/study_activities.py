from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload
from ..db import get_db
from ..database.models import StudyActivity, StudySession, Group, WordReviewItem
from ..models import (
    StudyActivityDetail,
    StudyActivityCreate,
    StudyActivityCreateResponse,
    StudySessionInList,
    StudySessionListResponse
)
from ..utils import (
    create_paginated_response,
    validate_entity_exists,
    PaginationParams
)

router = APIRouter(prefix="/api/study_activities", tags=["study_activities"])

@router.get("/{activity_id}", response_model=StudyActivityDetail)
async def get_activity(activity_id: int, db: AsyncSession = Depends(get_db)):
    query = select(StudyActivity).options(joinedload(StudyActivity.sessions)).where(StudyActivity.id == activity_id)
    result = await db.execute(query)
    activity = result.unique().scalar_one_or_none()
    
    if not activity:
        raise HTTPException(status_code=404, detail="Study activity not found")
    
    return StudyActivityDetail(
        id=activity.id,
        name=activity.name,
        thumbnail_url=activity.thumbnail_url,
        description=activity.description
    )

@router.get("/{activity_id}/study_sessions", response_model=StudySessionListResponse)
async def get_activity_sessions(
    activity_id: int,
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db)
):
    # Verify activity exists
    activity = await db.scalar(select(StudyActivity).where(StudyActivity.id == activity_id))
    if not activity:
        raise HTTPException(status_code=404, detail="Study activity not found")
    
    # Get total count
    count_query = select(func.count())\
        .select_from(StudySession)\
        .where(StudySession.study_activity_id == activity_id)
    total_count = await db.scalar(count_query)
    
    # Get paginated sessions with group info
    query = select(StudySession)\
        .options(joinedload(StudySession.group))\
        .where(StudySession.study_activity_id == activity_id)\
        .offset((pagination.page - 1) * pagination.items_per_page)\
        .limit(pagination.items_per_page)
    
    result = await db.execute(query)
    sessions = result.unique().scalars().all()
    
    # Get review counts for each session
    session_stats = {}
    for session in sessions:
        review_count = await db.scalar(
            select(func.count())
            .select_from(WordReviewItem)
            .where(WordReviewItem.study_session_id == session.id)
        )
        session_stats[session.id] = review_count or 0
    
    # Convert to response model
    session_list = [
        StudySessionInList(
            id=session.id,
            activity_name=activity.name,
            group_name=session.group.name,
            group_id=session.group_id,
            study_activity_id=session.study_activity_id,
            created_at=session.created_at,
            start_time=session.created_at,
            end_time=session.created_at,
            review_items_count=session_stats[session.id]
        ) for session in sessions
    ]
    
    return StudySessionListResponse(
        items=session_list,
        pagination={
            "current_page": pagination.page,
            "total_pages": (total_count + pagination.items_per_page - 1) // pagination.items_per_page,
            "total_items": total_count,
            "items_per_page": pagination.items_per_page
        }
    )

@router.post("", response_model=StudyActivityCreateResponse)
async def create_activity(
    activity: StudyActivityCreate,
    db: AsyncSession = Depends(get_db)
):
    # Verify group exists
    group = await db.scalar(select(Group).where(Group.id == activity.group_id))
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Create new activity
    new_activity = StudyActivity(
        group_id=activity.group_id,
        study_activity_id=activity.study_activity_id
    )
    db.add(new_activity)
    await db.commit()
    await db.refresh(new_activity)
    
    return StudyActivityCreateResponse(
        id=new_activity.id,
        group_id=new_activity.group_id
    ) 