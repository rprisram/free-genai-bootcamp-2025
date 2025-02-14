import pytest
from sqlalchemy import select
from app.database.models import Word, Group, WordGroup

@pytest.mark.asyncio
async def test_create_word(db_session):
    # Create a word
    word = Word(
        japanese="こんにちは",
        romaji="konnichiwa",
        english="hello"
    )
    db_session.add(word)
    await db_session.commit()
    
    # Verify word was created
    result = await db_session.execute(select(Word).where(Word.japanese == "こんにちは"))
    saved_word = result.scalar_one()
    assert saved_word.japanese == "こんにちは"
    assert saved_word.romaji == "konnichiwa"
    assert saved_word.english == "hello"

@pytest.mark.asyncio
async def test_word_group_relationship(db_session):
    # Create word and group
    word = Word(japanese="テスト", romaji="tesuto", english="test")
    group = Group(name="Test Group")
    db_session.add_all([word, group])
    await db_session.commit()
    
    # Create relationship
    word_group = WordGroup(word_id=word.id, group_id=group.id)
    db_session.add(word_group)
    await db_session.commit()
    
    # Verify relationship
    result = await db_session.execute(
        select(Word).where(Word.id == word.id)
    )
    saved_word = result.scalar_one()
    assert len(saved_word.groups) == 1
    assert saved_word.groups[0].name == "Test Group" 