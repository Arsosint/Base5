
import telebot
import sqlite3
from datetime import datetime, timedelta

API_TOKEN = '8105252956:AAHZr5AgjBDyIYh1MVkJ15hk-FZjJRKGSBM'
bot = telebot.TeleBot(API_TOKEN)

# Создание базы данных
conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users
                  (user_id INTEGER PRIMARY KEY, rank TEXT, mute_until DATETIME, ban_until DATETIME, 
                   slitoscammerov INTEGER DEFAULT 0, iskalivbase INTEGER DEFAULT 0, zaiavki INTEGER DEFAULT 0)''')
conn.commit()

owner_id = 6321157988

def user_exists(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    return cursor.fetchone() is not None

def add_user(user_id, rank='Нету в базе'):
    cursor.execute("INSERT INTO users (user_id, rank) VALUES (?, ?)", (user_id, rank))
    conn.commit()

add_user(owner_id, 'Владелец')

def set_mute(user_id, duration):
    mute_until = datetime.now() + timedelta(minutes=duration)
    cursor.execute("UPDATE users SET mute_until=? WHERE user_id=?", (mute_until, user_id))
    conn.commit()

def set_ban(user_id, duration):
    ban_until = datetime.now() + timedelta(minutes=duration)
    cursor.execute("UPDATE users SET ban_until=? WHERE user_id=?", (ban_until, user_id))
    conn.commit()

def add_scammer(user_id, reason, reputation, evidence):
    cursor.execute("UPDATE users SET rank=?, slitoscammerov=slitoscammerov+1, zaiavki=zaiavki+1 WHERE user_id=?", ('Скамер петух', user_id))
    cursor.execute("INSERT INTO users (user_id, rank, slitoscammerov, zaiavki) VALUES (?, 'Возможно скаммер', 0, 1)", (user_id,))
    conn.commit()

def remove_scammer(user_id, reason):
    cursor.execute("UPDATE users SET rank='Нету в базе' WHERE user_id=?", (user_id,))
    conn.commit()

def set_rank(user_id, new_rank):
    cursor.execute("UPDATE users SET rank=? WHERE user_id=?", (new_rank, user_id))
    conn.commit()

@bot.message_handler(commands=['start'])
def start_handler(message):
    user_id = message.from_user.id
    if not user_exists(user_id):
        add_user(user_id)

@bot.message_handler(commands=['чек'])
def check_handler(message):
    parts = message.text.split()
    if len(parts) != 2:
        bot.reply_to(message, "Используйте: /чек (id)")
        return
    user_id = int(parts[1])
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user_data = cursor.fetchone()
    print(user_data)  # Отладочная строка
    if user_data:
        user_id, rank, mute_until, ban_until, slitoscammerov, iskalivbase, zaiavki = user_data
        
        if rank in ['Админ', 'Владелец', 'Директор']:
            bot.send_photo(chat_id=message.chat.id, photo='https://drive.google.com/file/d/13S8glENhOfGxvctIKXV2sLzJmdwQdKPZ/view?usp=drivesdk',
                           caption=f"""
🆔 Id: {user_id}
🔁 Репутация: {rank}
Шанс скама: 0%
🚮 Заявки: {zaiavki}
🔍 Искали в базе: {iskalivbase}
🐝 Stand base
            """)
        elif rank == 'Гарант':
            bot.send_photo(chat_id=message.chat.id, photo='https://drive.google.com/file/d/13S8glENhOfGxvctIKXV2sLzJmdwQdKPZ/view?usp=drivesdk',
                           caption=f"""
🆔 Id: {user_id}
🔁 Репутация: {rank}
Шанс скама: 0%
🚮 Слито Скамеров: {slitoscammerov}
🔍 Искали в базе: {iskalivbase}
🐝 Stand base
            """)
        elif rank == 'Возможно скаммер':
            bot.send_photo(chat_id=message.chat.id, photo='https://drive.google.com/file/d/13Qugn3OBKX4r4JKScUjNj7-PYbq42JhQ/view?usp=drivesdk',
                           caption=f"""
🆔 Id: {user_id}
🔁 Репутация: {rank}
Шанс скама: 60%
🚮 Заявки: {zaiavki}
🔍 Искали в базе: {iskalivbase}
🐝 Stand base
            """)
        elif rank == 'Скамер петух':
            bot.send_photo(chat_id=message.chat.id, photo='https://drive.google.com/file/d/13gb7Sxcm1sS6eoq1e6RLD5gFHM8r_JWI/view?usp=drivesdk',
                           caption=f"""
🆔 Id: {user_id}
🔁 Репутация: {rank}
Шанс скама: 99%
🚮 Слито скамеров: {slitoscammerov}
🔍 Искали в базе: {iskalivbase}
🐝 Stand base
            """)
        else:
            chance_of_scam = 0
            if rank == 'Волонтёр':
                chance_of_scam = 10
            elif rank == 'Нету в базе':
                chance_of_scam = 38
            elif rank == 'Стажёр':
                chance_of_scam = 20
            elif rank == 'Проверен гарантом':
                chance_of_scam = 23
            bot.send_photo(chat_id=message.chat.id, photo='https://drive.google.com/file/d/13IHoB08r3irZdN3n-kG9jS4eg2Lu4WdU/view?usp=drivesdk',
                           caption=f"""
🆔 Id: {user_id}
🔁 Репутация: {rank}
Шанс скама: {chance_of_scam}%
🚮 Слито скамеров: {slitoscammerov}
🔍 Искали в базе: {iskalivbase}
🐝 Stand base
            """)
    else:
        bot.reply_to(message, "Пользователь не найден в базе.")

@bot.message_handler(commands=['чекми'])
def check_me_handler(message):
    user_id = message.from_user.id
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user_data = cursor.fetchone()
    print(user_data)  # Отладочная строка
    if user_data:
        user_id, rank, mute_until, ban_until, slitoscammerov, iskalivbase, zaiavki = user_data
        
        if rank in ['Админ', 'Владелец', 'Директор']:
            bot.send_photo(chat_id=message.chat.id, photo='https://drive.google.com/file/d/13S8glENhOfGxvctIKXV2sLzJmdwQdKPZ/view?usp=drivesdk',
                           caption=f"""
🆔 Id: {user_id}
🔁 Репутация: {rank}
Шанс скама: 0%
🚮 Заявки: {zaiavki}
🔍 Искали в базе: {iskalivbase}
🐝 Stand base
            """)
        elif rank == 'Гарант':
            bot.send_photo(chat_id=message.chat.id, photo='https://drive.google.com/file/d/13S8glENhOfGxvctIKXV2sLzJmdwQdKPZ/view?usp=drivesdk',
                           caption=f"""
🆔 Id: {user_id}
🔁 Репутация: {rank}
Шанс скама: 0%
🚮 Слито Скамеров: {slitoscammerov}
🔍 Искали в базе: {iskalivbase}
🐝 Stand base
            """)
        else:
            chance_of_scam = 0
            if rank == 'Волонтёр':
                chance_of_scam = 10
            elif rank == 'Нету в базе':
                chance_of_scam = 38
            elif rank == 'Стажёр':
                chance_of_scam = 20
            elif rank == 'Проверен гарантом':
                chance_of_scam = 23
            bot.send_photo(chat_id=message.chat.id, photo='https://drive.google.com/file/d/13IHoB08r3irZdN3n-kG9jS4eg2Lu4WdU/view?usp=drivesdk',
                           caption=f"""
🆔 Id: {user_id}
🔁 Репутация: {rank}
Шанс скама: {chance_of_scam}%
🚮 Слито скамеров: {slitoscammerov}
🔍 Искали в базе: {iskalivbase}
🐝 Stand base
            """)
    else:
        bot.reply_to(message, "Вы не найдены в базе.")

bot.polling(none_stop=True)
