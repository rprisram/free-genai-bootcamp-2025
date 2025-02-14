import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_groups(client, test_group):
    response = await client.get("/api/groups")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "Test Group"

@pytest.mark.asyncio
async def test_get_group_detail(client, test_group):
    response = await client.get(f"/api/groups/{test_group.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Group"
    assert "stats" in data

@pytest.mark.asyncio
async def test_get_group_words(client, test_group, test_word):
    # Add word to group first
    from app.database.models import WordGroup
    async with AsyncClient(app=client.app) as ac:
        await ac.post(f"/api/groups/{test_group.id}/words/{test_word.id}")
    
    response = await client.get(f"/api/groups/{test_group.id}/words")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["japanese"] == "テスト" 