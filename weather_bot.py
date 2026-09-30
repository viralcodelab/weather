import logging
import requests
from datetime import datetime, time
import pytz
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import config
import json
import os

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

WARDROBE_FILE = "wardrobe.json"

def load_wardrobe():
    if os.path.exists(WARDROBE_FILE):
        with open(WARDROBE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_wardrobe(wardrobe):
    with open(WARDROBE_FILE, 'w', encoding='utf-8') as f:
        json.dump(wardrobe, f, ensure_ascii=False, indent=2)

def get_weather():
    url = f"http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": f"{config.CITY},{config.COUNTRY_CODE}",
        "appid": config.WEATHER_API_KEY,
        "units": "metric",
        "lang": "ru"
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        logger.error(f"Ошибка получения погоды: {response.status_code}")
        return None

def get_forecast():
    url = f"http://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": f"{config.CITY},{config.COUNTRY_CODE}",
        "appid": config.WEATHER_API_KEY,
        "units": "metric",
        "lang": "ru"
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        logger.error(f"Ошибка получения прогноза: {response.status_code}")
        return None

def will_rain_at_time(forecast_data, target_time):
    if not forecast_data:
        return False, "Не удалось получить прогноз"

    tz = pytz.timezone(config.TIMEZONE)
    target_dt = tz.localize(target_time)

    for item in forecast_data['list']:
        forecast_dt = datetime.fromtimestamp(item['dt'], tz=tz)

        if abs((forecast_dt - target_dt).total_seconds()) < 3 * 3600:
            weather_main = item['weather'][0]['main'].lower()
            if 'rain' in weather_main or item.get('rain'):
                return True, f"Дождь ожидается около {forecast_dt.strftime('%H:%M')}"

    return False, "Дождя не ожидается"

def get_clothing_recommendation(temp, rain):
    recommendation = ""

    for category, data in config.CLOTHING_RECOMMENDATIONS.items():
        if data['temp_range'][0] <= temp < data['temp_range'][1]:
            recommendation = ", ".join(data['items'])
            break

    if rain:
        recommendation += ", зонт или дождевик"

    return recommendation

def format_weather_emoji(weather_main):
    weather_emojis = {
        'clear': '☀️',
        'clouds': '☁️',
        'rain': '🌧️',
        'drizzle': '🌦️',
        'thunderstorm': '⛈️',
        'snow': '❄️',
        'mist': '🌫️',
        'fog': '🌫️'
    }
    return weather_emojis.get(weather_main.lower(), '🌤️')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    context.job_queue.run_daily(
        morning_report,
        time=datetime.strptime(config.MORNING_REPORT_TIME, "%H:%M").time(),
        days=(0, 1, 2, 3, 4),
        chat_id=update.effective_chat.id,
        name=f"morning_report_{user_id}"
    )

    await update.message.reply_text(
        "Привет! 👋\n\n"
        "Я буду присылать тебе утренние сводки погоды каждый будний день в 7:00.\n\n"
        "Команды:\n"
        "/weather - текущая погода\n"
        "/forecast - прогноз на день\n"
        "/add_clothes - отправь фото одежды с описанием\n"
        "/wardrobe - посмотреть твой гардероб\n"
        "/stop - остановить утренние сообщения"
    )

async def weather_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    weather_data = get_weather()

    if not weather_data:
        await update.message.reply_text("Не удалось получить данные о погоде 😔")
        return

    temp = weather_data['main']['temp']
    feels_like = weather_data['main']['feels_like']
    weather_desc = weather_data['weather'][0]['description']
    weather_main = weather_data['weather'][0]['main']
    emoji = format_weather_emoji(weather_main)

    message = (
        f"{emoji} Погода в {config.CITY}:\n\n"
        f"🌡️ Температура: {temp:.1f}°C (ощущается как {feels_like:.1f}°C)\n"
        f"📝 {weather_desc.capitalize()}\n"
        f"💨 Ветер: {weather_data['wind']['speed']} м/с\n"
        f"💧 Влажность: {weather_data['main']['humidity']}%"
    )

    await update.message.reply_text(message)

async def forecast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now(pytz.timezone(config.TIMEZONE))
    weekday = now.weekday()

    if weekday not in config.SCHEDULE:
        await update.message.reply_text("Сегодня выходной! Отдыхай 😊")
        return

    schedule = config.SCHEDULE[weekday]
    forecast_data = get_forecast()

    if not forecast_data:
        await update.message.reply_text("Не удалось получить прогноз 😔")
        return

    start_time = datetime.combine(now.date(), datetime.strptime(schedule['start'], "%H:%M").time())
    end_time = datetime.combine(now.date(), datetime.strptime(schedule['end'], "%H:%M").time())

    rain_start, msg_start = will_rain_at_time(forecast_data, start_time)
    rain_end, msg_end = will_rain_at_time(forecast_data, end_time)

    weather_data = get_weather()
    temp = weather_data['main']['temp'] if weather_data else 15

    clothing = get_clothing_recommendation(temp, rain_start or rain_end)

    message = (
        f"📅 Прогноз на сегодня:\n\n"
        f"🏫 Школа: {schedule['start']} - {schedule['end']}\n\n"
        f"🌅 Когда идешь ({schedule['start']}): {msg_start}\n"
        f"🌆 Когда возвращаешься ({schedule['end']}): {msg_end}\n\n"
        f"👔 Что надеть: {clothing}"
    )

    await update.message.reply_text(message)

async def morning_report(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.chat_id
    now = datetime.now(pytz.timezone(config.TIMEZONE))
    weekday = now.weekday()

    if weekday not in config.SCHEDULE:
        return

    schedule = config.SCHEDULE[weekday]
    weather_data = get_weather()
    forecast_data = get_forecast()

    if not weather_data or not forecast_data:
        await context.bot.send_message(
            chat_id=chat_id,
            text="Доброе утро! ☀️\nНе удалось получить данные о погоде 😔"
        )
        return

    temp = weather_data['main']['temp']
    feels_like = weather_data['main']['feels_like']
    weather_desc = weather_data['weather'][0]['description']
    emoji = format_weather_emoji(weather_data['weather'][0]['main'])

    start_time = datetime.combine(now.date(), datetime.strptime(schedule['start'], "%H:%M").time())
    end_time = datetime.combine(now.date(), datetime.strptime(schedule['end'], "%H:%M").time())

    rain_start, msg_start = will_rain_at_time(forecast_data, start_time)
    rain_end, msg_end = will_rain_at_time(forecast_data, end_time)

    clothing = get_clothing_recommendation(temp, rain_start or rain_end)

    message = (
        f"Доброе утро! {emoji}\n\n"
        f"🌡️ Температура: {temp:.1f}°C (ощущается как {feels_like:.1f}°C)\n"
        f"📝 {weather_desc.capitalize()}\n\n"
        f"🏫 Школа: {schedule['start']} - {schedule['end']}\n\n"
        f"🌅 Утром: {msg_start}\n"
        f"🌆 После школы: {msg_end}\n\n"
        f"👔 Что надеть: {clothing}"
    )

    if rain_start or rain_end:
        message += "\n\n☔ Не забудь зонт!"

    await context.bot.send_message(chat_id=chat_id, text=message)

async def add_clothes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Отправь мне фото одежды с подписью, например:\n"
        "\"Красная куртка для холодной погоды\"\n\n"
        "Я сохраню это и буду учитывать при рекомендациях."
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    wardrobe = load_wardrobe()

    if user_id not in wardrobe:
        wardrobe[user_id] = []

    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)

    caption = update.message.caption or "Без описания"

    item = {
        "file_id": photo.file_id,
        "description": caption,
        "added_date": datetime.now().isoformat()
    }

    wardrobe[user_id].append(item)
    save_wardrobe(wardrobe)

    await update.message.reply_text(
        f"✅ Добавлено в гардероб!\n"
        f"Описание: {caption}\n\n"
        f"Всего вещей: {len(wardrobe[user_id])}"
    )

async def wardrobe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    wardrobe = load_wardrobe()

    if user_id not in wardrobe or not wardrobe[user_id]:
        await update.message.reply_text(
            "Твой гардероб пуст 👔\n"
            "Используй /add_clothes чтобы добавить одежду"
        )
        return

    await update.message.reply_text(f"👔 Твой гардероб ({len(wardrobe[user_id])} вещей):")

    for idx, item in enumerate(wardrobe[user_id], 1):
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=item['file_id'],
            caption=f"{idx}. {item['description']}"
        )

async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    current_jobs = context.job_queue.get_jobs_by_name(f"morning_report_{user_id}")

    if not current_jobs:
        await update.message.reply_text("У тебя нет активных утренних уведомлений")
        return

    for job in current_jobs:
        job.schedule_removal()

    await update.message.reply_text("Утренние сообщения остановлены. Используй /start чтобы включить снова")

def main():
    application = Application.builder().token(config.TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("weather", weather_command))
    application.add_handler(CommandHandler("forecast", forecast_command))
    application.add_handler(CommandHandler("add_clothes", add_clothes))
    application.add_handler(CommandHandler("wardrobe", wardrobe_command))
    application.add_handler(CommandHandler("stop", stop_command))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    logger.info("Бот запущен...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
