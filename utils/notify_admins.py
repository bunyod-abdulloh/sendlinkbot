import logging

from aiogram import Bot

from data.config import ADMINS


async def on_startup_notify(bot: Bot):
    try:
        await bot.send_message(chat_id=ADMINS[0], text="Bot ishga tushdi!")
    except Exception as err:
        logging.exception(err)
