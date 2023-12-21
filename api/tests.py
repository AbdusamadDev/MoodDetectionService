# import requests
# import sqlite3
# import random
# import string
# import time

# def generate():
#     alphabet = "abcdefghijklmnopqrstuvxyz"
#     return ''.join(random.choice(alphabet) for i in range(13))

# def create_mood(conn):
#     cursor = conn.cursor()
#     cursor.execute(
#         """INSERT INTO api_mood (jahldorlik, behuzur, xavotir, hursandchilik, gamgin, xayron, neytral) VALUES (?, ?, ?, ?, ?, ?, ?)""",
#         (generate(), generate(), generate(), generate(), generate(), generate(), generate())
#     )
#     conn.commit()
#     time.sleep(0.1)
#     cursor.execute("SELECT last_insert_rowid()")
#     mood_id = cursor.fetchone()[0]
#     cursor.close()
#     return mood_id

# def create_record(conn, screenshot_url, date_recorded, camera_id, employee_id, mood_id):
#     cursor = conn.cursor()
#     cursor.execute(
#         """INSERT INTO api_records (screenshot, date_recorded, camera_id, employee_id, mood_id) VALUES (?, ?, ?, ?, ?)""",
#         (screenshot_url, date_recorded, camera_id, employee_id, mood_id)
#     )
#     conn.commit()
#     cursor.close()

# def main():
#     conn = sqlite3.connect("../db.sqlite3")
#     try:
#         for i in range(100):
#             mood_id = create_mood(conn)
#             create_record(
#                 conn,
#                 "https://youtube.com/media/main.jpg",
#                 generate(),
#                 2,
#                 1,
#                 mood_id
#             )
#     finally:
#         conn.close()

# if __name__ == "__main__":
#     main()
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.callback_data import CallbackData
from aiogram.dispatcher.filters import BoundFilter
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.utils import executor
import sqlite3
import logging


# user_id = 2003049919
API_TOKEN = "6195275934:AAEngBypgfNw3SwcV9uV_jdatZtMvojF9cs"
option_callback = CallbackData("option", "name")
answer_callback = CallbackData("answer", "id")
faq_callback = CallbackData("faq", "id")
view_questions_callback = CallbackData("admin_action", "action")
view_users_callback = CallbackData("admin_action", "action")
view_faqs_callback = CallbackData("admin_action", "action")
region_callback = CallbackData("region", "name")
storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
logging.basicConfig(level=logging.INFO)
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())
admin_response_state = {}
user_data = {}


def fetch_admin_ids(db_path="../db.sqlite3"):
    """
    Fetches all admin Telegram IDs from the api_customadmin table in the SQLite3 database.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT telegram_id FROM api_customadmin WHERE telegram_id IS NOT NULL"
        )
        admin_ids = [row[0] for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        admin_ids = []
    finally:
        conn.close()

    return admin_ids


class UserIsAdminFilter(BoundFilter):
    key = "user_is_admin"

    def __init__(self, user_is_admin):
        self.user_is_admin = user_is_admin

    async def check(self, message: types.Message):
        user_is_admin = message.from_user.id in fetch_admin_ids()
        return user_is_admin


dp.filters_factory.bind(UserIsAdminFilter)


class Registration(StatesGroup):
    first_name = State()
    phone_number = State()
    region = State()
    manual_region = State()


def fetch_question_text(question_id):
    """
    Fetch the question text from the database using the question ID.
    """
    conn = sqlite3.connect("../db.sqlite3")
    cursor = conn.cursor()
    cursor.execute("SELECT text FROM api_question WHERE id = ?", (question_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


def get_user_telegram_id_from_question(question_id):
    """
    Get the Telegram ID of the user who asked the question.
    """
    conn = sqlite3.connect("../db.sqlite3")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT telegram_id FROM api_user JOIN api_question ON api_user.id = api_question.user_id WHERE api_question.id = ?",
        (question_id,),
    )
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


def save_answer_to_database(question_id, answer, admin_id):
    """
    Save the admin's answer to the `api_answer` table.
    """
    conn = sqlite3.connect("../db.sqlite3")
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO api_answer (question_id, text, admin_id)
        VALUES (?, ?, ?)
        """,
        (question_id, answer, admin_id),
    )
    conn.commit()
    conn.close()


