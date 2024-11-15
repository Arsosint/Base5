import telebot
import sqlite3
from datetime import datetime, timedelta

TOKEN = '8105252956:AAHZr5AgjBDyIYh1MVkJ15hk-FZjJRKGSBM'  # Замените на ваш токен бота
OWNER_ID = 6321157988  # ID изначального владельца
bot = telebot.TeleBot(TOKEN)

conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    rank TEXT DEFAULT 'Нету в базе',
    mute_until DATETIME
)
''')
conn.commit()

def parse_time(time_str):
    unit = time_str[-1]
    number = int(time_str[:-1])
    if unit == 'm':
        return timedelta(minutes=number)
    elif unit == 'h':
        return timedelta(hours=number)
    elif unit == 'd':
        return timedelta(days=number)
    return None

def get_user_rank(user_id_or_username):
    try:
        # Если передан числовой ID
        user_id = int(user_id_or_username)
        cursor.execute("SELECT rank FROM users WHERE id = ?", (user_id,))
    except ValueError:
        # Если передан username
        cursor.execute("SELECT rank FROM users WHERE username = ?", (user_id_or_username,))
    
    rank = cursor.fetchone()
    return rank[0] if rank else None

def update_rank(user_id_or_username, rank):
    try:
        user_id = int(user_id_or_username)
        cursor.execute("UPDATE users SET rank = ? WHERE id = ?", (rank, user_id))
    except ValueError:
        cursor.execute("UPDATE users SET rank = ? WHERE username = ?", (rank, user_id_or_username))
    conn.commit()

# Аналогично адаптируйте остальные функции
# ...

@bot.message_handler(commands=['траст', 'мут', 'делмут', 'оффтоп', 'бан', 'делбан', 'директор', 'владелец', 'админ', 'стажер', 'волонтер', 'гарант', 'снятьранг'])
def handle_commands(message):
    command = message.text.split()[0][1:]
    args = message.text.split()[1:]
    user_commander_id = message.from_user.id

    if len(args) < 1:
        bot.reply_to(message, f'Не достаточно аргументов для выполнения команды /{command}.')
        return

    user_id_or_username = args[0]
    current_rank = get_user_rank(user_commander_id)

    if command == 'траст' and current_rank in ['владелец', 'директор', 'админ', 'гарант']:
        update_rank(user_id_or_username, 'Проверен гарантом')
        bot.reply_to(message, f'Пользователю {user_id_or_username} выдан ранг "Проверен гарантом".')

    # Продолжайте обрабатывать другие команды аналогично
        
    elif command in ['директор', 'владелец', 'админ', 'стажер', 'волонтер', 'гарант', 'снятьранг'] and current_rank == 'владелец':
        new_rank = 'Нету в базе' if command == 'снятьранг' else command
        update_rank(user_id_or_username, new_rank)
        bot.reply_to(message, f'Пользователю {user_id_or_username} выдан ранг "{new_rank}".')

# ...

if __name__ == '__main__':
    bot.polling(non_stop=True)
