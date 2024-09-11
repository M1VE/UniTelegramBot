import asyncio
import asyncpg
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup
from aiogram import Router
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder

# Ваш токен API Telegram-бота
API_TOKEN = '6699057425:AAGrYesGQ-Pk2qo3gvw8WOd8J75cKXvk-P4'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())  # В версии 3.x требуется указать хранилище состояний
router = Router()  # Создание роутера для регистрации хендлеров


# Подключение к базе данных PostgreSQL
async def create_db_pool():
    return await asyncpg.create_pool(database='university', user='your_user', password='your_password',
                                     host='localhost')


db_pool = None


# Создание главного меню для выбора направления (ИСИТ или ИВТ)
def main_menu():
    builder = ReplyKeyboardBuilder()
    builder.button(text="ИСИТ")
    builder.button(text="ИВТ")
    builder.adjust(1)  # Одна кнопка в строке
    return builder.as_markup(resize_keyboard=True)


# Меню выбора курсов
def course_menu():
    builder = ReplyKeyboardBuilder()
    for i in range(1, 5):
        builder.button(text=f"{i} курс")
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)


# Меню выбора семестров
def semester_menu():
    builder = ReplyKeyboardBuilder()
    builder.button(text="1 семестр")
    builder.button(text="2 семестр")
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)


# Хендлер на старт
@router.message(Command(commands=["start"]))
async def start(message: types.Message):
    await message.answer("Выберите направление:", reply_markup=main_menu())


# Хендлер на выбор направления
@router.message(lambda message: message.text in ["ИСИТ", "ИВТ"])
async def choose_direction(message: types.Message):
    direction = message.text
    await message.answer(f"Вы выбрали {direction}. Теперь выберите курс:", reply_markup=course_menu())


# Хендлер на выбор курса
@router.message(lambda message: message.text in ["1 курс", "2 курс", "3 курс", "4 курс"])
async def choose_course(message: types.Message):
    course = int(message.text.split()[0])
    direction = message.reply_to_message.text
    await message.answer(f"Вы выбрали {course} курс. Теперь выберите семестр:", reply_markup=semester_menu())


# Получение предметов из базы данных для выбранного направления, курса и семестра
async def get_subjects(course_number, semester_number, direction_name):
    async with db_pool.acquire() as conn:
        # Получаем идентификатор направления (ИСИТ или ИВТ)
        direction_id = await conn.fetchval('SELECT id FROM directions WHERE name=$1', direction_name)

        # Получаем идентификатор курса
        course_id = await conn.fetchval('SELECT id FROM courses WHERE direction_id=$1 AND course_number=$2',
                                        direction_id, course_number)

        # Получаем идентификатор семестра
        semester_id = await conn.fetchval('SELECT id FROM semesters WHERE course_id=$1 AND semester_number=$2',
                                          course_id, semester_number)

        # Получаем список предметов
        rows = await conn.fetch('SELECT subject_name FROM subjects WHERE semester_id=$1 AND direction_id=$2',
                                semester_id, direction_id)

        return [row['subject_name'] for row in rows]


# Хендлер на выбор семестра и показ предметов
@router.message(lambda message: message.text in ["1 семестр", "2 семестр"])
async def choose_semester(message: types.Message):
    semester = int(message.text.split()[0])
    course = int(message.reply_to_message.text.split()[0])  # Извлекаем курс
    direction = message.reply_to_message.reply_to_message.text  # Извлекаем направление

    subjects = await get_subjects(course, semester, direction)  # Получаем предметы для направления
    if subjects:
        subjects_menu = ReplyKeyboardMarkup(resize_keyboard=True).add(*subjects)
        await message.answer("Теперь выберите предмет:", reply_markup=subjects_menu)
    else:
        await message.answer("Предметы не найдены для выбранного направления, курса и семестра.")


# Получение информации о предмете из базы данных
async def get_subject_info(subject_name):
    async with db_pool.acquire() as conn:
        info = await conn.fetchval('SELECT info FROM subjects WHERE subject_name=$1', subject_name)
        return info


# Хендлер на выбор предмета и показ информации
@router.message(lambda message: message.text not in ["1 семестр", "2 семестр"])
async def show_subject_info(message: types.Message):
    subject = message.text
    info = await get_subject_info(subject)

    if info:
        await message.answer(f"Информация о {subject}: {info}")
    else:
        await message.answer(f"Информация о {subject} не найдена.")


# Функция для запуска бота
async def main():
    global db_pool
    db_pool = await create_db_pool()  # Создаем пул соединений с базой данных
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
