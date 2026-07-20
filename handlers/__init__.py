from aiogram import Router
from . import common, calculation

def setup_routers() -> Router:
    root_router = Router()
    root_router.include_routers(
        common.router,
        calculation.router
    )
    return root_router