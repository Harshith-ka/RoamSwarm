import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_health_and_root():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/health")
        assert res.status_code == 200
        assert res.json()["status"] == "healthy"

        res_root = await client.get("/")
        assert res_root.status_code == 200
        assert "Orchestrator" in res_root.json()["agents"]

@pytest.mark.asyncio
async def test_evaluations_api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/evaluations/dataset")
        assert res.status_code == 200
        data = res.json()
        assert data["count"] >= 50
        assert len(data["landmarks"]) >= 50

@pytest.mark.asyncio
async def test_landmarks_nearby_api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/landmarks/nearby?latitude=13.0334&longitude=80.2699&radius_meters=1500")
        assert res.status_code == 200
        data = res.json()
        assert "landmarks" in data
