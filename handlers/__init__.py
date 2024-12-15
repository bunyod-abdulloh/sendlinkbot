from aiogram import Router


def setup_routers() -> Router:
    from .users import start, subcribed, admin

    from .errors import error_handler

    router = Router()

    router.include_routers(start.router, error_handler.router, subcribed.router, admin.router)

    return router
