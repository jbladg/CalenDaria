# Библиотеки
import asyncio
import aiogram
from aiogram import Dispatcher
from aiogram.utils import executor
from asyncio import sleep
from datetime import datetime
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP

# Запуск бота
bot = aiogram.Bot(token='5135057052:AAEe5qqDaOpDIcjobcvQqTWOx21ExY4-naM')
dp = Dispatcher(bot)

# Словари с пользователями
users = {}
events = {}
past_events = {}
user_create_event_status = {}
waiting_users = []

# Списки команд для каждой категории
start_commands = ["/start", "start", "старт", "начать", "начало"]
register_commands = ["/auth", "auth", "регистрация", "авторизация", "вход", "/reg", "reg"]
help_commands = ["/commands", "/cmds", "/help", "команды", "помощь"]
add_commands = ["/add", "/addevent", "/eventadd", "добавить", "создать"]


# Обработка команд
@dp.message_handler(content_types=['text'])
async def get_text_messages(message: aiogram.types.Message):
    # Получаем нужные переменные из глобального контекста
    global users, events, past_events, user_create_event_status, waiting_users
    msg = message.text.lower()
    user_id = message.from_user.id

    # Если пользователь настраивает событие
    if user_id in user_create_event_status:
        status = user_create_event_status[user_id]

        if status == "Время":
            if ":" not in msg:
                reply_msg = "❌ Неверный формат\nКорректный формат: Часы:Минуты\n"
                await bot.send_message(user_id, reply_msg)
                return
            hours = msg.split(":")[0]
            minutes = msg.split(":")[1]
            try:
                hours = int(hours)
                minutes = int(minutes)

                if hours > 23:
                    hours = hours % 24
                if minutes > 60:
                    minutes = minutes % 60
                if hours < 0:
                    hours = (24 + hours) % 24
                if minutes < 0:
                    minutes = (60 + minutes) % 60
            except:
                reply_msg = "❌ Неверный формат\nКорректный формат: Часы:Минуты\n"
                await bot.send_message(user_id, reply_msg)
                return

            events_list = events[user_id]
            event = events_list[len(events_list) - 1]

            if minutes < 10:
                minutes = "0" + str(minutes)
            if hours < 10:
                hours = "0" + str(hours)

            event += str(hours) + ":" + str(minutes) + "~"
            events_list[len(events_list) - 1] = event
            events[user_id] = events_list
            await bot.send_message(user_id, f"💯 Выбранная время события: {hours}:{minutes}\n" \
                                            f"Теперь введите название события\n")
            user_create_event_status[user_id] = "Название"
            return

        if status == "Название":
            events_list = events[user_id]
            event = events_list[len(events_list) - 1]
            event += msg + "~"
            events_list[len(events_list) - 1] = event
            events[user_id] = events_list
            await bot.send_message(user_id, f"💯 Имя события: {msg}\n" \
                                            f"🌐 Супер! Теперь оно есть в вашем списке.\n")
            user_create_event_status.pop(user_id)
            return

    # Если пользователь написал стартовую команду
    if msg in start_commands:
        if user_id not in users:
            reply_msg = "Добро пожаловать в КаленДарья 😎!\n" \
                        "Самый удобный и приятный ТГ-календарь.\n\n" \
                        "Вас нету в нашей базе, а значит вам надо зарегистрировать!\n" \
                        "Для этого пишите 'регистрация' или 'вход'"
            await bot.send_message(user_id, reply_msg)
        return

    # Если пользователь написал команду регистрации
    if msg in register_commands:
        if user_id in users:
            reply_msg = "⛔ Упс... Ошибка!\n" \
                        "Кажется вы уже авторизированы.\n\n" \
                        "Справка: 'команды'"
            await bot.send_message(user_id, reply_msg)
            return

        if user_id in waiting_users:
            reply_msg = "❕ Так-с...\n" \
                        "Кажись вы делаете что-то неправильно.\n\n" \
                        "Справка: 'команды'"
            await bot.send_message(user_id, reply_msg)
            return

        reply_msg = "✅ Супер!\n" \
                    "Напишите как к вам обращаться."
        await bot.send_message(user_id, reply_msg)
        waiting_users.append(user_id)
        return

    if msg in help_commands:
        reply_msg = "🏴‍ Доступные команды:\n" \
                    "   🔅 'события' показать доступные события\n" \
                    "   🔅 'добавить' добавить новое событие\n" \
                    "   🔅 'удалить' удалить существующее событие\n" \
                    "   🔅 'уведомление' настройки уведомлений\n" \
                    "   🔅 'обращение' изменить обращение к вам\n" \
                    "   🔅 'прошедшие' показать прошедшие события"
        await bot.send_message(user_id, reply_msg)
        return

    if msg == "события":
        if user_id not in events:
            reply_msg = "💨 Упс...\n" \
                        "У вас нет запланированных событий!"
            await bot.send_message(user_id, reply_msg)
            return

        events_list = events[user_id]
        if len(events_list) == 0:
            reply_msg = "💨 Упс...\n" \
                        "У вас нет запланированных событий!"
            await bot.send_message(user_id, reply_msg)
            return

        reply_msg = "🕒 События 🕤\n"
        for event in events_list:
            date = event.split("~")[0]
            time = event.split("~")[1]
            name = event.split("~")[2]
            reply_msg += date + " " + time + " " + name + "\n"
        await bot.send_message(user_id, reply_msg)
        return

    if msg == "прошедшие":
        if user_id not in past_events:
            reply_msg = "💨 Упс...\n" \
                        "У вас нет запланированных событий!"
            await bot.send_message(user_id, reply_msg)
            return

        events_list = past_events[user_id]
        if len(events_list) == 0:
            reply_msg = "💨 Упс...\n" \
                        "У вас нет запланированных событий!"
            await bot.send_message(user_id, reply_msg)
            return

        reply_msg = "⚜ Прошедшие события ⚜\n"
        for event in events_list:
            date = event.split("~")[0]
            time = event.split("~")[1]
            name = event.split("~")[2]
            reply_msg += date + " " + time + " " + name + "\n"
        await bot.send_message(user_id, reply_msg)
        return

    if msg in add_commands:
        if user_id not in users:
            reply_msg = "💨 Упс...\n" \
                        "Вы не зарегистрированы: 'войти'"
            await bot.send_message(user_id, reply_msg)
            return

        if user_id in user_create_event_status:
            reply_msg = "💨 Упс...\n" \
                        "Вы уже добавляете событие"
            await bot.send_message(user_id, reply_msg)
            return

        calendar, step = DetailedTelegramCalendar().build()
        reply_msg = "💥 Выберите дату события\n" \
                    f"{LSTEP[step]}"
        await bot.send_message(user_id, reply_msg, reply_markup=calendar)
        user_create_event_status[user_id] = "Дата"
        print(user_id)
        return

    # Если пользователь в списках на регистрацию (ожидаем имя)
    if user_id in waiting_users:
        users[user_id] = message.text
        events[user_id] = []

        reply_msg = f"✅ Прекрасно, {message.text}!\n" \
                    "Теперь вы можете полностью использовать календарь!\n\n" \
                    "Справка: 'команды'"
        await bot.send_message(user_id, reply_msg)
        waiting_users.remove(user_id)
        return


