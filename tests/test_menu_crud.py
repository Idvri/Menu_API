import json
import pytest

from httpx import AsyncClient

from main import app


@pytest.mark.asyncio
async def test_get_menus():
    async with AsyncClient(app=app, base_url="http://localhost:8000/api/v1/menus", follow_redirects=True) as ac:
        response = await ac.get(url='/')
        assert response.status_code == 200
        assert response.json() == []


@pytest.mark.asyncio
async def test_create_menu():
    async with AsyncClient(app=app, base_url="http://localhost:8000/api/v1/menus", follow_redirects=True) as ac:
        data = {
            "id": "7f59f0a0-db4a-4b8f-a832-f63796f448b4",
            "title": "string",
            "description": "string"
        }
        response = await ac.post(url='/', content=json.dumps(data))
        assert response.status_code == 201
        assert response.json() == {
            "id": "7f59f0a0-db4a-4b8f-a832-f63796f448b4",
            "title": "string",
            "description": "string"
        }

        data = {
            "description": "string"
        }
        response = await ac.post(url='/', content=json.dumps(data))
        assert response.status_code == 422
        assert response.json() == {
            "detail": [
                {
                    "type": "missing",
                    "loc": [
                        "body",
                        "title"
                    ],
                    "msg": "Field required",
                    "input": {
                        "description": "string"
                    },
                    "url": "https://errors.pydantic.dev/2.5/v/missing"
                }
            ]
        }
