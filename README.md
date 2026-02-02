# 🌤️ Telegram Weather Bot

Телеграм бот для получения текущей погоды в любом городе мира.

## 🚀 Деплой на Render.com

1. Нажмите кнопку ниже для быстрого деплоя:
   
   [![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/ваш-username/telegram-weather-bot)

2. Укажите переменные окружения:
   - `BOT_TOKEN` - токен от @BotFather
   - `WEATHER_API_KEY` - ключ от OpenWeatherMap

3. Нажмите "Apply" и дождитесь деплоя

## 📦 Локальная разработка

```bash
# Клонировать репозиторий
git clone https://github.com/ваш-username/weather_bot.git
cd telegram_weather

# Установить зависимости
pip install -r requirements.txt

# Запустить бота
BOT_TOKEN=ваш_токен WEATHER_API_KEY=ваш_ключ python bot.py