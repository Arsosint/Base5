import telebot
import sqlite3

TOKEN = '8105252956:AAHZr5AgjBDyIYh1MVkJ15hk-FZjJRKGSBM'  # Вставьте сюда ваш токен бота
OWNER_ID = 6321157988  # ID изначального владельца
bot = telebot.TeleBot(TOKEN)

conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()

# Создание таблицы пользователей, если она еще не создана
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    rank TEXT DEFAULT 'Нету в базе',
    mute_until DATETIME
)
''')
conn.commit()

def get_user_rank(user_id):
    try:
        cursor.execute("SELECT rank FROM users WHERE id = ?", (user_id,))
        rank = cursor.fetchone()
        return rank[0] if rank else 'Нету в базе'
    except Exception as e:
        print(f"Error getting user rank: {e}")
        return 'Нету в базе'  # Возвращаем, если пользователя нет

def is_owner(user_id):
    return user_id == OWNER_ID

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Это бот для Анти скам базы Stand Base.")

@bot.message_handler(commands=['Ранг'])
def set_rank(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        bot.reply_to(message, "Только владелец бота может использовать эту команду.")
        return

    args = message.text.split()[1:]  # Получаем аргументы, исключая саму команду
    if len(args) < 2:
        bot.reply_to(message, "Необходимо указать ID пользователя и новый ранг (например, /Ранг 123456789 Волонтер).")
        return

    user_id_to_change = args[0]
    new_rank = ' '.join(args[1:])  # Объединяем все части ранга

    try:
        cursor.execute("UPDATE users SET rank = ? WHERE id = ?", (new_rank, int(user_id_to_change)))
        conn.commit()
        bot.reply_to(message, f"Ранг пользователя {user_id_to_change} обновлен на '{new_rank}'.")
    except Exception as e:
        print(f"Error updating user rank: {e}")
        bot.reply_to(message, "Произошла ошибка при обновлении ранга пользователя.")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "Введите корректную команду.")

if __name__ == '__main__':
    bot.polling(non_stop=True)
