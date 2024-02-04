import json

import pytest
from httpx import AsyncClient

from main import app


@pytest.mark.asyncio
async def test_get_dishes():
    """Тест по получению списка блюд."""

    async with AsyncClient(
            app=app,
            base_url='http://localhost:8000',
            follow_redirects=True
    ) as ac:
        data = {
            'id': '7f59f0a0-db4a-4b8f-a832-f63796f4443b',
            'title': 'string',
            'description': 'string'
        }
        await ac.post(url=app.url_path_for('create_menu'), content=json.dumps(data))

        data = {
            'id': '7f59f0a0-db4a-4b8f-a832-f63796f4449b',
            'title': 'string',
            'description': 'string'
        }
        await ac.post(
            url=app.url_path_for('create_submenu', target_menu_id='7f59f0a0-db4a-4b8f-a832-f63796f4443b'),
            content=json.dumps(data)
        )

        response = await ac.get(
            url=app.url_path_for(
                'get_dishes',
                target_menu_id='7f59f0a0-db4a-4b8f-a832-f63796f4443b',
                target_submenu_id='7f59f0a0-db4a-4b8f-a832-f63796f4449b'
            ),
        )
        assert response.status_code == 200
        assert response.json() == []


@pytest.mark.asyncio
async def test_create_dish():
    """Тест по созданию блюда."""

    async with AsyncClient(
            app=app,
            base_url='http://localhost:8000',
            follow_redirects=True
    ) as ac:
        # Тестирую положительный ответ.
        data = {
            'id': '7f59f0a0-db4a-4b8f-a832-f63796f4466b',
            'title': 'string',
            'description': 'string',
            'price': '10'
        }
        response = await ac.post(
            url=app.url_path_for(
                'create_dish',
                target_menu_id='7f59f0a0-db4a-4b8f-a832-f63796f4443b',
                target_submenu_id='7f59f0a0-db4a-4b8f-a832-f63796f4449b'
            ),
            content=json.dumps(data)
        )
        assert response.status_code == 201
        assert response.json() == {
            'id': '7f59f0a0-db4a-4b8f-a832-f63796f4466b',
            'title': 'string',
            'description': 'string',
            'price': '10'
        }
        # Тестирую 1 исключение.
        data = {
            'description': 'string'
        }
        response = await ac.post(
            url=app.url_path_for(
                'create_dish',
                target_menu_id='7f59f0a0-db4a-4b8f-a832-f63796f4443b',
                target_submenu_id='7f59f0a0-db4a-4b8f-a832-f63796f4449b'
            ),
            content=json.dumps(data)
        )
        assert response.status_code == 422
        assert response.json() == {
            'detail': [
                {
                    'type': 'missing',
                    'loc': ['body', 'title'],
                    'msg': 'Field required',
                    'input': {'description': 'string'},
                    'url': 'https://errors.pydantic.dev/2.5/v/missing'
                },
                {
                    'type': 'missing',
                    'loc': ['body', 'price'],
                    'msg': 'Field required',
                    'input': {'description': 'string'},
                    'url': 'https://errors.pydantic.dev/2.5/v/missing'
                }
            ]
        }


@pytest.mark.asyncio
async def test_get_dish():
    """Тест по получению определенного блюда."""

    async with AsyncClient(
            app=app,
            base_url='http://localhost:8000',
            follow_redirects=True
    ) as ac:
        # Тестирую положительный ответ.
        response = await ac.get(
            url=app.url_path_for(
                'get_dish',
                target_menu_id='7f59f0a0-db4a-4b8f-a832-f63796f4443b',
                target_submenu_id='7f59f0a0-db4a-4b8f-a832-f63796f4449b',
                target_dish_id='7f59f0a0-db4a-4b8f-a832-f63796f4466b'
            )
        )
        assert response.status_code == 200
        assert response.json() == {
            'id': '7f59f0a0-db4a-4b8f-a832-f63796f4466b',
            'title': 'string',
            'description': 'string',
            'price': '10'
        }
        # Тестирую 1 исключение.
        response = await ac.get(
            url=app.url_path_for(
                'get_dish',
                target_menu_id='7f59f0a0-db4a-4b8f-a832-f63796f4443b',
                target_submenu_id='7f59f0a0-db4a-4b8f-a832-f63796f4449b',
                target_dish_id='7f59f0a0-db4a-4b8f-a832-f63796f448b8'
            )
        )
        assert response.status_code == 404
        assert response.json() == {
            'detail': 'dish not found'
        }
        # Тестирую 2 исключение.
        response = await ac.get(
            url=app.url_path_for(
                'get_dish',
                target_menu_id='7f59f0a0-db4a-4b8f-a832-f63796f4443b',
                target_submenu_id='7f59f0a0-db4a-4b8f-a832-f63796f4449b',
                target_dish_id='7f59f0a0-db4a-4b'
            )
        )
        assert response.status_code == 422
        assert response.json() == {'detail': [
            {
                'type': 'uuid_parsing',
                'loc': ['path', 'target_dish_id'],
                'msg': 'Input should be a valid UUID, invalid group count: expected 5, found 3',
                'input': '7f59f0a0-db4a-4b', 'ctx': {'error': 'invalid group count: expected 5, found 3'},
                'url': 'https://errors.pydantic.dev/2.5/v/uuid_parsing'
            }
        ]
        }


