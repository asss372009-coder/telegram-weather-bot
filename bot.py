# bot.py - РАБОЧАЯ ВЕРСИЯ
import os
import sys
import logging
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import requests

# Загружаем переменные из .env
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получаем токены
BOT_TOKEN = os.environ.get('BOT_TOKEN')
WEATHER_KEY = os.environ.get('WEATHER_API_KEY')

if not BOT_TOKEN:
    logger.error("❌ ОШИБКА: BOT_TOKEN не найден!")
    logger.error("Создайте файл .env с BOT_TOKEN=ваш_токен")
    sys.exit(1)

if not WEATHER_KEY:
    logger.error("❌ ОШИБКА: WEATHER_API_KEY не найден!")
    logger.error("Создайте файл .env с WEATHER_API_KEY=ваш_ключ")
    sys.exit(1)

logger.info(f"✅ BOT_TOKEN: {BOT_TOKEN[:10]}...")
logger.info(f"✅ WEATHER_API_KEY: {WEATHER_KEY[:10]}...")


# Команда /start
async def start(update, context):
    await update.message.reply_text(
        "🌤️ *Добро пожаловать в Weather Bot!*\n\n"
        "Напишите название города для получения погоды.\n\n"
        "*Примеры:*\n• Москва\n• London\n• New York",
        parse_mode='Markdown'
    )


# Обработка сообщений
async def get_weather(update, context):
    city = update.message.text.strip()

    if not city:
        await update.message.reply_text("Введите название города")
        return

    await update.message.reply_chat_action("typing")

    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            'q': city,
            'appid': WEATHER_KEY,
            'units': 'metric',
            'lang': 'ru'
        }

        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if data.get("cod") == 200:
            message = (
                f"🌤️ *Погода в {data['name']}*\n\n"
                f"🌡 *Температура:* {data['main']['temp']:.1f}°C\n"
                f"🤔 *Ощущается как:* {data['main']['feels_like']:.1f}°C\n"
                f"💧 *Влажность:* {data['main']['humidity']}%\n"
                f"💨 *Ветер:* {data['wind']['speed']:.1f} м/с\n"
                f"📊 *Давление:* {data['main']['pressure']} гПа\n"
                f"☁️ *Описание:* {data['weather'][0]['description'].capitalize()}"
            )
        else:
            error_msg = data.get('message', 'Неизвестная ошибка')
            message = f"❌ *Ошибка:* {error_msg}"

    except Exception as e:
        logger.error(f"Ошибка: {e}")
        message = "⚠️ Ошибка при получении погоды"

    await update.message.reply_text(message, parse_mode='Markdown')


# Главная функция
def main():
    print("=" * 50)
    print("🚀 ЗАПУСК ТЕЛЕГРАМ БОТА")
    print("=" * 50)

    try:
        # Создаем приложение
        application = Application.builder().token(BOT_TOKEN).build()

        # Регистрируем обработчики
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_weather))

        print("✅ Бот сконфигурирован")
        print("📱 Найдите бота в Telegram и напишите /start")
        print("=" * 50)

        # Запускаем бота
        application.run_polling(
            drop_pending_updates=True,
            timeout=30,
            connect_timeout=30
        )

    except Exception as e:
        logger.error(f"❌ Фатальная ошибка: {e}")
        print(f"\nОшибка: {e}")
        print("\nВозможные причины:")
        print("1. Неверный токен бота")
        print("2. Проблемы с версией python-telegram-bot")
        print("3. Другой экземпляр бота уже запущен")


if __name__ == "__main__":
    main()