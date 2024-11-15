import telebot
import sqlite3
from datetime import datetime, timedelta

TOKEN = 'YOUR_TELEGRAM_BOT_API_TOKEN'  # Замените на ваш токен бота
OWNER_ID = 6321157988  # ID изначального владельца
bot = telebot.TeleBot(TOKEN)

conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()

# Создаем таблицу пользователей, если она не существует
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    rank TEXT DEFAULT 'Нету в базе',
    mute_until DATETIME
)
''')

# Проверяем и добавляем изначального владельца, если он не зарегистрирован
cursor.execute("SELECT id FROM users WHERE id = ?", (OWNER_ID,))
if not cursor.fetchone():
    cursor.execute("INSERT INTO users (id, rank) VALUES (?, 'владелец')", (OWNER_ID,))
conn.commit()

# Помощник для парсинга строки времени
def parse_time(time_str):
    unit = time_str[-1]
    if unit == 'm':
        return timedelta(minutes=int(time_str[:-1]))
    elif unit == 'h':
        return timedelta(hours=int(time_str[:-1]))
    elif unit == 'd':
        return timedelta(days=int(time_str[:-1]))
    return timedelta()

# Проверка ранга пользователя
def check_rank(user_id, ranks):
    cursor.execute("SELECT rank FROM users WHERE id = ?", (user_id,))
    user_rank = cursor.fetchone()
    if user_rank:
        return user_rank[0] in ranks
    return False

# Обновление ранга пользователя
def update_rank(user_id, rank):
    cursor.execute("UPDATE users SET rank = ? WHERE id = ?", (rank, user_id))
    conn.commit()

@bot.message_handler(commands=['траст', 'мут', 'делмут', 'оффтоп', 'бан', 'делбан', 'директор', 'владелец', 'админ', 'стажер', 'волонтер', 'гарант', 'снятьранг'])
def handle_commands(message):
    command = message.text.split()[0][1:]
    args = message.text.split()[1:]
    user_commander_id = message.from_user.id  # ID пользователя, который отправляет команду

    if len(args) >= 1:
        user_id = int(args[0])  # ID пользователя, на которого направлена команда

    if command == 'траст':
        if check_rank(user_commander_id, ['владелец', 'директор', 'админ', 'гарант']):
            update_rank(user_id, 'Проверен гарантом')
            bot.reply_to(message, f'Пользователю {user_id} выдан ранг "Проверен гарантом".')

    elif command in ['мут', 'делмут', 'оффтоп', 'бан', 'делбан']:
        if check_rank(user_commander_id, ['владелец', 'директор', 'админ']) or (command == 'оффтоп' and check_rank(user_commander_id, ['волонтер', 'стажер'])):
            time_str = args[1] if len(args) > 1 else '5m'
            reason = ' '.join(args[2:]) if len(args) > 2 else 'Не указана'
            mute_duration = parse_time(time_str)
            mute_until = datetime.now() + mute_duration
            cursor.execute("UPDATE users SET mute_until = ? WHERE id = ?", (mute_until, user_id))
            conn.commit()
            bot.reply_to(message, f'Пользователь {user_id} заблокирован до {mute_until} по причине: {reason}')

    elif command in ['директор', 'владелец', 'админ', 'стажер', 'волонтер', 'гарант', 'снятьранг']:
        if check_rank(user_commander_id, ['владелец']):
            new_rank = 'Нету в базе' if command == 'снятьранг' else command
            update_rank(user_id, new_rank)
            bot.reply_to(message, f'Пользователю {user_id} выдан ранг "{new_rank}".')

@bot.message_handler(func=lambda message: True)
def handle_all(message):
    bot.reply_to(message, "Команда не распознана или у вас недостаточно прав.")

if __name__ == '__main__':
    bot.polling(non_stop=True)
