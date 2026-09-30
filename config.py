import os

# Читаем токены из переменных окружения (для Render/Railway) или используем захардкоженные (для локального запуска)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8661994601:AAEJBO-pb8ZkWAxdqYaesN2sWIEns90zCZw")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "9f06e90ef8293660ca0fb3cc83e9945d")

CITY = "Zielona Gora"
COUNTRY_CODE = "PL"

TIMEZONE = "Europe/Warsaw"

MORNING_REPORT_TIME = "07:00"

SCHEDULE = {
    0: {"start": "08:00", "end": "14:35"},  # Понедельник
    1: {"start": "08:00", "end": "15:25"},  # Вторник
    2: {"start": "08:00", "end": "14:35"},  # Среда
    3: {"start": "08:00", "end": "15:25"},  # Четверг
    4: {"start": "08:00", "end": "13:40"},  # Пятница
}

CLOTHING_RECOMMENDATIONS = {
    "cold": {
        "temp_range": (-100, 5),
        "items": ["теплая куртка", "шапка", "шарф", "перчатки", "теплые штаны"]
    },
    "cool": {
        "temp_range": (5, 15),
        "items": ["куртка", "джинсы", "свитер или худи"]
    },
    "mild": {
        "temp_range": (15, 20),
        "items": ["легкая куртка или толстовка", "джинсы или штаны"]
    },
    "warm": {
        "temp_range": (20, 25),
        "items": ["футболка", "легкие штаны или шорты"]
    },
    "hot": {
        "temp_range": (25, 100),
        "items": ["футболка", "шорты", "кепка от солнца"]
    }
}
