from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload
from typing import Optional
from ..db import get_db
from ..database.models import Word, WordReviewItem
from ..utils import create_paginated_response, validate_entity_exists, PaginationParams
from ..models import (
    WordListResponse, 
    WordDetail, 
    WordInList,
    WordStats,
    GroupInWord
)

router = APIRouter(prefix="/api/words", tags=["words"])

@router.get("/", response_model=WordListResponse)
async def get_words(
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db)
):
    # Get total count
    total_count = await db.scalar(select(func.count()).select_from(Word))
    
    # Get paginated words
    result = await db.execute(
        select(Word)
        .offset((pagination.page - 1) * pagination.items_per_page)
        .limit(pagination.items_per_page)
    )
    words = result.scalars().all()
    
    # Get review counts for each word
    word_stats = {}
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
        word_stats[word.id] = {"correct": correct_count or 0, "wrong": wrong_count or 0}
    
    # Convert to response model
    word_list = [
        WordInList(
            japanese=w.japanese,
            romaji=w.romaji,
            english=w.english,
            correct_count=word_stats[w.id]["correct"],
            wrong_count=word_stats[w.id]["wrong"]
        ) for w in words
    ]
    
    return create_paginated_response(word_list, total_count, pagination)

@router.get("/{word_id}", response_model=WordDetail)
async def get_word(word_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Word).options(joinedload(Word.groups)).where(Word.id == word_id)
    result = await db.execute(query)
    word = result.unique().scalar_one_or_none()
    
    if not word:
        raise HTTPException(status_code=404, detail="Word not found")
    
    # Get review stats
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
    
    return WordDetail(
        japanese=word.japanese,
        romaji=word.romaji,
        english=word.english,
        stats=WordStats(
            correct_count=correct_count or 0,
            wrong_count=wrong_count or 0
        ),
        groups=[GroupInWord(id=g.id, name=g.name) for g in word.groups]
    ) 