import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_get_words(client, test_word):
    response = await client.get("/api/words")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) == 1
    assert data["items"][0]["japanese"] == "テスト"

@pytest.mark.asyncio
async def test_get_word_detail(client, test_word):
    response = await client.get(f"/api/words/{test_word.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["japanese"] == "テスト"
    assert data["romaji"] == "tesuto"
    assert data["english"] == "test"

@pytest.mark.asyncio
async def test_get_nonexistent_word(client):
    response = await client.get("/api/words/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Word not found" 