"""
Telegram Bot для отправки игры Bomberman (Cyber Bomber).
Поддерживает три режима:
1. Отправка автономного HTML-файла для Telegram 13.2 (HTMLBubbles / Интерактивный баббл).
2. Запуск через Telegram WebApp (кнопка в чате / инлайн-кнопка).
3. Инлайн-режим (Inline Query) — возможность делиться игрой в любых чатах и группах (@ИмяБота).
"""

import os
import sys
import asyncio
from pathlib import Path

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    FSInputFile,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo,
    InlineQueryResultArticle,
    InputTextMessageContent
)

# Токен вашего бота от @BotFather (можно передать в BOT_TOKEN в переменных окружения)
BOT_TOKEN = os.getenv("BOT_TOKEN", "9020300503:AAFxQka3X3BhsgeWeg_hv4DFVsdhhVc6TT0")

# Путь к файлу игры
GAME_HTML_PATH = Path(__file__).parent / "index.html"

# Если вы хотите запускать игру через WebApp по ссылке (например GitHub Pages или свой домен):
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://abdulmutalib07.github.io/Bomberman_tg/")

dp = Dispatcher()


@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    """Приветственное сообщение с выбором режима запуска игры."""
    kb_buttons = [
        [
            InlineKeyboardButton(
                text="📥 Отправить как HTMLBubble (сообщение)",
                callback_data="send_bubble"
            )
        ]
    ]

    # Если указан URL для WebApp, добавляем кнопку WebApp
    if WEBAPP_URL:
        kb_buttons.append([
            InlineKeyboardButton(
                text="🎮 Играть в WebApp",
                web_app=WebAppInfo(url=WEBAPP_URL)
            )
        ])

    keyboard = InlineKeyboardMarkup(inline_keyboard=kb_buttons)

    text = (
        "💣 <b>Добро пожаловать в Cyber Bomber!</b>\n\n"
        "Эта игра разработана специально для интерактивных сообщений "
        "Telegram (HTMLBubbles) и весит меньше 32 КБ.\n\n"
        "• Нажмите кнопку ниже, чтобы получить интерактивный HTML-баббл прямо в диалог!\n"
        "• Либо введите команду /play.\n"
        "• Также вы можете вызвать бота инлайн: напишите <code>@юзернейм_бота</code> в любом чате!"
    )
    await message.answer(text, parse_mode="HTML", reply_markup=keyboard)


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    text = (
        "🕹 <b>Управление в Cyber Bomber:</b>\n\n"
        "📱 <b>На телефоне:</b> экранный D-Pad для ходьбы + большая кнопка 💣 для сброса плазмы.\n"
        "💻 <b>На компьютере:</b> WASD или стрелки для ходьбы, Пробел / Enter / E для сброса бомбы.\n\n"
        "⭐ <b>Бонусы в блоках:</b>\n"
        "• 💣 — +1 к запасу бомб (до 5 одновременно)\n"
        "• 🔥 — +1 к радиусу плазменного взрыва\n"
        "• ⚡ — увеличение скорости перемещения\n"
        "• 🛡️ — энергощит (поглощает 1 удар врага или взрыв)"
    )
    await message.answer(text, parse_mode="HTML")


@dp.message(Command("play"))
@dp.callback_query(F.data == "send_bubble")
async def send_bubble_game(event: types.Message | types.CallbackQuery):
    """
    Отправляет standalone HTML-файл с игрой.
    В клиентах Telegram 13.2+ с поддержкой HTMLBubbles файл открывается
    и запускается прямо внутри пузыря сообщения.
    """
    if isinstance(event, types.CallbackQuery):
        message = event.message
        await event.answer()
    else:
        message = event

    if not GAME_HTML_PATH.exists():
        await message.answer("❌ Файл index.html не найден!")
        return

    file = FSInputFile(
        path=GAME_HTML_PATH,
        filename="cyber_bomber.html"
    )

    caption = (
        "🎮 <b>Cyber Bomber (v1.0)</b>\n"
        "⚡ <i>32 KB Standalone HTMLBubble Game</i>\n\n"
        "В клиентах Telegram с поддержкой HTMLBubbles игра запускается прямо внутри чата!"
    )

    await message.answer_document(
        document=file,
        caption=caption,
        parse_mode="HTML"
    )


@dp.inline_query()
async def inline_game(inline_query: types.InlineQuery):
    """Позволяет делиться игрой в любых группах или диалогах через инлайн."""
    bot_info = await inline_query.bot.get_me()

    button = (
        InlineKeyboardButton(text="🎮 Играть в WebApp", web_app=WebAppInfo(url=WEBAPP_URL))
        if WEBAPP_URL
        else InlineKeyboardButton(text="💣 Запустить в боте", url=f"https://t.me/{bot_info.username}?start=play")
    )

    results = [
        InlineQueryResultArticle(
            id="bomber_game_share",
            title="💣 Сыграть в Cyber Bomber",
            description="Запустить киберпанк Bomberman прямо в Telegram (<32 KB)",
            input_message_content=InputTextMessageContent(
                message_text=(
                    "🎮 <b>Cyber Bomber в Telegram!</b>\n\n"
                    "Уничтожайте защитные барьеры, собирайте бонусы и зачищайте секторы от дронов.\n"
                    "Нажмите кнопку ниже, чтобы начать игру!"
                ),
                parse_mode="HTML"
            ),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[button]])
        )
    ]
    await inline_query.answer(results, cache_time=5)


async def main():
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("=" * 60)
        print("ВНИМАНИЕ: Укажите токен бота перед запуском!")
        print("Экспортируйте переменную окружения:")
        print("  export BOT_TOKEN='ваш_токен_от_BotFather'")
        print("Или отредактируйте переменную BOT_TOKEN в файле bot.py")
        print("=" * 60)
        sys.exit(1)

    bot = Bot(token=BOT_TOKEN)
    print("🤖 Бот запущен! Ожидание сообщений в Telegram...")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
