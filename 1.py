import telebot
import sqlite3

TOKEN = '8105252956:AAHZr5AgjBDyIYh1MVkJ15hk-FZjJRKGSBM'  # Вставьте сюда ваш токен бота
OWNER_ID = 6321157988  # ID владельца бота
bot = telebot.TeleBot(TOKEN)

conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()

# Создание таблицы пользователей, если она еще не создана
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    rank TEXT DEFAULT 'Нету в базе'
)
''')
conn.commit()

def get_user_rank(user_id):
    cursor.execute("SELECT rank FROM users WHERE id = ?", (user_id,))
    result = cursor.fetchone()
    if result:
        return result[0]
    return None

def is_owner(user_id):
    user_rank = get_user_rank(user_id)
    return user_rank == 'владелец' or user_id == OWNER_ID

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Это бот для АнтиСкам Базы Stand Base")
    bot.reply_to(message, f"Ваш user ID: {message.from_user.id}")

@bot.message_handler(commands=['ранг'])
def set_rank(message):
    user_id = message.from_user.id
    args = message.text.split()[1:]  # Получаем аргументы, исключая саму команду
    
    if not is_owner(user_id):
        bot.reply_to(message, "Только владелец может использовать эту команду.")
        return

    if len(args) < 2:
        bot.reply_to(message, "Необходимо указать username и ранг.")
        return

    tg_username, new_rank = args

    if new_rank not in ['волонтёр', 'админ', 'владелец', 'стажёр', 'гарант', 'директор']:
        bot.reply_to(message, "Некорректный ранг. Доступные ранги: волонтёр, админ, владелец, стажёр, гарант, директор.")
        return

    cursor.execute("INSERT OR IGNORE INTO users (username, rank) VALUES (?, 'Нету в базе')", (tg_username,))
    cursor.execute("UPDATE users SET rank = ? WHERE username = ?", (new_rank, tg_username))
    conn.commit()

    bot.reply_to(message, f"Пользователь {tg_username} повышен до {new_rank}.")

@bot.message_handler(func=lambda message: True)
def catch_all(message):
    bot.reply_to(message, 'Ошибка: данной команды не существует.')

if __name__ == '__main__':
    bot.polling(non_stop=True)
