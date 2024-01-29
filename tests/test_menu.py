import json

import pytest

from httpx import AsyncClient

from main import app


@pytest.mark.asyncio
async def test_get_menus():
    """Тест по получению списка меню."""

    async with AsyncClient(app=app, base_url='http://localhost:8000/api/v1/menus', follow_redirects=True) as ac:
        response = await ac.get(url='/')
        assert response.status_code == 200

        if not response.json():
            assert response.json() == []
        else:
            assert response.json() == [
                {'id': '7f59f0a0-db4a-4b8f-a832-f63796f4443b', 'title': 'string', 'description': 'string'}
            ]


@pytest.mark.asyncio
async def test_create_menu():
    """Тест по созданию меню."""

    async with AsyncClient(app=app, base_url='http://localhost:8000/api/v1/menus', follow_redirects=True) as ac:
        # Тестирую положительный ответ.
        data = {
            'id': '7f59f0a0-db4a-4b8f-a832-f63796f448b4',
            'title': 'string',
            'description': 'string'
        }
        response = await ac.post(url='/', content=json.dumps(data))
        assert response.status_code == 201
        assert response.json() == {
            'id': '7f59f0a0-db4a-4b8f-a832-f63796f448b4',
            'title': 'string',
            'description': 'string'
        }
        # Тестирую 1 исключение.
        data = {
            'description': 'string'
        }
        response = await ac.post(url='/', content=json.dumps(data))
        assert response.status_code == 422
        assert response.json() == {
            'detail': [
                {
                    'type': 'missing',
                    'loc': [
                        'body',
                        'title'
                    ],
                    'msg': 'Field required',
                    'input': {
                        'description': 'string'
                    },
                    'url': 'https://errors.pydantic.dev/2.5/v/missing'
                }
            ]
        }


@pytest.mark.asyncio
async def test_get_menu():
    """Тест по получению определенного меню."""

    async with AsyncClient(app=app, base_url='http://localhost:8000/api/v1/menus', follow_redirects=True) as ac:
        # Тестирую положительный ответ.
        data = {
            'id': '7f59f0a0-db4a-4b8f-a832-f63796f448b5',
            'title': 'test title',
            'description': 'test description'
        }
        await ac.post(url='/', content=json.dumps(data))

        response = await ac.get(
            url='/7f59f0a0-db4a-4b8f-a832-f63796f448b5',
        )
        assert response.status_code == 200
        assert response.json() == {
            'id': '7f59f0a0-db4a-4b8f-a832-f63796f448b5',
            'title': 'test title',
            'description': 'test description',
            'submenus_count': 0,
            'dishes_count': 0
        }
        # Тестирую 1 исключение.
        response = await ac.get(
            url='/7f59f0a0-db4a-4b8f-a832-f63796f448b8',
        )
        assert response.status_code == 404
        assert response.json() == {
            'detail': 'menu not found'
        }
        # Тестирую 2 исключение.
        response = await ac.get(
            url='/7f59f0a0-db4a-4b'
        )
        assert response.status_code == 422
        assert response.json() == {
            'detail': [
                {
                    'type': 'uuid_parsing',
                    'loc': [
                        'path',
                        'target_menu_id'
                    ],
                    'msg': 'Input should be a valid UUID, invalid group count: expected 5, found 3',
                    'input': '7f59f0a0-db4a-4b',
                    'ctx': {
                        'error': 'invalid group count: expected 5, found 3'
                    },
                    'url': 'https://errors.pydantic.dev/2.5/v/uuid_parsing'
                }
            ]
        }


@pytest.mark.asyncio
async def test_update_menu():
    """Тест по изменению определенного меню."""

    async with AsyncClient(app=app, base_url='http://localhost:8000/api/v1/menus', follow_redirects=True) as ac:
        # Тестирую положительный ответ.
        data = {
            'title': 'test patched title',
            'description': 'test patched description'
        }
        response = await ac.patch(url='/7f59f0a0-db4a-4b8f-a832-f63796f448b5', content=json.dumps(data))
        assert response.status_code == 200
        assert response.json() == {
            'id': '7f59f0a0-db4a-4b8f-a832-f63796f448b5',
            'title': 'test patched title',
            'description': 'test patched description'
        }
        # Тестирую 1 исключение.
        response = await ac.patch(url='/7f59f0a0-db4a-4b8f-a832-f63796f448b8', content=json.dumps(data))
        assert response.status_code == 404
        assert response.json() == {
            'detail': 'menu not found'
        }
        # Тестирую 2 исключение.
        response = await ac.patch(url='/7f59f0a0-db4a-4b', content=json.dumps(data))
        assert response.status_code == 422
        assert response.json() == {
            'detail': [
                {
                    'type': 'uuid_parsing',
                    'loc': [
                        'path',
                        'target_menu_id'
                    ],
                    'msg': 'Input should be a valid UUID, invalid group count: expected 5, found 3',
                    'input': '7f59f0a0-db4a-4b',
                    'ctx': {
                        'error': 'invalid group count: expected 5, found 3'
                    },
                    'url': 'https://errors.pydantic.dev/2.5/v/uuid_parsing'
                }
            ]
        }


@pytest.mark.asyncio
async def test_delete_menu():
    """Тест по удалению определенного меню."""

    async with AsyncClient(app=app, base_url='http://localhost:8000/api/v1/menus', follow_redirects=True) as ac:
        # Тестирую положительный ответ.
        response = await ac.delete(url='/7f59f0a0-db4a-4b8f-a832-f63796f448b5')
        assert response.status_code == 200
        assert response.json() == {'message': 'Success.'}
        # Тестирую 1 исключение.
        response = await ac.delete(
            url='/7f59f0a0-db4a-4b8f-a832-f63796f448b8',
        )
        assert response.status_code == 404
        assert response.json() == {
            'detail': 'menu not found'
        }
        # Тестирую 2 исключение.
        response = await ac.delete(
            url='/7f59f0a0-db4a-4b'
        )
        assert response.status_code == 422
        assert response.json() == {
            'detail': [
                {
                    'type': 'uuid_parsing',
                    'loc': [
                        'path',
                        'target_menu_id'
                    ],
                    'msg': 'Input should be a valid UUID, invalid group count: expected 5, found 3',
                    'input': '7f59f0a0-db4a-4b',
                    'ctx': {
                        'error': 'invalid group count: expected 5, found 3'
                    },
                    'url': 'https://errors.pydantic.dev/2.5/v/uuid_parsing'
                }
            ]
        }
