import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from aiogram.enums import ParseMode
from aiogram.client.bot import DefaultBotProperties
from aiogram import F
from dotenv import load_dotenv
import openai
import asyncio

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY
logging.basicConfig(level=logging.INFO)

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()
dp.bot = bot

buttons = [
    [KeyboardButton(text="🧠 Разобрать идею"), KeyboardButton(text="📌 Мои задачи")],
    [KeyboardButton(text="🌐 Найти инфо"), KeyboardButton(text="📋 Помощь")]
]

main_keyboard = ReplyKeyboardMarkup(
    keyboard=buttons,
    resize_keyboard=True
)

user_tasks = {}

@dp.message(F.text == "/start")
async def send_welcome(message: Message):
    await message.reply("Привет! Я — твой ИИ-ассистент. Чем займемся?", reply_markup=main_keyboard)

@dp.message(F.text == "🧠 Разобрать идею")
async def analyze_idea(message: Message):
    await message.reply("Опиши идею или гипотезу — я помогу разобрать её по системному мышлению.")

@dp.message(F.text == "📌 Мои задачи")
async def show_tasks(message: Message):
    user_id = message.from_user.id
    tasks = user_tasks.get(user_id, [])
    if not tasks:
        await message.reply("У тебя пока нет задач.")
    else:
        task_list = "\n".join(f"— {task}" for task in tasks)
        await message.reply(f"Вот твои задачи:\n{task_list}")

@dp.message(F.text == "🌐 Найти инфо")
async def ask_web(message: Message):
    await message.reply("Что ты хочешь найти? Напиши ключевые слова.")

@dp.message(F.text == "📋 Помощь")
async def help_menu(message: Message):
    await message.reply("Я могу:\n— Разбирать идеи\n— Искать информацию\n— Вести список задач\nПиши любую гипотезу, и мы разберём её.")

@dp.message()
async def handle_general(message: Message):
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
    await message.reply(answer)

if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
