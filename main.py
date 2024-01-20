from fastapi import FastAPI, APIRouter

from src.routers import menu_router, submenu_router, dish_router

app = FastAPI(
    title='CRUD Menu.'
)

router = APIRouter(
    prefix='/api/v1',
)

submenu_router.include_router(dish_router, prefix='/{target_submenu_id}')

menu_router.include_router(submenu_router, prefix='/{target_menu_id}')

router.include_router(menu_router)

app.include_router(router)
