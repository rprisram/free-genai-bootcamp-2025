import pytest
from sqlalchemy import select
from app.database.models import Group, Word, WordGroup, StudySession

@pytest.mark.asyncio
async def test_create_group(db_session):
    group = Group(name="Basic Phrases")
    db_session.add(group)
    await db_session.commit()
    
    result = await db_session.execute(select(Group).where(Group.name == "Basic Phrases"))
    saved_group = result.scalar_one()
    assert saved_group.name == "Basic Phrases"

@pytest.mark.asyncio
async def test_group_words_relationship(db_session):
    # Create group and words
    group = Group(name="Test Group")
    word1 = Word(japanese="一", romaji="ichi", english="one")
    word2 = Word(japanese="二", romaji="ni", english="two")
    db_session.add_all([group, word1, word2])
    await db_session.commit()
    
    # Create relationships
    db_session.add_all([
        WordGroup(word_id=word1.id, group_id=group.id),
        WordGroup(word_id=word2.id, group_id=group.id)
    ])
    await db_session.commit()
    
    # Verify relationships
    result = await db_session.execute(select(Group).where(Group.id == group.id))
    saved_group = result.scalar_one()
    assert len(saved_group.words) == 2
    assert {w.japanese for w in saved_group.words} == {"一", "二"}

@pytest.mark.asyncio
async def test_group_study_sessions(db_session, test_study_activity):
    # Create group and session
    group = Group(name="Test Group")
    db_session.add(group)
    await db_session.commit()
    
    session = StudySession(
        group_id=group.id,
        study_activity_id=test_study_activity.id
    )
    db_session.add(session)
    await db_session.commit()
    
    # Verify relationship
    result = await db_session.execute(select(Group).where(Group.id == group.id))
    saved_group = result.scalar_one()
    assert len(saved_group.study_sessions) == 1
    assert saved_group.study_sessions[0].group_id == group.id 