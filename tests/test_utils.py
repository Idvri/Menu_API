import json
from uuid import UUID

import pytest
from httpx import AsyncClient

from main import app
from src.utils import get_menu_db_with_counters, get_submenu_db_with_counters
from tests import override_get_async_session


@pytest.mark.asyncio
async def test_get_menu_db():
    """Тест функции для получения меню с выводом кол-ва подменю и блюд."""

    async with AsyncClient(app=app, base_url='http://localhost:8000', follow_redirects=True) as ac:
        data = {
            'id': '7f59f0a0-db4a-4b8f-a832-f63796f441a2',
            'title': 'string',
            'description': 'string'
        }
        await ac.post(url=app.url_path_for('create_menu'), content=json.dumps(data))

    gen = override_get_async_session()
    awaitable = anext(gen)
    session = await awaitable
    db_data = await get_menu_db_with_counters(data['id'], session)
    await session.close()
    assert db_data == (UUID('7f59f0a0-db4a-4b8f-a832-f63796f441a2'), 'string', 'string', 0, 0)


@pytest.mark.asyncio
async def test_get_submenu_db():
    """Тест функции для получения подменю с выводом кол-ва блюд."""

    async with AsyncClient(
            app=app,
            base_url='http://localhost:8000',
            follow_redirects=True
    ) as ac:
        data = {
            'id': '7f59f0a0-db4a-4b8f-a832-f63796f44112',
            'title': 'string',
            'description': 'string'
        }
        await ac.post(
            url=app.url_path_for('create_submenu', target_menu_id='7f59f0a0-db4a-4b8f-a832-f63796f448b4'),
            content=json.dumps(data)
        )

    gen = override_get_async_session()
    awaitable = anext(gen)
    session = await awaitable
    db_data = await get_submenu_db_with_counters(data['id'], session)
    await session.close()
    assert db_data == (UUID('7f59f0a0-db4a-4b8f-a832-f63796f44112'), 'string', 'string', 0)
