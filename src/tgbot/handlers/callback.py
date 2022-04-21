from aiogram import Dispatcher
from aiogram.types import CallbackQuery

from spbu_api import StudyDivisionsApi
from tgbot.handlers.user import user_start
from tgbot.keyboards import InlineKeyboardPaginator, get_programs_keyboard
from tgbot.misc.pagination_functions import count_pages, fill_paginator


async def send_divisions(query: CallbackQuery):
    page = int(query.data.split("#")[1])

    division_api = StudyDivisionsApi()
    divisions = await division_api.get_all()

    page_count = count_pages(divisions)

    paginator = InlineKeyboardPaginator(
        page_count=page_count, current_page=page,
        data_pattern='division_pages#{page}'
    )

    paginator = fill_paginator(
        data=divisions, data_field="name",
        callback_data_prefix="division", callback_data_field="alias",
        previous_keyboard_callback="start", paginator=paginator)

    await query.bot.send_message(
        query.from_user.id, f"Подразделения: {page}",
        reply_markup=paginator.markup
    )
    await query.bot.delete_message(
        query.message.chat.id, query.message.message_id
    )


async def start_with_callback(query: CallbackQuery):
    await user_start(query.message)


async def programs_from_division(query: CallbackQuery):
    _, division_alias = query.data.split(":")
    keyboard = await get_programs_keyboard(division_alias)
    await query.bot.send_message(query.from_user.id, division_alias, reply_markup=keyboard)
    await query.bot.delete_message(query.message.chat.id, query.message.message_id)


def register_callbacks(dp: Dispatcher):
    dp.register_callback_query_handler(
        programs_from_division, lambda query: "program_pages" in query.data, state="*")
    dp.register_callback_query_handler(
        start_with_callback, lambda query: "start" in query.data, state="*")
    dp.register_callback_query_handler(
        send_divisions, lambda query: "division_pages" in query.data,
        state="*"
    )