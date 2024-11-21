import telebot
import sqlite3
from datetime import datetime, timedelta

API_TOKEN = '8105252956:AAHZr5AgjBDyIYh1MVkJ15hk-FZjJRKGSBM'  # Замените на ваш токен
bot = telebot.TeleBot(API_TOKEN)

# Создание базы данных
conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users
                  (user_id INTEGER PRIMARY KEY, username TEXT, rank TEXT DEFAULT 'Нету в базе', mute_until DATETIME, ban_until DATETIME, 
                   slitoscammerov INTEGER DEFAULT 0, iskalivbase INTEGER DEFAULT 0, zaiavki INTEGER DEFAULT 0, evidence TEXT DEFAULT '')''')
conn.commit()

owner_id = 6321157988
owner_rank = 'Владелец'  # Установите ранг владельца

def user_exists(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    return cursor.fetchone() is not None

def add_user(user_id, username, rank='Нету в базе'):
    cursor.execute("INSERT INTO users (user_id, username, rank) VALUES (?, ?, ?)", (user_id, username, rank))
    conn.commit()

def get_user_id_by_username(username):
    cursor.execute("SELECT user_id FROM users WHERE username=?", (username,))
    result = cursor.fetchone()
    return result[0] if result else None

def set_mute(user_id, duration):
    mute_until = datetime.now() + timedelta(minutes=duration)
    cursor.execute("UPDATE users SET mute_until=? WHERE user_id=?", (mute_until, user_id))
    conn.commit()

def remove_mute(user_id):
    cursor.execute("UPDATE users SET mute_until=NULL WHERE user_id=?", (user_id,))
    conn.commit()

def set_ban(user_id, duration):
    ban_until = datetime.now() + timedelta(minutes=duration)
    cursor.execute("UPDATE users SET ban_until=? WHERE user_id=?", (ban_until, user_id))
    conn.commit()

def remove_ban(user_id):
    cursor.execute("UPDATE users SET ban_until=NULL WHERE user_id=?", (user_id,))
    conn.commit()

def delete_messages(chat_id, user_id, count):
    messages = bot.get_chat_history(chat_id, limit=count)  # Получаем последние сообщения в чате
    for message in messages:
        if message.from_user.id == user_id:
            bot.delete_message(chat_id, message.message_id)  # Удаляем сообщение

def add_scammer(user_id, rank, reason, evidence):
    cursor.execute("UPDATE users SET rank=?, slitoscammerov=slitoscammerov+1, zaiavki=zaiavki+1, evidence=? WHERE user_id=?", (rank, evidence, user_id))
    cursor.execute("UPDATE users SET evidence = evidence || ? WHERE user_id=?", (f", {evidence}", user_id))
    conn.commit()

def remove_scammer(user_id):
    cursor.execute("UPDATE users SET rank='Нету в базе' WHERE user_id=?", (user_id,))
    conn.commit()

def set_rank(user_id, new_rank):
    cursor.execute("UPDATE users SET rank=? WHERE user_id=?", (new_rank, user_id))
    conn.commit()

def remove_rank(user_id):
    cursor.execute("UPDATE users SET rank='Нету в базе' WHERE user_id=?", (user_id,))
    conn.commit()

def increment_search_count(user_id):
    cursor.execute("UPDATE users SET iskalivbase=iskalivbase+1 WHERE user_id=?", (user_id,))
    conn.commit()

@bot.message_handler(commands=['start'])
def start_handler(message):
    user_id = message.from_user.id
    username = message.from_user.username or "Нету в базе"
    if not user_exists(user_id):
        add_user(user_id, username)

def get_user_data(identifier):
    user_id = None
    if identifier.isdigit():
        user_id = int(identifier)
    else:
        user_id = get_user_id_by_username(identifier)

    if user_id:
        if user_exists(user_id):
            cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
            return cursor.fetchone()
        else:
            print(f"Пользователь с ID {user_id} не найден в базе данных.")
    else:
        print(f"Неверный идентификатор: {identifier}")

    return None

@bot.message_handler(commands=['чек'])
def check_handler(message):
    parts = message.text.split()
    if len(parts) != 2:
        bot.reply_to(message, "Используйте: /чек (id или юзернейм)")
        return
    user_data = get_user_data(parts[1])
    if user_data:
        user_id, username, rank, mute_until, ban_until, slitoscammerov, iskalivbase, zaiavki, evidence = user_data
        
        # Увеличиваем счетчик поиска
        increment_search_count(user_id)

        # Логика отображения информации о пользователе
        chance_of_scam = 0  # По умолчанию
        if rank in ['Админ', 'Владелец', 'Директор']:
            photo_url = 'https://imageup.ru/img58/4957060/1000006422.jpg'
        elif rank == 'Гарант':
            photo_url = 'https://imageup.ru/img58/4957061/1000006419.jpg'
        elif rank == 'Возможно скаммер':
            chance_of_scam = 60
            photo_url = 'https://imageup.ru/img181/4957063/1000006420.jpg'
        elif rank == 'Скаммер':
            chance_of_scam = 99
            photo_url = 'https://imageup.ru/img2/4957062/1000006417.jpg'
        elif rank == 'Волонтёр':
            chance_of_scam = 10
            photo_url = 'https://imageup.ru/img274/4957067/1000006523.jpg'
        elif rank == 'Стажёр':
            chance_of_scam = 20
            photo_url = 'https://imageup.ru/img263/4957066/1000006522.jpg'
        elif rank == 'Проверен гарантом':
            chance_of_scam = 23
            photo_url = 'https://imageup.ru/img233/4957059/1000006425.jpg'
        else:
            chance_of_scam = 38
            photo_url = 'https://imageup.ru/img53/4957058/1000006423.jpg'

        bot.send_photo(chat_id=message.chat.id, photo=photo_url,
                       caption=f"""
Вывожу информацию о пользователе:
🆔 Id: {user_id}
👤 Юзернейм: {username}
🔁 Репутация: {rank}
🛰️ Доказательство: {evidence if rank in ['Скаммер', 'Возможно скаммер'] else 'Нет'}
Шанс скама: {chance_of_scam}%
🚮 Слито скамеров: {slitoscammerov}
🔍 Искали в базе: {iskalivbase}
🐝 Stand base
            """)
    else:
        chance_of_scam = 38  # Устанавливаем шанс скама, если пользователь не найден
        bot.send_photo(chat_id=message.chat.id, photo='https://imageup.ru/img53/4957058/1000006423.jpg',
                       caption=f"""
Вывожу информацию о пользователе:
🆔 Id: Не найден
🔁 Репутация: Нету в базе
Шанс скама: {chance_of_scam}%
🚮 Слито скамеров: 0
🔍 Искали в базе: 0
🐝 Stand base
        """)

@bot.message_handler(commands=['чекми'])
def check_me_handler(message):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)
    if user_data:
        check_handler(message)
    else:
        chance_of_scam = 38  # Устанавливаем шанс скама, если пользователь не найден
        bot.send_photo(chat_id=message.chat.id, photo='https://imageup.ru/img53/4957058/1000006423.jpg',
                       caption=f"""
Вывожу информацию о вас:
🆔 Id: Не найден
🔁 Репутация: Нету в базе
Шанс скама: {chance_of_scam}%
🚮 Слито скамеров: 0
🔍 Искали в базе: 0
🐝 Stand base
        """)

@bot.message_handler(commands=['мут'])
def mute_handler(message):
    parts = message.text.split()
    if len(parts) != 3:
        bot.reply_to(message, "Используйте: /мут (id или юзернейм) (длительность в минутах)")
        return
    user_data = get_user_data(parts[1])
    if user_data:
        user_id = user_data[0]
        duration = int(parts[2])
        set_mute(user_id, duration)
        bot.reply_to(message, f"Пользователь {parts[1]} замучен на {duration} минут.")
    else:
        bot.reply_to(message, "Пользователь не найден.")

@bot.message_handler(commands=['делмут'])
def del_mute_handler(message):
    parts = message.text.split()
    if len(parts) != 5:
        bot.reply_to(message, "Используйте: /делмут (id или юзернейм) (кол-во) (причина) (время в минутах)")
        return
    user_data = get_user_data(parts[1])
    if user_data:
        user_id = user_data[0]
        count = int(parts[2])
        reason = parts[3]
        duration = int(parts[4])
        
        # Устанавливаем мут и удаляем сообщения
        set_mute(user_id, duration)
        delete_messages(message.chat.id, user_id, count)
        bot.reply_to(message, f"Пользователь {parts[1]} замучен на {duration} минут. Удалено {count} сообщений. Причина: {reason}.")
    else:
        bot.reply_to(message, "Пользователь не найден.")

@bot.message_handler(commands=['бан'])
def ban_handler(message):
    parts = message.text.split()
    if len(parts) != 3:
        bot.reply_to(message, "Используйте: /бан (id или юзернейм) (длительность в минутах)")
        return
    user_data = get_user_data(parts[1])
    if user_data:
        user_id = user_data[0]
        duration = int(parts[2])
        set_ban(user_id, duration)
        bot.reply_to(message, f"Пользователь {parts[1]} забанен на {duration} минут.")
    else:
        bot.reply_to(message, "Пользователь не найден.")

@bot.message_handler(commands=['делбан'])
def del_ban_handler(message):
    parts = message.text.split()
    if len(parts) != 5:
        bot.reply_to(message, "Используйте: /делбан (id или юзернейм) (кол-во) (причина) (время в минутах)")
        return
    user_data = get_user_data(parts[1])
    if user_data:
        user_id = user_data[0]
        count = int(parts[2])
        reason = parts[3]
        duration = int(parts[4])
        
        # Устанавливаем бан и удаляем сообщения
        set_ban(user_id, duration)
        delete_messages(message.chat.id, user_id, count)
        bot.reply_to(message, f"Пользователь {parts[1]} забанен на {duration} минут. Удалено {count} сообщений. Причина: {reason}.")
    else:
        bot.reply_to(message, "Пользователь не найден.")

@bot.message_handler(commands=['скам'])
def scam_handler(message):
    parts = message.text.split()
    if len(parts) != 5:
        bot.reply_to(message, "Используйте: /скам (id) (репутация) (причина) (доказательство)")
        return
    user_data = get_user_data(parts[1])
    if user_data:
        user_id = user_data[0]
        rank = parts[2]
        reason = parts[3]
        evidence = parts[4]
        add_scammer(user_id, rank, reason, evidence)
        bot.reply_to(message, f"Пользователь {parts[1]} добавлен в скаммеры. Репутация: {rank}. Причина: {reason}. Доказательства: {evidence}")
    else:
        bot.reply_to(message, "Пользователь не найден.")

@bot.message_handler(commands=['нескам'])
def unscam_handler(message):
    parts = message.text.split()
    if len(parts) != 2:
        bot.reply_to(message, "Используйте: /нескам (id или юзернейм)")
        return
    user_data = get_user_data(parts[1])
    if user_data:
        user_id = user_data[0]
        remove_scammer(user_id)
        bot.reply_to(message, f"Пользователь {parts[1]} убран из скаммеров.")
    else:
        bot.reply_to(message, "Пользователь не найден.")

@bot.message_handler(commands=['ранг'])
def set_rank_handler(message):
    parts = message.text.split()
    if len(parts) != 3:
        bot.reply_to(message, "Используйте: /ранг (id или юзернейм) (новый ранг)")
        return
    user_data = get_user_data(parts[1])
    if user_data:
        user_id = user_data[0]
        new_rank = parts[2]
        set_rank(user_id, new_rank)
        bot.reply_to(message, f"Ранг пользователя {parts[1]} установлен на {new_rank}.")
    else:
        bot.reply_to(message, "Пользователь не найден.")

@bot.message_handler(commands=['анмут'])
def unmute_handler(message):
    parts = message.text.split()
    if len(parts) != 2:
        bot.reply_to(message, "Используйте: /анмут (id или юзернейм)")
        return
    user_data = get_user_data(parts[1])
    if user_data:
        user_id = user_data[0]
        remove_mute(user_id)
        bot.reply_to(message, f"Пользователь {parts[1]} размучен.")
    else:
        bot.reply_to(message, "Пользователь не найден.")

@bot.message_handler(commands=['анбан'])
def unban_handler(message):
    parts = message.text.split()
    if len(parts) != 2:
        bot.reply_to(message, "Используйте: /анбан (id или юзернейм)")
        return
    user_data = get_user_data(parts[1])
    if user_data:
        user_id = user_data[0]
        remove_ban(user_id)
        bot.reply_to(message, f"Пользователь {parts[1]} разбанен.")
    else:
        bot.reply_to(message, "Пользователь не найден.")

# Запуск бота
bot.polling()
