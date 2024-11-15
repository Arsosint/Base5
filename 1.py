import telebot
import sqlite3
import time

# Токен вашего бота
bot = telebot.TeleBot('8105252956:AAHZr5AgjBDyIYh1MVkJ15hk-FZjJRKGSBM')

# Функция для получения ранга пользователя
def get_user_rank(tg_id):
    conn = sqlite3.connect('bot_data.db')
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT rank FROM users WHERE tg_id=?", (tg_id,))
        row = cursor.fetchone()
        if row:
            return row[0]
        else:
            cursor.execute("INSERT OR IGNORE INTO users (tg_id) VALUES (?)", (tg_id,))
            conn.commit()
            return 'Нету в базе'

# Функция для проверки прав доступа
def has_permissions(tg_id, command):
    rank = get_user_rank(tg_id)
    permissions = {
        'Владелец': ['/мут', '/бан', '/делмут', '/делбан', '/ранг', '/снятьранг', '/траст'],
        'Директор': ['/мут', '/бан', '/делмут', '/делбан', '/траст'],
        'Админ': ['/мут', '/бан', '/делмут', '/делбан'],
        'Гарант': ['/мут', '/делмут', '/траст'],
        'Стажёр': [],
        'Волонтёр': [],
        'Нету в базе': []
    }
    return command in permissions.get(rank, [])

# Обработчик команды /мут
@bot.message_handler(commands=['мут'])
def mute_user(message):
    if not has_permissions(message.from_user.id, '/мут'):
        bot.send_message(message.chat.id, 'У вас недостаточно прав.')
        return

    args = message.text.split()[1:]
    if len(args) < 3:
        bot.send_message(message.chat.id, 'Недостаточно аргументов. Используйте: /мут @username причина время (в секундах)')
        return

    tg_id = args[0][1:]
    reason = ' '.join(args[1:-1])
    duration = int(args[-1])

    conn = sqlite3.connect('bot_data.db')
    with conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET mute_until=?, mute_reason=? WHERE tg_id=?", (int(time.time()) + duration, reason, tg_id))
        conn.commit()

    bot.send_message(message.chat.id, f'Пользователь @{tg_id} заглушен на {duration} секунд.')

# Обработчик команды /бан
@bot.message_handler(commands=['бан'])
def ban_user(message):
    if not has_permissions(message.from_user.id, '/бан'):
        bot.send_message(message.chat.id, 'У вас недостаточно прав.')
        return

    args = message.text.split()[1:]
    if len(args) < 3:
        bot.send_message(message.chat.id, 'Недостаточно аргументов. Используйте: /бан @username причина время (в секундах)')
        return

    tg_id = args[0][1:]
    reason = ' '.join(args[1:-1])
    duration = int(args[-1])

    conn = sqlite3.connect('bot_data.db')
    with conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET ban_until=?, ban_reason=? WHERE tg_id=?", (int(time.time()) + duration, reason, tg_id))
        conn.commit()

    bot.send_message(message.chat.id, f'Пользователь @{tg_id} забанен на {duration} секунд.')

# Обработчик команды /делмут
@bot.message_handler(commands=['делмут'])
def unmute_user(message):
    if not has_permissions(message.from_user.id, '/делмут'):
        bot.send_message(message.chat.id, 'У вас недостаточно прав.')
        return

    args = message.text.split()[1:]
    if len(args) < 4:
        bot.send_message(message.chat.id, 'Недостаточно аргументов. Используйте: /делмут @username причина кол-во время (в секундах)')
        return

    tg_id = args[0][1:]
    reason = ' '.join(args[1:-2])
    count = int(args[-2])
    duration = int(args[-1])

    conn = sqlite3.connect('bot_data.db')
    with conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET mute_until=?, mute_reason=? WHERE tg_id=?", (int(time.time()) + duration, reason, tg_id))
        conn.commit()

    # Удаление последних сообщений
    try:
        for i in range(count):
            message_id = bot.get_updates()[-1].message.message_id - i
            bot.delete_message(message.chat.id, message_id) 
    except:
        bot.send_message(message.chat.id, 'Ошибка при удалении сообщений. Возможно, не удалось удалить некоторые из них.')

    bot.send_message(message.chat.id, f'Пользователь @{tg_id} заглушен на {duration} секунд. Удалено {count} последних сообщений.')

