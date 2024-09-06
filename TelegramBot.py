import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram import Router
from aiogram.filters import Command  # Фильтр для команд
from aiogram.utils.keyboard import ReplyKeyboardBuilder

API_TOKEN = '6699057425:AAGrYesGQ-Pk2qo3gvw8WOd8J75cKXvk-P4'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())  # В версии 3.x требуется указать хранилище состояний
router = Router()  # Создание роутера для регистрации хендлеров

# Временные данные вместо базы данных
fake_courses = ["Курс 1", "Курс 2", "Курс 3"]
fake_subjects = {
    ("Курс 1", "1"): ["Предмет 1.1", "Предмет 1.2"],
    ("Курс 1", "2"): ["Предмет 1.3", "Предмет 1.4"],
    ("Курс 2", "1"): ["Предмет 2.1", "Предмет 2.2"],
    ("Курс 2", "2"): ["Предмет 2.3", "Предмет 2.4"]
}

# Главная клавиатура
def main_menu():
    builder = ReplyKeyboardBuilder()
    for course in fake_courses:
        builder.button(text=course)
    builder.adjust(1)  # Одна кнопка в строке
    return builder.as_markup(resize_keyboard=True)

# Кнопки выбора семестра
def semester_menu(course):
    builder = ReplyKeyboardBuilder()
    builder.button(text="1 семестр")
    builder.button(text="2 семестр")
    builder.button(text="Назад")
    builder.adjust(2)  # Две кнопки в строке
    return builder.as_markup(resize_keyboard=True)

# Кнопки выбора предметов
def subjects_menu(course, semester):
    builder = ReplyKeyboardBuilder()
    subjects = fake_subjects.get((course, semester), [])
    for subject in subjects:
        builder.button(text=subject)
    builder.button(text="Назад")
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)

# Хендлер на старт с использованием фильтра Command
@router.message(Command(commands=["start"]))  # Фильтр для команды /start
async def start(message: types.Message):
    await message.answer("Выберите курс:", reply_markup=main_menu())

# Хендлер на выбор курса
@router.message(lambda message: message.text in fake_courses)
async def choose_course(message: types.Message):
    course = message.text
    await message.answer(f"Вы выбрали курс {course}. Теперь выберите семестр:", reply_markup=semester_menu(course))

# Хендлер на выбор семестра
@router.message(lambda message: message.text in ["1 семестр", "2 семестр"])
async def choose_semester(message: types.Message):
    course = message.reply_to_message.text.split()[1]  # Получаем курс из предыдущего сообщения
    semester = message.text.split()[0]
    await message.answer(f"Вы выбрали {semester} семестр. Теперь выберите предмет:", reply_markup=subjects_menu(course, semester))

# Хендлер на выбор предмета
@router.message(lambda message: message.text not in ["1 семестр", "2 семестр", "Назад"])
async def show_subject_info(message: types.Message):
    subject = message.text
    await message.answer(f"Информация о {subject}: Здесь будет информация о выбранном предмете.")

# Хендлер на кнопку "Назад"
@router.message(lambda message: message.text == "Назад")
async def go_back(message: types.Message):
    await message.answer("Вы вернулись назад. Выберите курс:", reply_markup=main_menu())

# Регистрация хендлеров в диспетчере
dp.include_router(router)

# Функция для запуска бота
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