@dp.callback_query_handler(run_task=DetailedTelegramCalendar.func())
async def cal(c):
    global events, user_create_event_status
    result, key, step = DetailedTelegramCalendar().process(c.data)
    if not result and key:
        await bot.edit_message_text(f"{LSTEP[step]}", c.message.chat.id, c.message.message_id, reply_markup=key)
    elif result:
        user_id = c.message.chat.id
        await bot.edit_message_text(f"💯 Выбранная дата события: {result}\n"\
                              f"Теперь введите время в формате\n"\
                              f"🔵 Часы:Минуты", c.message.chat.id, c.message.message_id)
        user_create_event_status[user_id] = "Время"
        print(user_id)
        events_list = events[user_id]
        events_list.append(f"{result}~")
        events[user_id] = events_list
    return


# Проверка наступления событий
async def checking():
    global past_events, events
    while True:
        # Асинхронно освобождаем секунду для работы бота
        await sleep(1)

        # Достаём ID пользователя и его список событий
        for user_id, event_list in events.items():
            # Если событий нет
            if len(event_list) == 0:
                continue

            # Список для удалённых событий (которые сработали)
            # Их нельзя удалить во время перебора в цикле
            removed_list = []

            # Проходимся по каждому событию
            for event in event_list:
                # Если событие не конечное (не хватает информации, разделённой ~)
                if str(event).count("~") != 3:
                    continue

                # Получаем нужные поля
                data = event.split("~")[0]
                time = event.split("~")[1]
                name = event.split("~")[2]

                # БЕрём наше время
                date_now = str(datetime.now())
                # Если время события есть в нашем времени
                # (например: 20/11/2022 12:33 в 20/11/2022 12:33.455353)
                if data + " " + time in date_now:
                    user_name = users[user_id]
                    await bot.send_message(user_id, "💥 ВРЕМЯ ПРИШЛО!\n"\
                                                    f"Дорогой, {user_name}\n"\
                                                    f"Событие {name} наступило")
                    removed_list.append(event)
            # Удаляем ненужные события из списка и добавляем их в прошедшие
            for event in removed_list:
                event_list.remove(event)
                past_events_list = [event]
                if user_id in past_events:
                    past_events_list = past_events[user_id]
                    past_events_list.append(event)
                past_events[user_id] = past_events_list


# Добавляем проверку на наступление событий
async def on_startup(_):
    asyncio.create_task(checking())

# Если скрипт запускается как основной скпирт (не import'ом и тд)
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False, on_startup=on_startup)