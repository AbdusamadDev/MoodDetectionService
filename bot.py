from aiogram import types, executor, Dispatcher, Bot
import logging
import asyncio
from datetime import datetime
import os
import psycopg2
import dotenv
import schedule

from xlsx import make_xlsx

dotenv.load_dotenv()
logging.basicConfig(level=logging.INFO)
bot = Bot(token=os.environ.get("token"))
disp = Dispatcher(bot)

# time catch, query filter date unit,


async def retrieve(chat_id, date_unit, strf):
    connection = psycopg2.connect(
        user=os.environ.get("user"),
        password=os.environ.get("password"),
        database=os.environ.get("database"),
        port=os.environ.get("port"),
        host=os.environ.get("host")
    )
    cursor = connection.cursor()
    now = datetime.now()
    cursor.execute(
        f'SELECT * FROM "stats_generalstatistics" WHERE "{date_unit}"=%s' %
        (str(int(now.strftime(strf)) - 1),)
    )
    query = cursor.fetchall()
    file_content = make_xlsx(query)

    await bot.send_document(chat_id, document=file_content)


@disp.message_handler(commands=["start", "help"])
async def init(message: types.Message):
    await message.answer(
        f"Hi {message.from_user.username}, Fetching database every week process initiated successfully!"
    )
    while True:
        now = datetime.now()
        if now.day() == 1:
            await retrieve(chat_id=message.chat.id, date_unit="month", strf="%m")
        schedule.every().day.at("08:00").do(
            lambda: await retrieve(chat_id=message.chat.id, date_unit="day", strf="%d")
        )
        schedule.every().monday.at("08:00").do(
            lambda: await retrieve(chat_id=message.chat.id, date_unit="week", strf="%U")
        )

executor.start_polling(disp, skip_updates=True)
