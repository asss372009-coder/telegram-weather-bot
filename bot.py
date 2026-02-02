import os
import sys
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ========== КОНФИГУРАЦИЯ ==========
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    stream=sys.stdout  # Важно для Render!
)
logger = logging.getLogger(__name__)


# ========== ПРОВЕРКА ТОКЕНОВ ==========
def setup_tokens():
    """Проверяем и получаем токены"""
    logger.info("🔍 Проверка переменных окружения...")

    # Получаем токены из переменных окружения
    BOT_TOKEN = os.environ.get('BOT_TOKEN')
    WEATHER_KEY = os.environ.get('WEATHER_API_KEY')

    if not BOT_TOKEN:
        logger.error("❌ ОШИБКА: BOT_TOKEN не найден!")
        logger.error("Добавьте переменную окружения BOT_TOKEN в Render")
        return None, None

    if not WEATHER_KEY:
        logger.error("❌ ОШИБКА: WEATHER_API_KEY не найден!")
        logger.error("Добавьте переменную окружения WEATHER_API_KEY в Render")
        return None, None

    # Маскируем для безопасности в логах
    bot_masked = BOT_TOKEN[:10] + '...' if len(BOT_TOKEN) > 10 else '***'
    weather_masked = WEATHER_KEY[:10] + '...' if len(WEATHER_KEY) > 10 else '***'

    logger.info(f"✅ BOT_TOKEN: {bot_masked}")
    logger.info(f"✅ WEATHER_API_KEY: {weather_masked}")

    return BOT_TOKEN, WEATHER_KEY


# ========== КОМАНДА /START ==========
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    await update.message.reply_text(
        "🌤️ *Добро пожаловать в Weather Bot!*\n\n"
        "Я покажу вам текущую погоду в любом городе мира.\n\n"
        "*Как пользоваться:*\n"
        "Просто напишите название города!\n\n"
        "*Примеры:*\n"
        "• Москва\n"
        "• London\n"
        "• New York\n"
        "• Tokyo\n\n"
        "Напишите город прямо сейчас! 👇",
        parse_mode='Markdown'
    )


# ========== КОМАНДА /HELP ==========
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    await update.message.reply_text(
        "📖 *Помощь*\n\n"
        "Просто отправьте название города, и я покажу погоду.\n\n"
        "*Советы:*\n"
        "• Используйте русское или английское название\n"
        "• Для точности можно указать страну: 'Москва, RU'\n"
        "• Если город не находится, попробуйте другое написание\n\n"
        "*Примеры:*\n"
        "Москва\nСанкт-Петербург\nLondon\nParis, France",
        parse_mode='Markdown'
    )


# ========== ПОЛУЧЕНИЕ ПОГОДЫ ==========
def get_weather_data(city: str, api_key: str):
    """Получает данные о погоде из API"""
    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            'q': city,
            'appid': api_key,
            'units': 'metric',  # Градусы Цельсия
            'lang': 'ru'  # Русский язык
        }

        logger.info(f"🌍 Запрос погоды для: {city}")
        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ Погода получена для: {data.get('name', city)}")
            return data
        else:
            logger.error(f"❌ API ошибка: {response.status_code}")
            return {'cod': response.status_code, 'message': response.text}

    except requests.exceptions.Timeout:
        logger.error("⏳ Таймаут при запросе погоды")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"🌐 Ошибка сети: {e}")
        return None
    except Exception as e:
        logger.error(f"⚠️ Неизвестная ошибка: {e}")
        return None


