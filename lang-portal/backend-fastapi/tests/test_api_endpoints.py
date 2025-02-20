import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
class TestAPIEndpoints:
    # Words API
    async def test_get_words(self, client):
        async with AsyncClient(app=app, base_url="http://test", follow_redirects=True) as ac:
            response = await ac.get("/api/words")
            assert response.status_code == 200

    async def test_get_word_detail(self, client):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/api/words/1")
            assert response.status_code == 200

    # Groups API
    async def test_get_groups(self, client):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/api/groups")
            assert response.status_code == 200

    async def test_get_group_detail(self, client):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/api/groups/1")
            assert response.status_code == 200

    async def test_get_group_words(self, client):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/api/groups/1/words")
            assert response.status_code == 200

    async def test_get_group_study_sessions(self, client):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/api/groups/1/study_sessions")
            assert response.status_code == 200

    # Study Activities API
    async def test_get_activity(self, client):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/api/study_activities/1")
            assert response.status_code == 200

    async def test_get_activity_sessions(self, client):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/api/study_activities/1/study_sessions")
            assert response.status_code == 200

    async def test_create_activity(self, client):
        # First create a group
        async with AsyncClient(app=app, base_url="http://test", follow_redirects=True) as ac:
            group_response = await ac.post(
                "/api/groups",
                json={"name": "Test Group"}
            )
            assert group_response.status_code == 200
            group_id = group_response.json()["id"]

            # Then create activity with valid group_id
            response = await ac.post(
                "/api/study_activities",
                json={
                    "name": "New Activity",
                    "thumbnail_url": "https://example.com/new.jpg",
                    "description": "Test activity",
                    "group_id": group_id
                }
            )
            assert response.status_code == 200

    # Study Sessions API
    async def test_get_sessions(self, client):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/api/study_sessions")
            assert response.status_code == 200

    async def test_get_session(self, client):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/api/study_sessions/1")
            assert response.status_code == 200

    async def test_get_session_words(self, client):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/api/study_sessions/1/words")
            assert response.status_code == 200

    async def test_review_word(self, client):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post(
                "/api/study_sessions/1/words/1/review",
                json={"correct": True}
            )
            assert response.status_code == 200

    # Dashboard API
    async def test_get_last_study_session(self, client):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/api/dashboard/last_study_session")
            assert response.status_code == 200

    async def test_get_study_progress(self, client):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/api/dashboard/study_progress")
            assert response.status_code == 200

    async def test_get_quick_stats(self, client):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/api/dashboard/quick-stats")
            assert response.status_code == 200

    # System API
    async def test_reset_history(self, client):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/api/reset_history")
            assert response.status_code == 200

    async def test_full_reset(self, client):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/api/full_reset")
            assert response.status_code == 200 