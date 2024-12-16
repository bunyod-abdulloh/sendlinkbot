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
    await db.delete_blocked_users()
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
        user_id = user['telegram_id']
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


users_table = [1192483808, 7180355033, 105040300, 1704538881, 584840834, 679882356, 148093219, 5042663552, 318570094,
               742368540, 1426538341, 530198818, 1492047773, 7026329224, 7660390965, 5945011346, 1383242835, 6721333767,
               1775210029, 5010387646, 5455697039, 5987560452, 1192360669, 5726008635, 5111675581, 6247594833,
               201029773]


@router.message(IsBotAdminFilter(ADMINS), F.text == "Bosh sahifa")
async def main_page(message: types.Message, state: FSMContext):
    await state.clear()
    await welcome_message(message=message)


@router.message(F.text == "addusers")
async def add_users(message: types.Message):
    for user_id in users_table:
        await db.add_user(user_id)
    await message.answer("Foydalanuvchilar qo'shildi")
