from aiogram import Router


def setup_routers() -> Router:
    from .users import admin, start, subcribed

    from .errors import error_handler

    router = Router()

    # Agar kerak bo'lsa, o'z filteringizni o'rnating
    # start.router.message.filter(ChatTypeFilter(chat_types=[ChatType.PRIVATE]))
    # bot_admin.router.message.filter(AllowedChatFilter())
    router.include_routers(admin.router, start.router, error_handler.router, subcribed.router)

    return router
