import logging
import asyncio
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from handlers.users.start import welcome_message
from loader import db

from states.test import AdminState
from filters.admin import IsBotAdminFilter
from data.config import ADMINS

router = Router()


@router.message(Command('admin'), IsBotAdminFilter(ADMINS))
async def admin_main(message: types.Message):
    button = types.ReplyKeyboardMarkup(
        keyboard=[[
            types.KeyboardButton(
                text="Foydalanuvchilar soni"
            ),
            types.KeyboardButton(
                text="Reklama yuborish"
            )
        ],
            [
                types.KeyboardButton(
                    text="Delete (except today)"
                ),
                types.KeyboardButton(
                    text="Delete blockers"
                )
            ],
            [
                types.KeyboardButton(
                    text="Bosh sahifa"
                )
            ]
        ],
        resize_keyboard=True
    )

    await message.answer(
        text="Admin sahifasi", reply_markup=button
    )


@router.message(IsBotAdminFilter(ADMINS), F.text == "Foydalanuvchilar soni")
async def get_users_count(message: types.Message):
    users_count = await db.count_users()
    await message.answer(f"Bazada {users_count} ta foydalanuvchi bor")


@router.message(IsBotAdminFilter(ADMINS), F.text == "Delete (except today)")
async def delete_except_today(message: types.Message):
    await db.delete_old_links()
    await message.answer("Bugungi sanadan oldingi barcha foydalanuvchilar ma'lumotlari o'chirildi!")


@router.message(IsBotAdminFilter(ADMINS), F.text == "Delete blockers")
async def delete_blockers_from_db(message: types.Message):
    await db.delete_blockers()
    users_count = await db.count_users()
    await message.answer(f"Botni block qilgan foydalanuvchilar ma'lumotlari o'chirildi!\n\n"
                         f"Bazada {users_count} ta foydalanuvchi bor")


@router.message(IsBotAdminFilter(ADMINS), F.text == "Reklama yuborish")
async def ask_ad_content(message: types.Message, state: FSMContext):
    await message.answer("Reklama uchun post yuboring")
    await state.set_state(AdminState.ask_ad_content)


@router.message(AdminState.ask_ad_content, IsBotAdminFilter(ADMINS))
async def send_ad_to_users(message: types.Message, state: FSMContext):
    users = await db.select_all_users()
    count = 0
    for user in users:
        user_id = user[-1]
        try:
            await message.send_copy(chat_id=user_id)
            count += 1
            await asyncio.sleep(0.05)
            if count == 1500:
                await asyncio.sleep(30)
        except Exception as error:
            logging.info(f"Ad did not send to user: {user_id}. Error: {error}")
            await db.update_status_false(
                telegram_id=user_id
            )
    await message.answer(text=f"Reklama {count} ta foydalanuvchiga muvaffaqiyatli yuborildi")
    await state.clear()


@router.message(IsBotAdminFilter(ADMINS), F.text == "Bosh sahifa")
async def main_page(message: types.Message, state: FSMContext):
    await state.clear()
    await welcome_message(message=message)
