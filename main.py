from fastapi import APIRouter, FastAPI
from httpx import Request
from sqlalchemy.exc import NoResultFound
from starlette.responses import JSONResponse
from starlette.status import HTTP_404_NOT_FOUND

from src.routers import dish_router, menu_router, submenu_router

app = FastAPI(
    title='Menu API.'
)

router = APIRouter(
    prefix='/api/v1',
)

submenu_router.include_router(dish_router, prefix='/{target_submenu_id}')

menu_router.include_router(submenu_router, prefix='/{target_menu_id}')

router.include_router(menu_router)

app.include_router(router)


@app.exception_handler(NoResultFound)
async def menu_exception_handler(request: Request, exc: NoResultFound):
    return JSONResponse(content={'detail': f'{exc.args} not found'}, status_code=HTTP_404_NOT_FOUND)
