import json

import pytest
from httpx import AsyncClient

from main import app


@pytest.mark.asyncio
async def test_by_postman_scenario():
    async with AsyncClient(app=app, base_url='http://localhost:8000', follow_redirects=True) as ac:
        # Создает меню.
        data = {
            'id': '7f59f0a0-db4a-4b8f-a832-f63796f443b7',
            'title': 'test title',
            'description': 'test description'
        }
        response = await ac.post(url=app.url_path_for('create_menu'), content=json.dumps(data))
        assert response.status_code == 201
        assert response.json() == {
            'id': '7f59f0a0-db4a-4b8f-a832-f63796f443b7',
            'title': 'test title',
            'description': 'test description'
        }
        # Создает подменю.
        data = {
            'id': '7f59f0a0-db4a-4b8f-a832-f63796f443b5',
            'title': 'test title',
            'description': 'test description'
        }
        response = await ac.post(
            url=app.url_path_for('create_submenu', target_menu_id='7f59f0a0-db4a-4b8f-a832-f63796f443b7'),
            content=json.dumps(data)
        )
        assert response.status_code == 201
        assert response.json() == {
            'id': '7f59f0a0-db4a-4b8f-a832-f63796f443b5',
            'title': 'test title',
            'description': 'test description'
        }
        # Создает блюдо 1.
        data = {
            'id': '7f59f0a0-db4a-4b8f-a832-f63796f443b8',
            'title': 'test title',
            'description': 'test description',
            'price': '10'
        }
        response = await ac.post(
            url=app.url_path_for(
                'create_dish',
                target_menu_id='7f59f0a0-db4a-4b8f-a832-f63796f443b7',
                target_submenu_id='7f59f0a0-db4a-4b8f-a832-f63796f443b5'
            ),
            content=json.dumps(data)
        )
        assert response.status_code == 201
        assert response.json() == {
            'id': '7f59f0a0-db4a-4b8f-a832-f63796f443b8',
            'title': 'test title',
            'description': 'test description',
            'price': '10',
        }
        # Создает блюдо 2.
        data = {
            'id': '7f59f0a0-db4a-4b8f-a832-f63796f443b4',
            'title': 'test title',
            'description': 'test description',
            'price': '10'
        }
        response = await ac.post(
            url=app.url_path_for(
                'create_dish',
                target_menu_id='7f59f0a0-db4a-4b8f-a832-f63796f443b7',
                target_submenu_id='7f59f0a0-db4a-4b8f-a832-f63796f443b5'
            ),
            content=json.dumps(data)
        )
        assert response.status_code == 201
        assert response.json() == {
            'id': '7f59f0a0-db4a-4b8f-a832-f63796f443b4',
            'title': 'test title',
            'description': 'test description',
            'price': '10'
        }
        # Просматривает определенное меню.
        response = await ac.get(
            url=app.url_path_for('get_menu', target_menu_id='7f59f0a0-db4a-4b8f-a832-f63796f443b7')
        )
        assert response.status_code == 200
        assert response.json() == {
            'id': '7f59f0a0-db4a-4b8f-a832-f63796f443b7',
            'title': 'test title',
            'description': 'test description',
            'submenus_count': 1,
            'dishes_count': 2
        }
        # Просматривает определенное подменю.
        response = await ac.get(
            url=app.url_path_for(
                'get_submenu',
                target_menu_id='7f59f0a0-db4a-4b8f-a832-f63796f443b7',
                target_submenu_id='7f59f0a0-db4a-4b8f-a832-f63796f443b5'
            ),
        )
        assert response.status_code == 200
        assert response.json() == {
            'id': '7f59f0a0-db4a-4b8f-a832-f63796f443b5',
            'title': 'test title',
            'description': 'test description',
            'dishes_count': 2
        }
        # Удаляет определенное подменю.
        response = await ac.delete(
            url=app.url_path_for(
                'delete_submenu',
                target_menu_id='7f59f0a0-db4a-4b8f-a832-f63796f443b7',
                target_submenu_id='7f59f0a0-db4a-4b8f-a832-f63796f443b5')
        )
        assert response.status_code == 200
        assert response.json() == {'message': 'Success.'}
        # Просматривает список подменю определенного меню.
        response = await ac.get(
            url=app.url_path_for('get_submenus', target_menu_id='7f59f0a0-db4a-4b8f-a832-f63796f443b7')
        )
        assert response.status_code == 200
        assert response.json() == []
        # Просматривает список блюд определенного подменю.
        response = await ac.get(
            url=app.url_path_for(
                'get_dishes',
                target_menu_id='7f59f0a0-db4a-4b8f-a832-f63796f443b7',
                target_submenu_id='7f59f0a0-db4a-4b8f-a832-f63796f443b5'
            ),
        )
        assert response.status_code == 200
        assert response.json() == []
        # Просматривает определенное меню.
        response = await ac.get(
            url=app.url_path_for('get_menu', target_menu_id='7f59f0a0-db4a-4b8f-a832-f63796f443b7')
        )
        assert response.status_code == 200
        assert response.json() == {
            'id': '7f59f0a0-db4a-4b8f-a832-f63796f443b7',
            'title': 'test title',
            'description': 'test description',
            'submenus_count': 0,
            'dishes_count': 0
        }
        # Удаляет определенное меню.
        response = await ac.delete(
            url=app.url_path_for('delete_menu', target_menu_id='7f59f0a0-db4a-4b8f-a832-f63796f443b7')
        )
        assert response.status_code == 200
        assert response.json() == {'message': 'Success.'}
        # Просматривает список меню.
        response = await ac.get(url=app.url_path_for('get_menus'))
        assert response.status_code == 200
        assert response.json() == []
