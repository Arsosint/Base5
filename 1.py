import telebot
import sqlite3
from datetime import datetime, timedelta

# Замените '8105252956:AAHZr5AgjBDyIYh1MVkJ15hk-FZjJRKGSBM' на токен вашего бота
API_TOKEN = '8105252956:AAHZr5AgjBDyIYh1MVkJ15hk-FZjJRKGSBM'
bot = telebot.TeleBot(API_TOKEN)

# Создание базы данных
conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users
                  (user_id INTEGER PRIMARY KEY, rank TEXT, mute_until DATETIME, ban_until DATETIME, 
                   slitoscammerov INTEGER DEFAULT 0, iskalivbase INTEGER DEFAULT 0, zaiavki INTEGER DEFAULT 0)''')
conn.commit()

# Изначальный владелец
owner_id = 6321157988
add_user(owner_id, 'Владелец')

def user_exists(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    return cursor.fetchone() is not None

def add_user(user_id, rank='Нету в базе'):
    cursor.execute("INSERT INTO users (user_id, rank) VALUES (?, ?)", (user_id, rank))
    conn.commit()

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

@bot.message_handler(commands=['ранг'])
def rank_handler(message):
    parts = message.text.split()
    if len(parts) != 3:
        bot.reply_to(message, "Используйте: /ранг (id) (ранг)")
        return
    user_id = int(parts[1])
    new_rank = parts[2]
    set_rank(user_id, new_rank)
    bot.reply_to(message, f"Пользователю {user_id} установлен ранг {new_rank}")

@bot.message_handler(commands=['траст'])
def trust_handler(message):
    parts = message.text.split()
    if len(parts) != 3:
        bot.reply_to(message, "Используйте: /траст (id) (ранг)")
        return
    user_id = int(parts[1])
    new_rank = parts[2]
    set_rank(user_id, new_rank)
    bot.reply_to(message, f"Пользователь {user_id} получил ранг {new_rank}")

@bot.message_handler(commands=['скам'])
def scam_handler(message):
    parts = message.text.split()
    if len(parts) != 5:
        bot.reply_to(message, "Используйте: /скам (id) (причина) (репутация) (доказательства)")
        return
    user_id = int(parts[1])
    reason = parts[2]
    reputation = parts[3]
    evidence = parts[4]
    add_scammer(user_id, reason, reputation, evidence)
    bot.reply_to(message, f"Пользователь {user_id} добавлен в базу как скамер")

@bot.message_handler(commands=['нескам'])
def unscam_handler(message):
    parts = message.text.split()
    if len(parts) != 3:
        bot.reply_to(message, "Используйте: /нескам (id) (причина)")
        return
    user_id = int(parts[1])
    reason = parts[2]
    remove_scammer(user_id, reason)
    bot.reply_to(message, f"Пользователь {user_id} удален из базы скамеров")

@bot.message_handler(commands=['мут'])
def mute_handler(message):
    parts = message.text.split()
    if len(parts) != 4:
        bot.reply_to(message, "Используйте: /мут (id) (причина) (время в минутах)")
        return
    user_id = int(parts[1])
    reason = parts[2]
    duration = int(parts[3])
    set_mute(user_id, duration)
    bot.reply_to(message, f"Пользователь {user_id} замучен на {duration} минут(ы) по причине: {reason}")

@bot.message_handler(commands=['делмут'])
def del_mute_handler(message):
    parts = message.text.split()
    if len(parts) != 5:
        bot.reply_to(message, "Используйте: /делмут (id) (кол-во) (причина) (время в минутах)")
        return
    user_id = int(parts[1])
    message_count = int(parts[2])
    reason = parts[3]
    duration = int(parts[4])
    set_mute(user_id, duration)
    # Логика удаления сообщений
    bot.reply_to(message, f"Пользователь {user_id} замучен на {duration} минут(ы) с удалением {message_count} сообщений по причине: {reason}")

@bot.message_handler(commands=['бан'])
def ban_handler(message):
    parts = message.text.split()
    if len(parts) != 3:
        bot.reply_to(message, "Используйте: /бан (id) (причина)")
        return
    user_id = int(parts[1])
    reason = parts[2]
    set_ban(user_id, 0)
    bot.reply_to(message, f"Пользователь {user_id} забанен по причине: {reason}")

@bot.message_handler(commands=['оффтоп'])
def offtopic_handler(message):
    parts = message.text.split()
    if len(parts) != 3:
        bot.reply_to(message, "Используйте: /оффтоп (id) (причина)")
        return
    user_id = int(parts[1])
    reason = parts[2]
    set_mute(user_id, 5)
    bot.reply_to(message, f"Пользователь {user_id} замучен на 5 минут по причине: {reason}")

@bot.message_handler(commands=['снятьранг'])
def remove_rank_handler(message):
    user_id = message.from_user.id
    set_rank(user_id, 'Нету в базе')
    bot.reply_to(message, "Ваш ранг снижен до 'Нету в базе'.")

@bot.message_handler(commands=['спасибо'])
def thank_handler(message):
    parts = message.text.split()
    if len(parts) != 2:
        bot.reply_to(message, "Используйте: /спасибо (id)")
        return
    user_id = int(parts[1])
    cursor.execute("UPDATE users SET slitoscammerov=slitoscammerov+1 WHERE user_id=?", (user_id,))
    conn.commit()
    bot.reply_to(message, f"Пользователю {user_id} добавлен 1 к счетчику 'Слито скамеров'.")

@bot.message_handler(commands=['чек'])
def check_handler(message):
    parts = message.text.split()
    if len(parts) != 2:
        bot.reply_to(message, "Используйте: /чек (id)")
        return
    user_id = int(parts[1])
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user_data = cursor.fetchone()
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
