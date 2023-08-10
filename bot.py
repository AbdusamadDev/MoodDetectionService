from aiogram import types, executor, Dispatcher, Bot
import logging
import asyncio
from datetime import datetime
import os
import psycopg2
import dotenv

from xlsx import make_xlsx

dotenv.load_dotenv()
logging.basicConfig(level=logging.INFO)
bot = Bot(token=os.environ.get("token"))
disp = Dispatcher(bot)

# time catch, query filter date unit, 
async def retrieve(chat_id, _time_catch, date_unit, strf):
    connection = psycopg2.connect(
        user=os.environ.get("user"), 
        password=os.environ.get("password"), 
        database=os.environ.get("database"), 
        port=os.environ.get("port"), 
        host=os.environ.get("host")
    )
    cursor = connection.cursor()
    already_sent = False
    while True:
        now = datetime.now()
        time_catch = now.strftime("%H:%M:%S")
        if time_catch == _time_catch and not already_sent:
            cursor.execute(
                f'SELECT * FROM "stats_generalstatistics" WHERE "{date_unit}"=%s' %
                (str(int(now.strftime(strf)) - 1),)
            )
            query = cursor.fetchall()
            file_content = make_xlsx(query)

            await bot.send_document(chat_id, document=file_content)
            already_sent = True
        elif time_catch != _time_catch:
            already_sent = False
            await bot.send_message(chat_id, time_catch)
        await asyncio.sleep(1)


@disp.message_handler(commands=["start", "help"])
async def init(message: types.Message):
    await message.answer(
        f"Hi {message.from_user.username}, Fetching database every week process initiated successfully!"
    )
    await retrieve(chat_id=message.chat.id, _time_catch="07:40:00", date_unit="day", strf="%d")
    # await retrieve(chat_id=message.chat.id, _time_catch="07:40:05", date_unit="week", strf="%U")
    # await retrieve(chat_id=message.chat.id, _time_catch="07:40:10", date_unit="month", strf="%m")

executor.start_polling(disp, skip_updates=True)
