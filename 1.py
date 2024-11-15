import telebot
import sqlite3
import time
from datetime import datetime, timedelta

# Инициализация бота
TOKEN = '8105252956:AAHZr5AgjBDyIYh1MVkJ15hk-FZjJRKGSBM'
bot = telebot.TeleBot(TOKEN)

# Инициализация базы данных
conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()

# Создание таблицы пользователей (если она не существует)
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    rank TEXT,
    mute_until DATETIME,
    ban_until DATETIME
)''')
conn.commit()

# Утилита для проверки привилегий
def has_permissions(user_id, command):
    cursor.execute('SELECT rank FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    if user:
        rank = user[0]
        if rank == 'Владелец':
            return True
        elif rank == 'Директор' and command not in ['/ранг', '/снять_ранг']:
            return True
        elif rank == 'Гарант' and command not in ['/бан', '/делбан', '/делмут', '/мут', '/ранг', '/снять_ранг']:
            return True
        elif rank == 'Админ':
            return command not in ['/траст', '/делбан', '/делмут', '/ранг', '/снять_ранг']
        elif rank in ['Стажёр', 'Волонтёр']:
            return command in ['/бан', '/делбан', '/делмут', '/мут']
    return False

@bot.message_handler(commands=['мут'])
def mute_user(message):
    # Обработка команды /мут
    args = message.text.split()
    if len(args) < 4:
        return bot.reply_to(message, "Использование: /мут (юзер) (причина) (время)")

    user_id = args[1]
    reason = args[2]
    time_limit = int(args[3])  # время в минутах

    mute_until = datetime.now() + timedelta(minutes=time_limit)

    cursor.execute('UPDATE users SET mute_until = ? WHERE user_id = ?', (mute_until, user_id))
    conn.commit()
    
    bot.reply_to(message, f"Пользователь {user_id} был замучен на {time_limit} минут(ы). Причина: {reason}")

# Другие команды можно добавить аналогично

@bot.message_handler(commands=['ранг'])
def set_rank(message):
    # Обработка команды /ранг
    args = message.text.split()
    if len(args) < 3:
        return bot.reply_to(message, "Использование: /ранг (id) (ранг)")

    user_id = int(args[1])
    rank = args[2]

    cursor.execute('INSERT OR REPLACE INTO users (user_id, rank) VALUES (?, ?)', (user_id, rank))
    conn.commit()

    bot.reply_to(message, f"Ранг пользователя {user_id} установлен на {rank}")

@bot.message_handler(commands=['снять_ранг'])
def remove_rank(message):
    args = message.text.split()
    if len(args) < 2:
        return bot.reply_to(message, "Использование: /снять_ранг (id)")

    user_id = int(args[1])

    cursor.execute('UPDATE users SET rank = NULL WHERE user_id = ?', (user_id,))
    conn.commit()

    bot.reply_to(message, f"Ранг пользователя {user_id} снят")

# Запуск бота
bot.polling(none_stop=True)
    