def create_new_question(text, status, category_id, user_id):
    """
    Create a new question in the SQLite3 database.
    """
    conn = sqlite3.connect("../db.sqlite3")
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO api_question (text, status, category_id, user_id)
        VALUES (?, ?, ?, ?)
    """,
        (text, status, category_id, user_id),
    )
    conn.commit()
    conn.close()


def get_user_database_id(telegram_id):
    """
    Retrieve the user's database ID based on their Telegram ID using SQLite.
    """
    conn = sqlite3.connect("../db.sqlite3")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM api_user WHERE telegram_id = ?", (telegram_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    else:
        return None


def fetch_unanswered_questions():
    conn = sqlite3.connect("../db.sqlite3")
    cursor = conn.cursor()
    cursor.execute("SELECT id, text FROM api_question WHERE status = 0")
    questions = cursor.fetchall()
    conn.close()
    return questions


def fetch_categories():
    """
    Fetch all categories from the database.
    """
    conn = sqlite3.connect("../db.sqlite3")
    cursor = conn.cursor()
    cursor.execute("SELECT title FROM api_category")
    categories = cursor.fetchall()
    conn.close()
    return [category[0] for category in categories]


def add_user_to_database(user_data):
    """
    Adds a user to the database using the provided user data.
    """
    conn = sqlite3.connect("../db.sqlite3")
    cursor = conn.cursor()
    fullname = user_data["first_name"]
    phone_number = user_data["phone_number"]
    region = user_data["region"]
    if not region:
        region = user_data["manual_region"]
    telegram_id = user_data["telegram_id"]
    telegram_username = user_data.get("telegram_username", "")
    cursor.execute(
        """
        INSERT INTO api_user (fullname, phone_number, region, telegram_id, telegram_username) 
        VALUES (?, ?, ?, ?, ?)
    """,
        (fullname, phone_number, region, telegram_id, telegram_username),
    )
    conn.commit()
    conn.close()


def fetch_regions():
    """
    Fetch all regions from the database.
    """
    conn = sqlite3.connect("../db.sqlite3")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM api_regions")
    regions = cursor.fetchall()
    conn.close()
    return [region[0] for region in regions]


def is_user_in_database(telegram_id):
    conn = sqlite3.connect("../db.sqlite3")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM api_user WHERE telegram_id = ?", (telegram_id,))
    user = cursor.fetchone()
    conn.close()
    return user is not None


def fetch_faqs():
    """
    Fetch all FAQ entries from the database.
    """
    conn = sqlite3.connect("../db.sqlite3")
    cursor = conn.cursor()
    cursor.execute("SELECT id, question FROM api_faq")
    faqs = cursor.fetchall()
    conn.close()
    return faqs


def fetch_faq_answer(faq_id):
    """
    Fetch the answer for a specific FAQ from the database.
    """
    conn = sqlite3.connect("../db.sqlite3")
    cursor = conn.cursor()
    cursor.execute("SELECT answer FROM api_faq WHERE id = ?", (faq_id,))
    answer = cursor.fetchone()
    conn.close()
    return answer[0] if answer else "No answer found."


def waiting_for_admin_response_condition(message: types.Message):
    user_id = message.from_user.id
    return admin_response_state.get(user_id, {}).get("awaiting_response", False)


# ------------------------- USER POSSIBLE ACTIONS ---------------------------
@dp.callback_query_handler(option_callback.filter(name="FAQ"))
async def process_faq_option(query: types.CallbackQuery):
    await bot.delete_message(query.message.chat.id, query.message.message_id)
    await display_faq_pages(query.message)
    await query.answer()


@dp.callback_query_handler(faq_callback.filter())
async def process_faq_answer(query: types.CallbackQuery, callback_data: dict):
    faq_id = int(callback_data["id"])
    answer = fetch_faq_answer(faq_id)
    await query.message.reply(answer)
    await query.answer()


async def present_options(message: types.Message):
    inline_kb = InlineKeyboardMarkup(row_width=3)
    inline_kb.add(
        InlineKeyboardButton(
            "ℹ️ FAQ - Ko'p beriladigan savollar",
            callback_data=option_callback.new(name="FAQ"),
        )
    )
    inline_kb.add(
        InlineKeyboardButton(
            "ℹ️ Yo'nalishlarni korish",
            callback_data=option_callback.new(name="Categories"),
        )
    )
    await message.reply(
        "✅ Ro'yxatdan o'tdingiz, iltimos quyidalardan birini tanglang:",
        reply_markup=inline_kb,
    )


@dp.message_handler(state=Registration.manual_region)
async def process_manual_region(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["region"] = message.text
        data["telegram_id"] = message.from_user.id
        data["telegram_username"] = message.from_user.username
        add_user_to_database(data)
    await state.finish()
    user_data[message.from_user.id] = {"awaiting_question": True}
    await present_options(message)


@dp.message_handler(commands=["start"], state=None)
async def process_start_command(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id in fetch_admin_ids():
        inline_kb = InlineKeyboardMarkup(row_width=1)
        inline_kb.add(
            InlineKeyboardButton(
                "Murojaatlarni ko'rish",
                callback_data=view_questions_callback.new(action="view_questions"),
            ),
            # InlineKeyboardButton(
            #     "Murojaatchilarni ko'rish",
            #     callback_data=view_users_callback.new(action="view_users"),
            # ),
            # InlineKeyboardButton(
            #     "FAQ ni ko'rish",
            #     callback_data=view_faqs_callback.new(action="view_faqs"),
            # ),
        )
        await message.reply(
            "Assalomu alaykum admin, hush kelibsiz!", reply_markup=inline_kb
        )
    elif is_user_in_database(user_id):
        inline_kb = InlineKeyboardMarkup(row_width=3)
        inline_kb.add(
            InlineKeyboardButton(
                "ℹ️ FAQ - Ko'p beriladigan savollar",
                callback_data=option_callback.new(name="FAQ"),
            )
        )
        inline_kb.add(
            InlineKeyboardButton(
                "ℹ️ Yo'nalishlarni korish",
                callback_data=option_callback.new(name="Categories"),
            )
        )
        await message.reply(
            "Assalomu alaykum, bugun qanday murojaatlaringiz bor?",
            reply_markup=inline_kb,
        )
    else:
        await Registration.first_name.set()
        await message.reply("Hi!\nIsmingizni kiriting:")


@dp.message_handler(state=Registration.first_name)
async def process_first_name(message: types.Message, state: FSMContext):
    if len(message.text.split(" ")) not in [3, 4]:
        await message.reply(
            "🚫 Iltimos, to'liq ismingiz, familiyangiz va otaliq ismingizni to'g'ri kiriting! \nMasalan: Anvar Anvarov Anvarovich/Anvar o'g'li"
        )
    else:
        async with state.proxy() as data:
            data["first_name"] = message.text
        await Registration.next()
        await message.reply("Telefon raqamingizni kiriting:\nMasalan +998991234567")


# Pagination callback data for FAQs
faq_pagination_callback = CallbackData("faq_paginate", "page")


# Helper function to chunk the FAQ list into pages
def chunked_faqs_list(faqs, items_per_page):
    for i in range(0, len(faqs), items_per_page):
        yield faqs[i : i + items_per_page]


async def display_faq_pages(message: types.Message, page=0):
    faqs = fetch_faqs()  # Fetch all FAQ entries from the database.
    pages = list(chunked_faqs_list(faqs, 3))  # 3 FAQs per page

    if pages:
        faqs_page = pages[page]
        # Adjust the row_width to 4
        inline_kb = InlineKeyboardMarkup(row_width=4)

        # Message text to include FAQ questions
        message_text = "Murojaatlardan birini tanlang:\n\n" + "\n".join(
            [f"{faq_id}. {question}" for faq_id, question in faqs_page]
        )

        # Add FAQ question buttons
        for faq_id, _ in faqs_page:
            inline_kb.insert(
                InlineKeyboardButton(
                    text=str(faq_id), callback_data=faq_callback.new(id=faq_id)
                )
            )

        # Add navigation buttons
        if page > 0:
            inline_kb.insert(
                InlineKeyboardButton(
                    text="<< avvalgisi",
                    callback_data=faq_pagination_callback.new(page=page - 1),
                )
            )
        if page < len(pages) - 1:
            inline_kb.insert(
                InlineKeyboardButton(
                    text="keyingisi >>",
                    callback_data=faq_pagination_callback.new(page=page + 1),
                )
            )
        # Ensure to send a new message since the original was deleted
        await message.answer(message_text, reply_markup=inline_kb)
    else:
        await message.answer("Hech qanday FAQ yo'q.")


@dp.callback_query_handler(faq_pagination_callback.filter())
async def navigate_faq_pages(query: types.CallbackQuery, callback_data: dict):
    logging.info("navigate_faq_pages called with callback_data: %s", callback_data)
    try:
        page = int(callback_data["page"])
        await bot.delete_message(
            chat_id=query.message.chat.id, message_id=query.message.message_id
        )
        await display_faq_pages(query.message, page=page)
        await query.answer()
    except Exception as e:
        logging.exception("Error in navigate_faq_pages: %s", e)
        await query.answer("An error occurred.")


@dp.message_handler(state=Registration.phone_number)
async def process_phone_number(message: types.Message, state: FSMContext):
    if (
        message.text.startswith("+998")
        and message.text[1:].isdigit()
        and len(message.text[1:]) == 12
    ):
        async with state.proxy() as data:
            data["phone_number"] = message.text
        regions = fetch_regions()
        if len(regions) != 0:
            await Registration.next()
            inline_kb = InlineKeyboardMarkup(row_width=4)
            for region in regions:
                inline_kb.add(
                    InlineKeyboardButton(
                        region, callback_data=region_callback.new(name=region)
                    )
                )
            await message.reply("Turar joyingizni tanlang:", reply_markup=inline_kb)
        else:
            await Registration.manual_region.set()
            await message.reply("Turar joyingizni kiriting:")
    else:
        await message.reply(
            "🚫 Iltimos telefon raqamingizni quyidagi formatda kiriting: +998123456789(101213 agar chet el nomer bolsa)."
        )


@dp.callback_query_handler(region_callback.filter(), state=Registration.region)
async def process_region_selection(
    query: types.CallbackQuery, callback_data: dict, state: FSMContext
):
    region = callback_data["name"]
    async with state.proxy() as data:
        data["region"] = region
        data["telegram_id"] = query.from_user.id
        data["telegram_username"] = query.from_user.username
        print(data)
        add_user_to_database(data)
    await state.finish()
    user_data[query.from_user.id] = {"awaiting_question": True}
    await present_options(query.message)


@dp.callback_query_handler(option_callback.filter(name="Categories"))
async def process_categories_option(query: types.CallbackQuery):
    categories = fetch_categories()
    message_text = "Yo'nalishlarni tanlang:\n"
    inline_kb = InlineKeyboardMarkup(row_width=4)

    # Add existing categories to the keyboard
    for index, category_name in enumerate(categories, start=1):
        category_id_button = InlineKeyboardButton(
            f"{index}. {category_name}", callback_data=f"category_{index}"
        )
        inline_kb.add(category_id_button)

    # Add the "Other" option
    inline_kb.add(InlineKeyboardButton("Boshqa", callback_data="category_other"))

    await query.message.reply(message_text, reply_markup=inline_kb)
    await query.answer()


@dp.callback_query_handler(lambda query: query.data.startswith("category_"))
async def process_category_selection(query: types.CallbackQuery):
    category_data = query.data.split("_")

    if category_data[1] == "other":
        selected_category = None
    else:
        category_index = int(category_data[1])
        categories = fetch_categories()
        if 1 <= category_index <= len(categories):
            selected_category = category_index
        else:
            await query.answer("🚫 Yaroqsiz yo'nalish tanlandi.")
            return

    user_telegram_id = query.from_user.id
    user_database_id = get_user_database_id(user_telegram_id)
    if user_database_id is not None:
        await query.message.reply(f"Iltimos, savolingizni yozing.")
        user_data[user_telegram_id] = {
            "category_id": selected_category,
            "awaiting_question": True,
        }
    else:
        await query.answer("🚫 Foydalanuvchi topilmadi.")


@dp.message_handler(
    lambda message: user_data.get(message.from_user.id, {}).get("awaiting_question")
)
async def process_user_question(message: types.Message):
    user_telegram_id = message.from_user.id
    user_data_entry = user_data.get(user_telegram_id, {})
    if "category_id" in user_data_entry and "awaiting_question" in user_data_entry:
        category_id = user_data_entry.get("category_id")
        user_data_entry.pop("category_id")
        user_data_entry.pop("awaiting_question")
        user_database_id = get_user_database_id(user_telegram_id)
        if user_database_id:
            create_new_question(message.text, False, category_id, user_database_id)
            message_payload = "🥳🥳🥳\nE'tiboringiz uchun katta rahmat!\nSo'rovingiz hozirgina adminga jo'natildi."
            await message.reply(message_payload)
            admin_message = (
                f"ℹ️ℹ️ℹ️\nAssalomu alaykum!\n\nYangi So'rov:\n{message.text}"
            )
            for admin_id in fetch_admin_ids():
                await bot.send_message(admin_id, admin_message)
        else:
            await message.reply("🚫 Foydalanuvchi topilmadi.")
    else:
        await message.reply("🚫 Iltimos birinchi yo'nalishlardan birini tanlang.")


# --------------------------- ADMIN POSSILBE ACTIONS ---------------------------------
# Define constants for pagination
ITEMS_PER_PAGE = 5

# Pagination callback data
pagination_callback = CallbackData("paginate", "page")


# Helper function to chunk the questions list into pages
def chunked_questions_list(questions, items_per_page):
    for i in range(0, len(questions), items_per_page):
        yield questions[i : i + items_per_page]


# Updated function to display paginated questions
@dp.message_handler(commands=["savollar"], user_is_admin=True)
async def view_questions(message: types.Message):
    questions = fetch_unanswered_questions()
    pages = list(chunked_questions_list(questions, ITEMS_PER_PAGE))
    await display_page(message, pages, page=0)


async def display_page(message: types.Message, pages, page):
    if pages:
        questions_page = pages[page]
        inline_kb = InlineKeyboardMarkup(row_width=5)
        message_text = "Murojaatlardan birini tanlang:\n\n" + "\n".join(
            [f"{q_id}. {text}" for q_id, text in questions_page]
        )
        for q_id, _ in questions_page:
            inline_kb.insert(
                InlineKeyboardButton(
                    text=str(q_id), callback_data=answer_callback.new(id=q_id)
                )
            )
        if page > 0:
            inline_kb.insert(
                InlineKeyboardButton(
                    text="<< avvalgisi",
                    callback_data=pagination_callback.new(page=page - 1),
                )
            )
        if page < len(pages) - 1:
            inline_kb.insert(
                InlineKeyboardButton(
                    text="keyingisi >>",
                    callback_data=pagination_callback.new(page=page + 1),
                )
            )
        await message.answer(message_text, reply_markup=inline_kb)
    else:
        await message.answer("Hech qanday murojaatlar yo'q.")


@dp.callback_query_handler(pagination_callback.filter())
async def navigate_pages(query: types.CallbackQuery, callback_data: dict):
    page = int(callback_data["page"])
    questions = fetch_unanswered_questions()
    pages = list(chunked_questions_list(questions, ITEMS_PER_PAGE))
    await bot.delete_message(
        chat_id=query.message.chat.id, message_id=query.message.message_id
    )
    await display_page(query.message, pages, page=page)
    await query.answer()


# @dp.callback_query_handler(lambda query: query.data.startswith("answer_"))
# async def process_answer(query: types.CallbackQuery):
#     question_id = query.data.split("_")[1]
#     admin_response_state[query.from_user.id] = {
#         "awaiting_response": True,
#         "question_id": question_id,
#     }
#     print("process_answer function is running\n\n\n\n\n\n")
#     await query.message.reply(f"ℹ️ Iltimos so'rov uchun javobingizni yozing")


@dp.callback_query_handler(answer_callback.filter())
async def prompt_for_answer(query: types.CallbackQuery, callback_data: dict):
    question_id = callback_data["id"]
    admin_response_state[query.from_user.id] = {
        "awaiting_response": True,
        "question_id": question_id,
    }
    print("prompt_for_answer function is running\n\n\n\n\n\n")
    await query.message.reply(f"ℹ️ Iltimos so'rov uchun javobingizni yozing")


@dp.message_handler(lambda message: waiting_for_admin_response_condition(message))
async def save_admin_response(message: types.Message):
    admin_id = message.from_user.id
    response = message.text
    user_data = admin_response_state.get(admin_id)
    if user_data:
        question_id = user_data["question_id"]
        save_answer_to_database(question_id, response, admin_id)
        user_telegram_id = get_user_telegram_id_from_question(question_id)
        question = fetch_question_text(question_id)
        if user_telegram_id:
            await bot.send_message(
                user_telegram_id,
                f"Berilgan savol: {question}\nAdmindan Javob: {response}",
            )
        conn = sqlite3.connect("../db.sqlite3")
        cursor = conn.cursor()
        cursor.execute("UPDATE api_question SET status=1 WHERE id=?", (question_id,))
        conn.commit()
        conn.close()
        await message.reply(f"🥳🥳🥳\nJavob muvaffaqiyatli jonatildi!")
        admin_response_state.pop(admin_id)


@dp.callback_query_handler(view_questions_callback.filter(action="view_questions"))
async def admin_view_questions(query: types.CallbackQuery):
    questions = fetch_unanswered_questions()
    pages = list(chunked_questions_list(questions, ITEMS_PER_PAGE))
    if not pages:
        await query.message.answer("Murojaatlar mavjud emas.")
        return
    await display_page(query.message, pages, page=0)
    await query.answer()


if __name__ == "__main__":
    executor.start_polling(dp)