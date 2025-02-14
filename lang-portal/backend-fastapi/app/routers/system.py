from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete
from ..db import get_db
from ..database.models import StudySession, WordReviewItem, Word, Group, WordGroup
from ..utils import create_success_response

router = APIRouter(prefix="/api", tags=["system"])

@router.post("/reset_history")
async def reset_history(db: AsyncSession = Depends(get_db)):
    # Delete all review items
    await db.execute(delete(WordReviewItem))
    # Delete all study sessions
    await db.execute(delete(StudySession))
    await db.commit()
    
    return create_success_response("Study history has been reset")

@router.post("/full_reset")
async def full_reset(db: AsyncSession = Depends(get_db)):
    # Delete everything in order due to foreign key constraints
    await db.execute(delete(WordReviewItem))
    await db.execute(delete(StudySession))
    await db.execute(delete(WordGroup))
    await db.execute(delete(Word))
    await db.execute(delete(Group))
    await db.commit()
    
    return create_success_response("System has been fully reset") 