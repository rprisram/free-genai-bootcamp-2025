import pytest
import asyncio
from pathlib import Path
from tasks.seed_data import seed_data
from app.database.models import Word, Group, StudyActivity

@pytest.mark.asyncio
async def test_seed_data(tmp_path):
    # Set up test environment
    os.chdir(tmp_path)
    
    # Create seeds directory and files
    seeds_dir = tmp_path / "seeds"
    seeds_dir.mkdir()
    
    # Create words.json
    (seeds_dir / "words.json").write_text("""
    {
        "words": [
            {
                "japanese": "こんにちは",
                "romaji": "konnichiwa",
                "english": "hello",
                "groups": ["Basic Greetings"]
            }
        ]
    }
    """)
    
    # Create study_activities.json
    (seeds_dir / "study_activities.json").write_text("""
    {
        "activities": [
            {
                "name": "Vocabulary Quiz",
                "thumbnail_url": "https://example.com/quiz.jpg",
                "description": "Practice vocabulary"
            }
        ]
    }
    """)
    
    # Run seeding
    assert await seed_data() == True
    
    # Verify data was seeded
    async with AsyncSession(engine) as session:
        # Check words
        result = await session.execute(select(Word))
        words = result.scalars().all()
        assert len(words) == 1
        assert words[0].japanese == "こんにちは"
        
        # Check groups
        result = await session.execute(select(Group))
        groups = result.scalars().all()
        assert len(groups) == 1
        assert groups[0].name == "Basic Greetings"
        
        # Check study activities
        result = await session.execute(select(StudyActivity))
        activities = result.scalars().all()
        assert len(activities) == 1
        assert activities[0].name == "Vocabulary Quiz" 