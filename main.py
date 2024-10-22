import logging
import random
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
from aiogram import F
from aiogram import Router
import asyncio
from elevenlabs import ElevenLabs

# Устанавливаем уровень логирования
logging.basicConfig(level=logging.INFO)

# Токен бота
API_TOKEN = ''

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()
router = Router()  # Добавляем маршрутизацию


# Создаем клавиатуру один раз
def create_keyboard():
    # Создаем кнопку для ссылки на GitHub
    github_button = InlineKeyboardButton(text="Мой GitHub", url="https://github.com/pan-keke/TG_bot")

    # Создаем кнопку для аудиофайла
    audio_button = InlineKeyboardButton(text="Получить аудиофайл", callback_data='get_audio')

    # Создаем клавиатуру с кнопками в виде вложенного списка
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [github_button],  # Кнопка GitHub на первой строке
        [audio_button]  # Кнопка для получения аудиофайла на третьей строке
    ])
    return keyboard


# Команда /start
@router.message(Command(commands=['start']))
async def send_welcome(message: types.Message):
    keyboard = create_keyboard()  # Создаем клавиатуру
    await message.answer("Привет! Я бот, который может отправить изображение и аудиофайл. Нажми на кнопки ниже:",
                         reply_markup=keyboard)


@router.message(Command(commands=['git']))
async def send_git_link(message: types.Message):
    git_link = "Вот ссылка на мой GitHub: https://github.com/pan-keke/TG_bot"
    await message.answer(git_link, disable_web_page_preview=True)


# Обработка сообщение "фото"
@router.message(F.text)
async def send_random_image(message: types.Message):
    if 'фото' in message.text.lower():  # Преобразуем текст к нижнему регистру и проверяем
        random_param = random.randint(1, 100000)
        image_url = f'https://picsum.photos/600/400?random={random_param}'

        try:
            await bot.send_photo(message.from_user.id, image_url)
            await message.answer("Вот случайное изображение, как вы и просили!", reply_markup=create_keyboard())
        except Exception as e:
            logging.error(f"Ошибка при отправке изображения: {e}")
            await message.answer("Не удалось получить изображение. Попробуйте позже.")


# Обработка нажатия на кнопку "Получить аудиофайл"
@router.callback_query(F.data == 'get_audio')
async def send_audio(callback_query: types.CallbackQuery):
    # URL аудиофайла (замени на реальную ссылку)
    client = ElevenLabs(
        api_key="sk_1a5ba9458f0d1649d23b6a484121f6b4d64a8f919b0d8037",
    )
    audio_url = client.samples.get_audio(
    voice_id="ja9xsmfGhxYcymxGcOGB",
    sample_id="pMsXgVXv3BLzUgSXRplE",
)

    try:
        # Отправка аудиофайла пользователю
        await bot.send_audio(callback_query.from_user.id, audio_url)

        # Отправляем сообщение с клавиатурой
        await callback_query.message.answer("Вот аудиофайл:", reply_markup=create_keyboard())
    except Exception as e:
        logging.error(f"Ошибка при отправке аудиофайла: {e}")
        await callback_query.answer("Не удалось получить аудиофайл. Попробуйте позже.")

    # Сообщаем Телеграму, что запрос обработан
    await callback_query.answer()


# Обработчик всех остальных сообщений
@router.message()
async def echo(message: types.Message):
    keyboard = create_keyboard()  # Создаем клавиатуру
    await message.answer("Я понимаю только команды или нажатия на кнопки.", reply_markup=keyboard)


# Регистрация маршрутов
dp.include_router(router)


async def main():
    # Запуск бота
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
