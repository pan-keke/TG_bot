import os
import logging
import random
import requests
import asyncio
from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, FSInputFile
from aiogram.filters import Command

# Устанавливаем уровень логирования
logging.basicConfig(level=logging.INFO)

# Переменные конфигурации
API_TOKEN = ''
FREESOUND_API_KEY = ''

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()
router = Router()  # Используем маршрутизацию


# Функция создания клавиатуры
def create_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Мой GitHub", url="https://github.com/pan-keke/tg_bot")],
        [InlineKeyboardButton(text="Получить аудиофайл", callback_data='get_audio')]
    ])


# Функция для получения случайного аудио URL из FreeSound API
def get_random_audio_url():
    random_page = random.randint(1, 5)  # Выбор случайной страницы
    search_url = (
        f"https://freesound.org/apiv2/search/text/"
        f"?query=random&filter=duration:[1 TO 10]&page={random_page}&page_size=10&fields=id,previews"
    )
    headers = {"Authorization": f"Token {FREESOUND_API_KEY}"}

    response = requests.get(search_url, headers=headers)
    if response.status_code == 200:
        results = response.json().get('results', [])
        if results:
            random_sound = random.choice(results)
            return random_sound['previews'].get('preview-lq-mp3')
    return None


# Команда /start
@router.message(Command(commands=['start']))
async def send_welcome(message: types.Message):
    await message.answer(
        "Привет! Я бот, который может отправить случайное изображение и аудиофайл. Нажми на кнопки ниже:",
        reply_markup=create_keyboard()
    )


# Команда /git
@router.message(Command(commands=['git']))
async def send_git_link(message: types.Message):
    await message.answer("Вот ссылка на мой GitHub: https://github.com/pan-keke/TG_bot", disable_web_page_preview=True)


# Обработка сообщений с текстом, содержащим "фото"
@router.message(F.text)
async def send_random_image(message: types.Message):
    if 'фото' in message.text.lower():
        random_param = random.randint(1, 100000)
        image_url = f'https://picsum.photos/600/400?random={random_param}'

        try:
            await bot.send_photo(message.from_user.id, image_url)
            await message.answer("Вот случайное изображение, как вы и просили!", reply_markup=create_keyboard())
        except Exception as e:
            logging.error(f"Ошибка при отправке изображения: {e}")
            await message.answer("Не удалось получить изображение. Попробуйте позже.")
    else:
        await message.answer("Я не понимаю такой команды(", reply_markup=create_keyboard())


# Отправка случайного аудио при нажатии кнопки
@router.callback_query(lambda c: c.data == 'get_audio')
async def send_audio(callback_query: types.CallbackQuery):
    audio_url = get_random_audio_url()

    if audio_url:
        audio_response = requests.get(audio_url)

        if audio_response.status_code == 200:
            with open("temp_audio.mp3", "wb") as file:
                file.write(audio_response.content)

            try:
                audio_file = FSInputFile("temp_audio.mp3")
                await bot.send_audio(callback_query.from_user.id, audio_file)
                await callback_query.message.answer("Вот случайный аудиофайл:", reply_markup=create_keyboard())
            finally:
                os.remove("temp_audio.mp3")  # Удаляем временный файл
        else:
            await callback_query.answer("Не удалось получить аудиофайл. Попробуйте позже.")
    else:
        await callback_query.answer("Не удалось получить аудиофайл. Попробуйте позже.")

    await callback_query.answer()


# Регистрация маршрутов
dp.include_router(router)


# Главная функция запуска бота
async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
