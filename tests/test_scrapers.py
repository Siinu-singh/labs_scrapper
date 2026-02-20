import pytest
from httpx import AsyncClient, ASGITransport
from src.main import app

@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client

@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_scrape_invalid_lab(client: AsyncClient):
    response = await client.post(
        "/api/v1/scrape",
        json={"test_name": "CBC", "lab_name": "invalid"}
    )
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_scrape_empty_test_name(client: AsyncClient):
    response = await client.post(
        "/api/v1/scrape",
        json={"test_name": "", "lab_name": "1mg"}
    )
    assert response.status_code == 422