# Обработчик команды /оффтоп
@bot.message_handler(commands=['оффтоп'])
def offtop_user(message):
    if not has_permissions(message.from_user.id, '/оффтоп'):
        bot.send_message(message.chat.id, 'У вас недостаточно прав.')
        return

    tg_id = message.text.split()[1][1:]
    conn = sqlite3.connect('bot_data.db')
    with conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET mute_until=?, mute_reason='Оффтоп' WHERE tg_id=?", (int(time.time()) + 300, tg_id))
        conn.commit()

    bot.send_message(message.chat.id, f'Пользователь @{tg_id} заглушен на 5 минут за оффтоп.')

# Обработчик команды /делбан
@bot.message_handler(commands=['делбан'])
def unban_user(message):
    if not has_permissions(message.from_user.id, '/делбан'):
        bot.send_message(message.chat.id, 'У вас недостаточно прав.')
        return

    args = message.text.split()[1:]
    if len(args) < 4:
        bot.send_message(message.chat.id, 'Недостаточно аргументов. Используйте: /делбан @username причина кол-во время (в секундах)')
        return

    tg_id = args[0][1:]
    reason = ' '.join(args[1:-2])
    count = int(args[-2])
    duration = int(args[-1])

    conn = sqlite3.connect('bot_data.db')
    with conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET ban_until=?, ban_reason=? WHERE tg_id=?", (int(time.time()) + duration, reason, tg_id))
        conn.commit()

    # Удаление последних сообщений
    try:
        for i in range(count):
            message_id = bot.get_updates()[-1].message.message_id - i
            bot.delete_message(message.chat.id, message_id) 
    except:
        bot.send_message(message.chat.id, 'Ошибка при удалении сообщений. Возможно, не удалось удалить некоторые из них.')

    bot.send_message(message.chat.id, f'Пользователь @{tg_id} забанен на {duration} секунд. Удалено {count} последних сообщений.')

# Обработчик команды /ранг
@bot.message_handler(commands=['ранг'])
def set_rank(message):
    if not has_permissions(message.from_user.id, '/ранг'):
        bot.send_message(message.chat.id, 'У вас недостаточно прав.')
        return

    args = message.text.split()[1:]
    if len(args) < 2:
        bot.send_message(message.chat.id, 'Недостаточно аргументов. Используйте: /ранг id ранг')
        return

    tg_id = int(args[0])
    rank = args[1]

    conn = sqlite3.connect('bot_data.db')
    with conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET rank=? WHERE tg_id=?", (rank, tg_id))
        conn.commit()

    bot.send_message(message.chat.id, f'Пользователю {tg_id} выдан ранг {rank}.')

# Обработчик команды /снятьранг
@bot.message_handler(commands=['снятьранг'])
def remove_rank(message):
    if not has_permissions(message.from_user.id, '/снятьранг'):
        bot.send_message(message.chat.id, 'У вас недостаточно прав.')
        return

    tg_id = int(message.text.split()[1])
    conn = sqlite3.connect('bot_data.db')
    with conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET rank='Нету в базе' WHERE tg_id=?", (tg_id,))
        conn.commit()

    bot.send_message(message.chat.id, f'Ранг пользователя {tg_id} снят.')

# Обработчик команды /траст
@bot.message_handler(commands=['траст'])
def trust_user(message):
    if not has_permissions(message.from_user.id, '/траст'):
        bot.send_message(message.chat.id, 'У вас недостаточно прав.')
        return

    tg_id = message.text.split()[1][1:]
    bot.send_message(message.chat.id, f'Пользователь @{tg_id} получил доступ к командам "Траст".')

# Проверка мута и бана пользователей
@bot.message_handler(func=lambda message: True)
def check_mute_ban(message):
    tg_id = message.from_user.id
    conn = sqlite3.connect('bot_data.db')
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT mute_until, ban_until FROM users WHERE tg_id=?", (tg_id,))
        row = cursor.fetchone()
        mute_until = row[0]
        ban_until = row[1]

        if mute_until and int(time.time()) < mute_until:
            bot.delete_message(message.chat.id, message.message_id)
            bot.send_message(message.chat.id, f'Пользователь @{tg_id} заглушен. Причина: {row[2]}')
            return

        if ban_until and int(time.time()) < ban_until:
            bot.delete_message(message.chat.id, message.message_id)
            bot.send_message(message.chat.id, f'Пользователь @{tg_id} забанен. Причина: {row[3]}')
            return

# Запуск бота
bot.polling(none_stop=True)
