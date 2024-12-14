import asyncpg
from aiogram import Router, types
from aiogram.filters import CommandStart, CommandObject

from aiogram.utils.keyboard import InlineKeyboardBuilder

from loader import db, bot
from data.config import PRIVATE_CHANNEL, CHANNELS

router = Router()


async def welcome_message(message: types.Message):
    builder = InlineKeyboardBuilder()

    get_fullname = (await bot.get_chat(chat_id=CHANNELS)).full_name
    get_username = (await bot.get_chat(chat_id=CHANNELS)).username
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
        else:
            try:

                await db.add_members(
                    inviter=inviter, new_member=new_member, invite_count=1
                )
                count_inviter = await db.count_members(inviter=inviter)
                friend_fullname = (await bot.get_chat(chat_id=inviter)).full_name
                await bot.send_message(
                    chat_id=inviter, text=f"🎉 Tabriklaymiz, {message.from_user.full_name} do’stingiz {friend_fullname}"
                                          f" Sizning unikal taklif havolangiz orqali botimizga qo’shildi.\n\n🎁Aytilgan "
                                          f"Bonus sovg'alarni olishingiz uchun yana {5 - count_inviter} ta do’stingizni "
                                          f"taklif qilishingiz lozim.\n\nBonuslar sizni kutmoqda...."
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
        await welcome_message(message=message)
    try:
        await db.add_user(
            telegram_id=message.from_user.id
        )
    except asyncpg.exceptions.UniqueViolationError:
        pass
