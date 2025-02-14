import json
from pathlib import Path
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import (
    Word, Group, WordGroup, StudyActivity,
    StudySession, WordReviewItem
)

async def seed_data():
    """Seed database with initial data"""
    try:
        root_dir = Path(__file__).parent.parent
        engine = create_async_engine(f"sqlite+aiosqlite:///{root_dir}/words.db")
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async with async_session() as db:
            # 1. Load and insert groups
            with open(root_dir / "seeds" / "groups.json") as f:
                groups_data = json.load(f)
            
            groups_map = {}  # Store group id mapping
            for group_data in groups_data["groups"]:
                group = Group(name=group_data["name"])
                db.add(group)
                await db.flush()
                groups_map[group.name] = group
            
            # 2. Load and insert words with group associations
            with open(root_dir / "seeds" / "words.json") as f:
                words_data = json.load(f)
            
            words_map = {}  # Store word id mapping
            for word_data in words_data["words"]:
                word = Word(
                    japanese=word_data["japanese"],
                    romaji=word_data["romaji"],
                    english=word_data["english"]
                )
                db.add(word)
                await db.flush()
                words_map[word.japanese] = word
                
                # Create word-group associations
                for group_name in word_data["groups"]:
                    group = groups_map[group_name]
                    word_group = WordGroup(word_id=word.id, group_id=group.id)
                    db.add(word_group)
            
            # 3. Load and insert study activities
            with open(root_dir / "seeds" / "study_activities.json") as f:
                activities_data = json.load(f)
            
            activities_map = {}  # Store activity id mapping
            for activity_data in activities_data["activities"]:
                activity = StudyActivity(**activity_data)
                db.add(activity)
                await db.flush()
                activities_map[activity.name] = activity
            
            # 4. Create sample study sessions and reviews
            # Last 3 days of study sessions
            for days_ago in range(3):
                session_date = datetime.utcnow() - timedelta(days=days_ago)
                
                # Create one session per activity per day
                for activity in activities_map.values():
                    for group in groups_map.values():
                        session = StudySession(
                            group_id=group.id,
                            study_activity_id=activity.id,
                            created_at=session_date
                        )
                        db.add(session)
                        await db.flush()
                        
                        # Add some word reviews for each session
                        for word in words_map.values():
                            # Randomly review some words (simulate real usage)
                            if word.japanese in ["こんにちは", "ありがとう"]:  # Sample frequently reviewed words
                                review = WordReviewItem(
                                    word_id=word.id,
                                    study_session_id=session.id,
                                    correct=True,  # Simulate mostly correct answers
                                    created_at=session_date
                                )
                                db.add(review)
            
            await db.commit()
            print("✅ Database seeded successfully")
            return True
            
    except Exception as e:
        print(f"❌ Error seeding database: {str(e)}")
        return False

if __name__ == "__main__":
    import asyncio
    asyncio.run(seed_data()) 