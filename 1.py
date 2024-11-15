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

def is_owner(user_id):
    return user_id == OWNER_ID

def can_issue_rank(user_id):
    cursor.execute("SELECT rank FROM users WHERE id = ?", (user_id,))
    rank = cursor.fetchone()
    return rank and rank[0] in ['гарант', 'директор', 'владелец']

def can_remove_rank(user_id):
    cursor.execute("SELECT rank FROM users WHERE id = ?", (user_id,))
    rank = cursor.fetchone()
    return rank and rank[0] in ['владелец']

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Это бот для АнтиСкам Базы Stand Base")

@bot.message_handler(commands=['ранг'])
def set_rank(message):
    user_id = message.from_user.id
    args = message.text.split()[1:]  # Получаем аргументы, исключая саму команду
    
    if not is_owner(user_id):
        bot.reply_to(message, "Только владелец может использовать эту команду.")
        return

    if len(args) < 2:
        bot.reply_to(message, "Необходимо указать юзер и ранг.")
        return

    tg_username = args[0]
    new_rank = args[1]

    if new_rank not in ['волонтëр', 'админ', 'владелец', 'стажёр', 'гарант', 'директор']:
        bot.reply_to(message, "Некорректный ранг. Доступные ранги: волонтëр, админ, владелец, стажёр, гарант, директор.")
        return

    cursor.execute("INSERT OR IGNORE INTO users (username, rank) VALUES (?, 'Нету в базе')", (tg_username,))
    cursor.execute("UPDATE users SET rank = ? WHERE username = ?", (new_rank, tg_username))
    conn.commit()

    bot.reply_to(message, f"пользователь {tg_username} повышен до {new_rank}.")

@bot.message_handler(commands=['снятьранг'])
def remove_rank(message):
    user_id = message.from_user.id
    if not can_remove_rank(user_id):
        bot.reply_to(message, "Только владелец может использовать эту команду.")
        return

    args = message.text.split()[1:]
    if len(args) < 1:
        bot.reply_to(message, "Необходимо указать юзер .")
        return

    tg_username = args[0]
    
    cursor.execute("UPDATE users SET rank = 'Нету в базе' WHERE username = ?", (tg_username,))
    conn.commit()

    bot.reply_to(message, f"Ранг пользователя {tg_username} снят и понижен до 'Нету в базе'.")

@bot.message_handler(commands=['траст'])
def trust_user(message):
    user_id = message.from_user.id
    if not can_issue_rank(user_id):
        bot.reply_to(message, "У вас нет прав для использования этой команды.")
        return

    args = message.text.split()[1:]
    if len(args) < 1:
        bot.reply_to(message, "Необходимо указать юзер .")
        return

    tg_username = args[0]
    
    cursor.execute("INSERT OR IGNORE INTO users (username, rank) VALUES (?, 'Нету в базе')", (tg_username,))
    cursor.execute("UPDATE users SET rank = 'Проверен Гарантом' WHERE username = ?", (tg_username,))
    conn.commit()

    bot.reply_to(message, f"Пользователю {tg_username} выдан ранг 'Проверен Гарантом'.")

@bot.message_handler(func=lambda message: True)
def catch_all(message):
    bot.reply_to(message, " Ошибка Данной Команды не существует")

if __name__ == '__main__':
    bot.polling(non_stop=True)