@pytest.mark.asyncio
async def test_update_dish():
    """Тест по изменению определенного блюда."""

    async with AsyncClient(
            app=app,
            base_url='http://localhost:8000',
            follow_redirects=True
    ) as ac:
        # Тестирую положительный ответ.
        data = {
            'title': 'test patched title',
            'description': 'test patched description',
            'price': '12',
        }
        response = await ac.patch(
            url=app.url_path_for(
                'update_dish',
                target_menu_id='7f59f0a0-db4a-4b8f-a832-f63796f4443b',
                target_submenu_id='7f59f0a0-db4a-4b8f-a832-f63796f4449b',
                target_dish_id='7f59f0a0-db4a-4b8f-a832-f63796f4466b'
            ),
            content=json.dumps(data)
        )
        assert response.status_code == 200
        assert response.json() == {
            'id': '7f59f0a0-db4a-4b8f-a832-f63796f4466b',
            'title': 'test patched title',
            'description': 'test patched description',
            'price': '12'
        }
        # Тестирую 1 исключение.
        response = await ac.patch(
            url=app.url_path_for(
                'update_dish',
                target_menu_id='7f59f0a0-db4a-4b8f-a832-f63796f4443b',
                target_submenu_id='7f59f0a0-db4a-4b8f-a832-f63796f4449b',
                target_dish_id='7f59f0a0-db4a-4b8f-a832-f63796f448b8'
            ),
            content=json.dumps(data)
        )
        assert response.status_code == 404
        assert response.json() == {
            'detail': 'dish not found'
        }
        # Тестирую 2 исключение.
        response = await ac.patch(
            url=app.url_path_for(
                'update_dish',
                target_menu_id='7f59f0a0-db4a-4b8f-a832-f63796f4443b',
                target_submenu_id='7f59f0a0-db4a-4b8f-a832-f63796f4449b',
                target_dish_id='7f59f0a0-db4a-4b'
            ),
            content=json.dumps(data)
        )
        assert response.status_code == 422
        assert response.json() == {
            'detail': [
                {
                    'type': 'uuid_parsing',
                    'loc': ['path', 'target_dish_id'],
                    'msg': 'Input should be a valid UUID, invalid group count: expected 5, found 3',
                    'input': '7f59f0a0-db4a-4b', 'ctx': {'error': 'invalid group count: expected 5, found 3'},
                    'url': 'https://errors.pydantic.dev/2.5/v/uuid_parsing'
                }
            ]
        }


@pytest.mark.asyncio
async def test_delete_dish():
    """Тест по удалению определенного блюда."""

    async with AsyncClient(
            app=app,
            base_url='http://localhost:8000',
            follow_redirects=True
    ) as ac:
        # Тестирую положительный ответ.
        response = await ac.delete(
            url=app.url_path_for(
                'delete_dish',
                target_menu_id='7f59f0a0-db4a-4b8f-a832-f63796f4443b',
                target_submenu_id='7f59f0a0-db4a-4b8f-a832-f63796f4449b',
                target_dish_id='7f59f0a0-db4a-4b8f-a832-f63796f4466b'
            )
        )
        assert response.status_code == 200
        assert response.json() == {'message': 'Success.'}
        # Тестирую 1 исключение.
        response = await ac.delete(
            url=app.url_path_for(
                'delete_dish',
                target_menu_id='7f59f0a0-db4a-4b8f-a832-f63796f4443b',
                target_submenu_id='7f59f0a0-db4a-4b8f-a832-f63796f4449b',
                target_dish_id='7f59f0a0-db4a-4b8f-a832-f63796f448b8'
            )
        )
        assert response.status_code == 404
        assert response.json() == {
            'detail': 'dish not found'
        }
        # Тестирую 2 исключение.
        response = await ac.delete(
            url=app.url_path_for(
                'delete_dish',
                target_menu_id='7f59f0a0-db4a-4b8f-a832-f63796f4443b',
                target_submenu_id='7f59f0a0-db4a-4b8f-a832-f63796f4449b',
                target_dish_id='7f59f0a0-db4a-4b'
            )
        )
        assert response.status_code == 422
        assert response.json() == {
            'detail': [
                {
                    'type': 'uuid_parsing', 'loc': ['path', 'target_dish_id'],
                    'msg': 'Input should be a valid UUID, invalid group count: expected 5, found 3',
                    'input': '7f59f0a0-db4a-4b', 'ctx': {'error': 'invalid group count: expected 5, found 3'},
                    'url': 'https://errors.pydantic.dev/2.5/v/uuid_parsing'
                }
            ]
        }
