import pytest
from datetime import datetime
from sqlalchemy import select
from app.database.models import StudyActivity, StudySession, WordReviewItem

@pytest.mark.asyncio
async def test_create_study_activity(db_session):
    activity = StudyActivity(
        name="Vocabulary Quiz",
        thumbnail_url="https://example.com/quiz.jpg",
        description="Test your vocabulary"
    )
    db_session.add(activity)
    await db_session.commit()
    
    result = await db_session.execute(
        select(StudyActivity).where(StudyActivity.name == "Vocabulary Quiz")
    )
    saved_activity = result.scalar_one()
    assert saved_activity.name == "Vocabulary Quiz"
    assert saved_activity.description == "Test your vocabulary"

@pytest.mark.asyncio
async def test_study_session_relationships(db_session, test_group, test_study_activity):
    # Create study session
    session = StudySession(
        group_id=test_group.id,
        study_activity_id=test_study_activity.id
    )
    db_session.add(session)
    await db_session.commit()
    
    # Verify relationships
    result = await db_session.execute(select(StudySession).where(StudySession.id == session.id))
    saved_session = result.scalar_one()
    assert saved_session.group.name == "Test Group"
    assert saved_session.activity.name == "Test Activity"

@pytest.mark.asyncio
async def test_word_review_item(db_session, test_word):
    # Create study session first
    session = StudySession(
        group_id=(await db_session.execute(select(test_word.groups[0].id))).scalar_one(),
        study_activity_id=1
    )
    db_session.add(session)
    await db_session.commit()
    
    # Create review item
    review = WordReviewItem(
        word_id=test_word.id,
        study_session_id=session.id,
        correct=True
    )
    db_session.add(review)
    await db_session.commit()
    
    # Verify review
    result = await db_session.execute(
        select(WordReviewItem).where(WordReviewItem.word_id == test_word.id)
    )
    saved_review = result.scalar_one()
    assert saved_review.correct == True
    assert isinstance(saved_review.created_at, datetime) 