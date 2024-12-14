from aiogram import Router, types, F
from aiogram.utils.deep_linking import create_start_link

from data.config import CHANNELS
from loader import bot

router = Router()


@router.callback_query(F.data == "subscribed")
async def subscribe_callback(call: types.CallbackQuery):
    user_status = (await bot.get_chat_member(chat_id=CHANNELS, user_id=call.from_user.id)).status
    await bot.send_message(
        chat_id=call.from_user.id, text=user_status
    )
    if user_status == 'left' or 'kicked':
        bot_fullname = (await bot.get_chat(chat_id=CHANNELS)).full_name
        await call.answer(
            text=f"Siz {bot_fullname} kanaliga a'zo bo'lmagansiz!", show_alert=True
        )
    else:
        link = await create_start_link(bot=bot, payload=str(call.from_user.id))
        send_link_ = f"\n\nQuyidagi havola orqali botga a'zo bo'ling:\n\n{link}"
        markup = types.InlineKeyboardMarkup(inline_keyboard=[[
            types.InlineKeyboardButton(text="Yuborish", switch_inline_query=send_link_)

        ]]
        )
        await call.message.edit_text(text=f"So'nggi qadam!\n\nKitobimizni qo'lga kiritish uchun Kimyo-Biologiya "
                                          f"o'qiydigan 5ta do'stingizni taklif qiling.\n\n"
                                          f"Kitobni yopiq kanalga joyladik takliflar soni 5ta bo'lganda Siz ushbu "
                                          f"kanalga havola(link) olasiz.",
                                     reply_markup=markup)
