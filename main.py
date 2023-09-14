import logging
import time
from decouple import config
import aiohttp
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

from Amplitude import send_registration_event_to_amplitude

from helper_db import save_user_data, create_users_table, user_exists
from message_templates import message_templates

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config("BOT_TOKEN"))
dp = Dispatcher(bot)


messages = {}
gpt = ""
user_languages = {}  # Keep track of user's current language


@dp.callback_query_handler(lambda c: c.data in ["en", "ru"])
async def process_callback(callback_query: types.CallbackQuery):
    user_languages[callback_query.from_user.id] = callback_query.data
    await send_message(callback_query.from_user.id, "language_confirmation")
    await bot.answer_callback_query(callback_query.id)


# Create language selection keyboard
language_keyboard = InlineKeyboardMarkup(row_width=2)
language_keyboard.add(
    InlineKeyboardButton("English🇬🇧", callback_data="en"),
    InlineKeyboardButton("Русский🇷🇺", callback_data="ru"),
)
# Create a keyboard object with a button
webapp_keyboard = types.ReplyKeyboardMarkup()
webapp_keyboard.add(
    types.KeyboardButton(
        text="Выбор персонажа",
        web_app=WebAppInfo(url="https://chafstels.github.io/AI_models_telegramBot/"),
    )
)


async def send_message(user_id, message_key):
    language = user_languages.get(user_id, "ru")  # Default to English
    message_template = message_templates[language][message_key]
    await bot.send_message(user_id, message_template)


@dp.message_handler(commands=["language"])
async def language_cmd(message: types.Message):
    await bot.send_message(
        message.chat.id,
        message_templates["ru"]["language_selection"],
        reply_markup=language_keyboard,
    )


@dp.callback_query_handler(lambda c: c.data in ["en", "ru"])
async def process_callback(callback_query: types.CallbackQuery):
    user_languages[callback_query.from_user.id] = callback_query.data
    await bot.answer_callback_query(callback_query.id)


@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    try:
        username = message.from_user.username
        user_id = message.from_user.id
        messages[username] = []
        language = user_languages.get(
            message.from_user.id, "ru"
        )  # Get the selected language
        await message.reply(
            message_templates[language]["start"],
            reply_markup=webapp_keyboard,
        )  # Retrieve the correct message based on the language

        # Отправляем событие регистрации в Amplitude для нового пользователя
        send_registration_event_to_amplitude(message.from_user.id, "Sign up")

        # Сохраняем данные о пользователе в базе данных
        if not user_exists(user_id):
            save_user_data(
                user_id=message.from_user.id,
                username=message.from_user.username,
                name=message.from_user.first_name,
                surname=message.from_user.last_name,
            )
    except Exception as e:
        logging.error(f"Error in start_cmd: {e}")


@dp.message_handler(commands=["newtopic"])
async def new_topic_cmd(message: types.Message):
    try:
        userid = message.from_user.id
        messages[str(userid)] = []
        language = user_languages.get(message.from_user.id, "ru")
        await message.reply(message_templates[language]["newtopic"])
    except Exception as e:
        logging.error(f"Error in new_topic_cmd: {e}")


@dp.message_handler(commands=["help"])
async def help_cmd(message: types.Message):
    language = user_languages.get(message.from_user.id, "ru")
    await message.reply(message_templates[language]["help"])


@dp.message_handler(commands=["about"])
async def about_cmd(message: types.Message):
    language = user_languages.get(message.from_user.id, "ru")
    await message.reply(message_templates[language]["about"])


@dp.message_handler(content_types=["web_app_data"])
async def web_app(message: types.Message):
    global gpt
    gpt = message.web_app_data.data
    if gpt == "mario_gpt":
        event = "Pick Mario"
    else:
        event = "Pick Albert"
    send_registration_event_to_amplitude(message.from_user.id, event)
    await message.answer(message.web_app_data.data)


@dp.message_handler()
async def echo_msg(message: types.Message):
    try:
        user_message = message.text
        userid = message.from_user.username

        if userid not in messages:
            messages[userid] = []
        messages[userid].append({"role": "user", "content": user_message})
        messages[userid].append(
            {
                "role": "user",
                "content": f"chat: {message.chat} Now {time.strftime('%d/%m/%Y %H:%M:%S')} user: {message.from_user.first_name} message: {message.text}",
            }
        )
        logging.info(f"{userid}: {user_message}")

        should_respond = (
            not message.reply_to_message
            or message.reply_to_message.from_user.id == bot.id
        )

        if should_respond:
            language = user_languages.get(message.from_user.id, "ru")
            processing_message = await message.reply(
                message_templates[language]["processing"]
            )

            await bot.send_chat_action(chat_id=message.chat.id, action="typing")

            # Сформируйте данные для отправки на ваш ендпоинт
            messages_to_send = {
                "model": "gpt-3.5-turbo",
                "messages": messages[userid],
                "prompt": message_templates[language]["mario_gpt"],
            }

            headers = {"accept": "application/json", "Content-Type": "application/json"}
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    config("ENDPOINT"),
                    headers=headers,
                    json=messages_to_send,
                ) as response:
                    response_data = await response.json()
                    chatgpt_response = response_data["choices"][0]["message"]["content"]

            messages[userid].append({"role": "assistant", "content": chatgpt_response})
            logging.info(f"ChatGPT response: {chatgpt_response}")

            await message.reply(chatgpt_response)

            await bot.delete_message(
                chat_id=processing_message.chat.id,
                message_id=processing_message.message_id,
            )

    except Exception as ex:
        if ex == "context_length_exceeded":
            language = user_languages.get(message.from_user.id, "ru")
            await message.reply(message_templates[language]["error"])
            await new_topic_cmd(message)
            await echo_msg(message)


if __name__ == "__main__":
    create_users_table()
    executor.start_polling(dp)
