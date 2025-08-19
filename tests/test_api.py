import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_create_order():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/orders/",
            json={"vendor": "Supplier A", "amount": 500.0, "category": "inventory", "date": "2025-08-18"}
        )
    assert response.status_code == 200
    assert response.json()["vendor"] == "Supplier A"

@pytest.mark.asyncio
async def test_get_orders():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/orders/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)