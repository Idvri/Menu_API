import json
from typing import Any
from uuid import UUID

from fastapi import Request
from redis.asyncio import Redis

from src import CACHE_TIMEOUT

from .universal import reverse


class CacheNotFound(BaseException):
    pass


async def get_cache(key: str, redis_client: Redis) -> Any:
    """Функция для получения кэша."""

    cache = await redis_client.get(key)
    if cache:
        return json.loads(cache)
    raise CacheNotFound


async def set_cache(key: str, value: Any, redis_client: Redis) -> None:
    """Функция для создания либо обновления кэша."""

    if isinstance(value, list):
        for item in value:
            if item['id']:
                item['id'] = str(item['id'])
    else:
        value['id'] = str(value['id'])
    await redis_client.set(key, json.dumps(value), ex=int(CACHE_TIMEOUT))


async def delete_cache(key: str, redis_client: Redis) -> None:
    """Функция для удаления кэша."""

    await redis_client.delete(key)


async def delete_all_depended_cache(
        request: Request,
        target_menu_id: UUID,
        redis_client: Redis,
) -> None:
    """Функция для удаления всего кэша меню."""

    await delete_cache(
        key=await reverse('get_menu', request, target_menu_id=target_menu_id),
        redis_client=redis_client
    )
    await delete_cache(
        key=await reverse('get_menus', request),
        redis_client=redis_client
    )

    submenus = await get_cache(
        key=await reverse('get_submenus', request, target_menu_id=target_menu_id),
        redis_client=redis_client
    )
    if submenus:
        submenus = json.loads(submenus)
        for submenu in submenus:

            dishes = await get_cache(
                key=await reverse(
                    'get_dishes',
                    request,
                    target_menu_id=target_menu_id,
                    target_submenu_id=submenu['id']
                ),
                redis_client=redis_client
            )
            if dishes:
                dishes = json.loads(dishes)
                for dish in dishes:
                    await delete_cache(
                        await reverse(
                            'get_dish',
                            request,
                            target_menu_id=target_menu_id,
                            target_submenu_id=str(submenu['id']),
                            target_dish_id=str(dish['id'])
                        ),
                        redis_client=redis_client
                    )

            await delete_cache(
                await reverse(
                    'get_submenu',
                    request,
                    target_menu_id=target_menu_id,
                    target_submenu_id=str(submenu['id'])
                ),
                redis_client=redis_client
            )
    await delete_cache(
        key=await reverse('get_submenus', request, target_menu_id=target_menu_id),
        redis_client=redis_client
    )