# ========== ОБРАБОТКА СООБЩЕНИЙ ==========
async def handle_city_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик сообщений с городами"""
    city = update.message.text.strip()

    if not city:
        await update.message.reply_text("❌ Пожалуйста, введите название города.")
        return

    # Показываем статус "печатает"
    await update.message.reply_chat_action(action="typing")

    # Получаем ключ из контекста
    weather_key = context.application.bot_data.get('weather_key')
    if not weather_key:
        await update.message.reply_text("⚠️ Ошибка конфигурации бота.")
        return

    # Получаем данные о погоде
    weather_data = get_weather_data(city, weather_key)

    if weather_data is None:
        await update.message.reply_text(
            "⚠️ *Ошибка соединения*\n"
            "Не удалось подключиться к серверу погоды. "
            "Попробуйте позже.",
            parse_mode='Markdown'
        )
        return

    # Обрабатываем ответ API
    if weather_data.get('cod') == 200:
        # Извлекаем данные
        location = weather_data['name']
        country = weather_data.get('sys', {}).get('country', '')
        if country:
            location = f"{location}, {country}"

        temp = weather_data['main']['temp']
        feels_like = weather_data['main']['feels_like']
        humidity = weather_data['main']['humidity']
        pressure = weather_data['main']['pressure']
        wind_speed = weather_data['wind']['speed']
        description = weather_data['weather'][0]['description'].capitalize()

        # Выбираем иконку
        icon = get_weather_icon(description.lower())

        # Формируем ответ
        message = (
            f"{icon} *Погода в {location}*\n\n"
            f"🌡 *Температура:* {temp:.1f}°C\n"
            f"🤔 *Ощущается как:* {feels_like:.1f}°C\n"
            f"💧 *Влажность:* {humidity}%\n"
            f"📊 *Давление:* {pressure} гПа\n"
            f"💨 *Ветер:* {wind_speed:.1f} м/с\n"
            f"☁️ *Описание:* {description}"
        )

        await update.message.reply_text(message, parse_mode='Markdown')

        # Подсказка для следующего запроса
        await update.message.reply_text(
            "Хотите узнать погоду в другом городе? "
            "Просто напишите его название! 😊"
        )

    else:
        error_msg = weather_data.get('message', 'Неизвестная ошибка')
        if 'city not found' in error_msg.lower() or weather_data.get('cod') == '404':
            await update.message.reply_text(
                f"❌ *Город не найден*\n"
                f"Я не могу найти город '{city}'.\n\n"
                f"*Попробуйте:*\n"
                f"• Проверить написание\n"
                f"• Использовать английское название\n"
                f"• Указать страну: 'Москва, RU'",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                f"⚠️ *Ошибка API:* {error_msg}",
                parse_mode='Markdown'
            )


def get_weather_icon(description: str):
    """Возвращает иконку для типа погоды"""
    icons = {
        'ясно': '☀️',
        'солнечно': '☀️',
        'малооблачно': '🌤️',
        'облачно': '☁️',
        'пасмурно': '☁️',
        'дождь': '🌧️',
        'ливень': '🌧️',
        'гроза': '⛈️',
        'снег': '❄️',
        'туман': '🌫️',
        'ветрено': '💨'
    }

    for key, icon in icons.items():
        if key in description:
            return icon

    return '🌤️'  # Иконка по умолчанию


# ========== ОБРАБОТЧИК ОШИБОК ==========
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logger.error(f"Ошибка при обработке обновления: {context.error}")

    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "⚠️ Произошла ошибка. Пожалуйста, попробуйте позже."
            )
    except Exception as e:
        logger.error(f"Не удалось отправить сообщение об ошибке: {e}")


# ========== ГЛАВНАЯ ФУНКЦИЯ ==========
async def main():
    """Основная асинхронная функция"""
    logger.info("=" * 50)
    logger.info("🚀 ЗАПУСК ТЕЛЕГРАМ БОТА НА RENDER")
    logger.info("=" * 50)

    # Получаем токены
    BOT_TOKEN, WEATHER_KEY = setup_tokens()

    if not BOT_TOKEN or not WEATHER_KEY:
        logger.error("❌ Не удалось получить токены. Завершаю работу.")
        return

    try:
        # Создаем приложение
        application = Application.builder().token(BOT_TOKEN).build()

        # Сохраняем ключ погоды в данных бота
        application.bot_data['weather_key'] = WEATHER_KEY

        # Регистрируем обработчики
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_city_message)
        )

        # Регистрируем обработчик ошибок
        application.add_error_handler(error_handler)

        logger.info("✅ Бот сконфигурирован")
        logger.info("📱 Найдите бота в Telegram и напишите /start")
        logger.info("=" * 50)

        # Запускаем бота
        await application.run_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES,
            timeout=30,
            connect_timeout=30,
            read_timeout=30,
            write_timeout=30
        )

    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        raise


def run_bot():
    """Точка входа для Render"""
    try:
        import asyncio
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"❌ Фатальная ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_bot()