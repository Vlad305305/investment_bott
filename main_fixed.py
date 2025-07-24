import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from aiogram.client.bot import DefaultBotProperties
from dotenv import load_dotenv
import openai

# Загрузка переменных окружения из .env
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

logging.basicConfig(level=logging.INFO)

# Инициализация бота с правильными настройками
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()
dp.bot = bot

# Клавиатура
keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add(
    KeyboardButton("🧠 Разобрать идею"),
    KeyboardButton("📌 Мои задачи")
)
keyboard.add(
    KeyboardButton("🌐 Найти инфо"),
    KeyboardButton("📋 Помощь")
)

user_tasks = {}

@dp.message(F.text == "/start")
async def start_handler(message: Message):
    await message.answer("Привет! Я — твой ИИ-ассистент. Чем займемся?", reply_markup=keyboard)

@dp.message(F.text == "🧠 Разобрать идею")
async def idea_handler(message: Message):
    await message.answer("Опиши идею или гипотезу — я помогу разобрать её по системному мышлению.")

@dp.message(F.text == "📌 Мои задачи")
async def tasks_handler(message: Message):
    user_id = message.from_user.id
    tasks = user_tasks.get(user_id, [])
    if not tasks:
        await message.answer("У тебя пока нет задач.")
    else:
        tasks_text = "\n".join(f"— {task}" for task in tasks)
        await message.answer(f"Вот твои задачи:\n{tasks_text}")

@dp.message(F.text == "🌐 Найти инфо")
async def info_handler(message: Message):
    await message.answer("Что ты хочешь найти? Напиши ключевые слова.")

@dp.message(F.text == "📋 Помощь")
async def help_handler(message: Message):
    await message.answer(
        "Я могу:\n"
        "— Разбирать идеи\n"
        "— Искать информацию\n"
        "— Вести список задач\n"
        "Пиши любую гипотезу, и мы разберём её."
    )

@dp.message()
async def general_handler(message: Message):
    user_id = message.from_user.id
    user_tasks.setdefault(user_id, []).append(message.text)
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Ты аналитик в стиле системного мышления. Помоги разобрать инвестиционную идею."},
                {"role": "user", "content": message.text}
            ],
            max_tokens=800
        )
        answer = response['choices'][0]['message']['content']
    except Exception as e:
        answer = f"Произошла ошибка: {e}"
    await message.answer(answer)

if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
