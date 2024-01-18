from fastapi import FastAPI

from src.routers import menu_router

app = FastAPI(
    title='CRUD Menu.'
)

app.include_router(
    menu_router
)
