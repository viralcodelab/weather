# 🚀 Как задеплоить бота на Render.com (БЕСПЛАТНО)

## Шаг 1: Создай GitHub репозиторий

1. Зайди на https://github.com и войди в аккаунт (или зарегистрируйся)
2. Нажми **"New repository"** (зеленая кнопка справа вверху)
3. Назови репозиторий: `weather-telegram-bot`
4. Сделай **Public** (для бесплатного деплоя)
5. НЕ добавляй README, .gitignore - у нас уже есть
6. Нажми **"Create repository"**

## Шаг 2: Загрузи файлы на GitHub

### Вариант А - Через браузер (проще):

1. На странице нового репозитория нажми **"uploading an existing file"**
2. Перетащи все файлы из папки `C:\scripts\weather_telegram_bot\`:
   - `weather_bot.py`
   - `config.py`
   - `requirements.txt`
   - `Procfile`
   - `runtime.txt`
   - `.gitignore`
   - `README.md`
3. Напиши commit message: "Initial commit"
4. Нажми **"Commit changes"**

### Вариант Б - Если есть git:

```bash
cd C:\scripts\weather_telegram_bot
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/ТВО_ИМЯ/weather-telegram-bot.git
git push -u origin main
```

## Шаг 3: Зарегистрируйся на Render.com

1. Зайди на https://render.com
2. Нажми **"Get Started"** или **"Sign Up"**
3. Выбери **"Sign up with GitHub"** - это проще
4. Разреши Render доступ к GitHub

## Шаг 4: Создай Web Service на Render

1. На главной странице Render нажми **"New +"** → **"Web Service"**
2. Найди свой репозиторий `weather-telegram-bot` и нажми **"Connect"**
3. Заполни настройки:

   **Name:** `weather-telegram-bot` (или любое имя)
   
   **Region:** Frankfurt (EU Central) - ближе к Польше
   
   **Branch:** `main`
   
   **Runtime:** `Python 3`
   
   **Build Command:** `pip install -r requirements.txt`
   
   **Start Command:** `python weather_bot.py`
   
   **Instance Type:** **FREE** ⬅️ ВАЖНО!

4. **Не нажимай "Create Web Service" пока!**

## Шаг 5: Добавь переменные окружения (Environment Variables)

⚠️ **ВАЖНО:** Не оставляй токены в `config.py` на GitHub - это небезопасно!

Перед созданием сервиса прокрути вниз до **"Environment Variables"** и добавь:

```
TELEGRAM_TOKEN = 8661994601:AAEJBO-pb8ZkWAxdqYaesN2sWIEns90zCZw
WEATHER_API_KEY = 9f06e90ef8293660ca0fb3cc83e9945d
```

(Нажимай **"Add Environment Variable"** для каждой переменной)

## Шаг 6: Обнови config.py для использования переменных окружения

**Я уже подготовлю для тебя обновленный `config.py`** который будет читать секреты из переменных окружения на Render, но работать локально если их нет.

Тебе нужно будет заменить содержимое `config.py` на GitHub на новую версию (я создам файл ниже).

## Шаг 7: Запусти деплой

1. Нажми **"Create Web Service"**
2. Render начнет деплой (займет 2-3 минуты)
3. Смотри логи - должно быть "Application started"
4. Когда статус станет **"Live"** - бот работает! 🎉

## Шаг 8: Проверь работу

1. Открой Telegram
2. Напиши своему боту `/start`
3. Попробуй `/weather`

## ⚠️ Важные моменты про бесплатный план Render:

### Ограничения FREE плана:
- ✅ **750 часов/месяц бесплатно** - этого хватит
- ⚠️ **Засыпает после 15 минут без активности**
- ⚠️ **Просыпается при первом запросе** (занимает ~30 секунд)

### Что это значит для бота:
- Если боту никто не пишет 15+ минут → он засыпает
- Когда ты напишешь `/weather` → он проснется через 30 сек и ответит
- **ПРОБЛЕМА:** Утренние сообщения в 7:00 могут не отправиться, если бот спит!

### Решение - Keep Alive (будильник для бота):

**Вариант 1:** Использовать **UptimeRobot** (бесплатно):
1. Зарегистрируйся на https://uptimerobot.com
2. Добавь монитор с URL твоего Render сервиса
3. Интервал проверки: каждые 5 минут
4. Бот будет просыпаться каждые 5 минут и не пропустит утреннюю сводку

**Вариант 2:** Использовать **Koyeb** или **Railway** вместо Render:
- Railway дает 500 часов/месяц и не засыпает
- Но требует привязку карты (не списывает деньги на FREE плане)

## Альтернатива: Railway.app (рекомендую!)

Если Render не подходит из-за засыпания:

1. Зайди на https://railway.app
2. Sign up with GitHub
3. New Project → Deploy from GitHub repo
4. Выбери `weather-telegram-bot`
5. Добавь те же Environment Variables
6. Deploy!

**Плюсы Railway:**
- ✅ 500 часов/месяц бесплатно
- ✅ **НЕ засыпает** - утренние сообщения работают!
- ⚠️ Требует подключить GitHub Student Pack или карту (не списывает на FREE)

## 🐛 Проблемы и решения

### Бот не отвечает:
- Проверь логи в Render (вкладка "Logs")
- Убедись что API ключ погоды активен (10-15 мин после регистрации)

### "Invalid API key":
- Подожди 15 минут после регистрации на OpenWeatherMap
- Проверь что правильно скопировал ключ в Environment Variables

### Бот задеплоился но не отправляет утренние сообщения:
- Render уснул → используй UptimeRobot или переходи на Railway

### Build failed:
- Проверь что все файлы загружены на GitHub
- Проверь что `requirements.txt` и `Procfile` на месте

---

## 📝 Чеклист перед деплоем:

- [ ] Создал GitHub репозиторий
- [ ] Загрузил все файлы на GitHub
- [ ] Зарегистрировался на Render.com
- [ ] Создал Web Service с правильными настройками
- [ ] Добавил Environment Variables (TELEGRAM_TOKEN, WEATHER_API_KEY)
- [ ] Обновил config.py для чтения env переменных
- [ ] Запустил деплой
- [ ] Проверил логи - "Application started"
- [ ] Написал боту в Telegram `/start`
- [ ] (Опционально) Настроил UptimeRobot если бот засыпает

---

Если что-то не работает - пиши, разберемся! 🚀
