from datetime import datetime, timedelta

import asyncpg
from aiogram import Router, types, F
from aiogram.filters import CommandStart, CommandObject
from aiogram.utils.deep_linking import create_start_link

from aiogram.utils.keyboard import InlineKeyboardBuilder

from loader import db, bot
from data.config import PRIVATE_CHANNEL, CHANNEL

router = Router()


async def invite_button(user_id):
    link = await create_start_link(bot=bot, payload=str(user_id))
    send_link_ = (f"📚 Qiymati 2000$ bo'lgan Milliy Sertifikat kitobini olish uchun quyidagi havola orqali botga a'zo "
                  f"bo'ling:\n\n{link}")
    markup = types.InlineKeyboardMarkup(inline_keyboard=[[
        types.InlineKeyboardButton(text="Yuborish", switch_inline_query=send_link_)

    ]]
    )
    return markup


async def welcome_message(message: types.Message):
    builder = InlineKeyboardBuilder()

    get_fullname = (await bot.get_chat(chat_id=CHANNEL)).full_name
    get_username = (await bot.get_chat(chat_id=CHANNEL)).username
    builder.add(types.InlineKeyboardButton(text=f"{get_fullname}",
                                           url=f"https://t.me/{get_username}"))
    builder.add(types.InlineKeyboardButton(text="✅ A'zo bo'ldim!", callback_data="subscribed"))
    builder.adjust(1)

    await message.answer(
        text="🎉 Tabriklaymiz 🎉\n\nSiz birinchi qadamni bosdingiz! Davom etish uchun yagona bo'lgan kanalimizga a'zo "
             "bo'ling.\n\nKeyin \"✅ А'zo bo'ldim!\" tugmasini bosing", reply_markup=builder.as_markup())


@router.message(CommandStart())
async def do_start(message: types.Message, command: CommandObject):
    if command.args:
        inviter = int(command.args)
        new_member = message.from_user.id
        count_inviter = await db.count_members(inviter=inviter)

        if count_inviter == 4:
            # expire_time = datetime.now() + timedelta(minutes=10)
            invite_link = (await bot.create_chat_invite_link(chat_id=PRIVATE_CHANNEL, member_limit=1)).invite_link
            markup = types.InlineKeyboardMarkup(inline_keyboard=[[
                types.InlineKeyboardButton(text="Kanalga qo'shilish", url=invite_link)
            ]])
            await bot.send_message(
                chat_id=inviter,
                text=f"Tabriklaymiz Siz ushbu sovg'ani olishga haqli deb topildingiz\n\n"
                     f"Quyidagi tugma orqali yopiq kanalga qo'shilib olishingiz mumkin",
                reply_markup=markup, protect_content=True
            )
            await welcome_message(message=message)
            try:
                await db.add_user(telegram_id=inviter)
                await db.add_user(telegram_id=message.from_user.id)
                await db.add_members(
                    inviter=inviter, new_member=new_member, invite_count=1
                )
            except asyncpg.exceptions.UniqueViolationError:
                pass

        elif count_inviter > 4:
            await welcome_message(message=message)
        else:
            try:
                await db.add_members(
                    inviter=inviter, new_member=new_member, invite_count=1
                )
                friend_fullname = (await bot.get_chat(chat_id=inviter)).full_name
                await bot.send_message(
                    chat_id=inviter,
                    text=f"🎉 Tabriklaymiz, {friend_fullname} do’stingiz {message.from_user.full_name}"
                         f" Sizning unikal taklif havolangiz orqali botimizga qo’shildi.\n\n🎁Aytilgan "
                         f"Bonus sovg'alarni olishingiz uchun yana {4 - count_inviter} ta do’stingizni "
                         f"taklif qilishingiz lozim.\n\nBonuslar Sizni kutmoqda....\n\nQuyidagi tugma orqali taklif "
                         f"havolasini yuborishingiz mumkin",
                    reply_markup=await invite_button(user_id=inviter)
                )
                await welcome_message(message=message)
            except asyncpg.exceptions.UniqueViolationError:
                try:
                    await message.answer(
                        text="Siz bot uchun ro'yxatdan o'tgansiz!"
                    )
                    await bot.send_message(
                        chat_id=inviter,
                        text=f"Foydalanuvchi {message.from_user.full_name} bot uchun avval ro'yxatdan o'tgan!\n\n"
                             f"Iltimos, boshqa foydalanuvchi taklif qiling!"
                    )
                except:
                    pass
    else:
        await db.add_user(telegram_id=message.from_user.id)
        await welcome_message(message=message)
