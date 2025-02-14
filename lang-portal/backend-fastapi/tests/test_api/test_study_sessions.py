import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_sessions(client, test_group, test_study_activity):
    # Create a study session first
    from app.database.models import StudySession
    async with AsyncClient(app=client.app) as ac:
        response = await ac.post(
            "/api/study_sessions",
            json={
                "group_id": test_group.id,
                "study_activity_id": test_study_activity.id
            }
        )
    assert response.status_code == 201
    
    # Get sessions
    response = await client.get("/api/study_sessions")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["group_name"] == "Test Group"

@pytest.mark.asyncio
async def test_review_word(client, test_word, test_group, test_study_activity):
    # Create session first
    session_response = await client.post(
        "/api/study_sessions",
        json={
            "group_id": test_group.id,
            "study_activity_id": test_study_activity.id
        }
    )
    session_id = session_response.json()["id"]
    
    # Submit review
    response = await client.post(
        f"/api/study_sessions/{session_id}/words/{test_word.id}/review",
        json={"correct": True}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert data["data"]["correct"] == True 