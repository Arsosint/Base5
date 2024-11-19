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

def add_scammer(user_id, reason, evidence):
    cursor.execute("UPDATE users SET rank=?, slitoscammerov=slitoscammerov+1, zaiavki=zaiavki+1, evidence=? WHERE user_id=?", ('Скаммер', evidence, user_id))
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
    
    if user_id and user_exists(user_id):
        cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
        return cursor.fetchone()
    return None

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
        user_id, rank, mute_until, ban_until, slitoscammerov, iskalivbase, zaiavki, evidence = user_data
        
        # Отображение информации о пользователе в зависимости от его ранга
        if rank in ['Админ', 'Владелец', 'Директор']:
            bot.send_photo(chat_id=message.chat.id, photo='https://imageup.ru/img58/4957060/1000006422.jpg',
                           caption=f"""
Вывожу информацию о пользователе
🆔 Id: {user_id}
🔁 Репутация: {rank}
Шанс скама: 0%
🚮 Заявки: {zaiavki}
🔍 Искали в базе: {iskalivbase}
🐝 Stand base
            """)
        elif rank == 'Гарант':
            bot.send_photo(chat_id=message.chat.id, photo='https://imageup.ru/img58/4957061/1000006419.jpg',
                           caption=f"""
Вывожу информацию о пользователе:
🆔 Id: {user_id}
🔁 Репутация: {rank}
Шанс скама: 0%
🚮 Слито Скамеров: {slitoscammerov}
🔍 Искали в базе: {iskalivbase}
🐝 Stand base
            """)
        elif rank == 'Возможно скаммер':
            chance_of_scam = 60
            bot.send_photo(chat_id=message.chat.id, photo='https://imageup.ru/img181/4957063/1000006420.jpg',
                           caption=f"""
Вывожу информацию о пользователе:
🆔 Id: {user_id}
🔁 Репутация: {rank}
🛰️ Доказательство: {evidence}
Шанс скама: {chance_of_scam}%
🚮 Слито скамеров: {slitoscammerov}
🔍 Искали в базе: {iskalivbase}
🐝 Stand base
            """)
        elif rank == 'Скаммер':
            chance_of_scam = 99
            bot.send_photo(chat_id=message.chat.id, photo='https://imageup.ru/img2/4957062/1000006417.jpg',
                           caption=f"""
Вывожу информацию о пользователе:
🆔 Id: {user_id}
🔁 Репутация: {rank}
🛰️ Доказательство: {evidence}
Шанс скама: {chance_of_scam}%
🚮 Слито скамеров: {slitoscammerov}
🔍 Искали в базе: {iskalivbase}
🐝 Stand base
            """)
        else:
            chance_of_scam = 0
            if rank == 'Волонтёр':
                chance_of_scam = 10
                bot.send_photo(chat_id=message.chat.id, photo='https://imageup.ru/img274/4957067/1000006523.jpg',
                               caption=f"""
Вывожу информацию о пользователе:
🆔 Id: {user_id}
🔁 Репутация: {rank}
Шанс скама: {chance_of_scam}%
🚮 Слито скамеров: {slitoscammerov}
🔍 Искали в базе: {iskalivbase}
🐝 Stand base
                """)
            elif rank == 'Нету в базе':
                chance_of_scam = 38
                bot.send_photo(chat_id=message.chat.id, photo='https://imageup.ru/img53/4957058/1000006423.jpg',
                               caption=f"""
Вывожу информацию о пользователе:
🆔 Id: {user_id}
🔁 Репутация: {rank}
Шанс скама: {chance_of_scam}%
🚮 Слито скамеров: {slitoscammerov}
🔍 Искали в базе: {iskalivbase}
🐝 Stand base
                """)
            elif rank == 'Стажёр':
                chance_of_scam = 20
                bot.send_photo(chat_id=message.chat.id, photo='https://imageup.ru/img263/4957066/1000006522.jpg',
                               caption=f"""
Вывожу информацию о пользователе:
🆔 Id: {user_id}
🔁 Репутация: {rank}
Шанс скама: {chance_of_scam}%
🚮 Слито скамеров: {slitoscammerov}
🔍 Искали в базе: {iskalivbase}
🐝 Stand base
                """)
            elif rank == 'Проверен гарантом':
                chance_of_scam = 23
                bot.send_photo(chat_id=message.chat.id, photo='https://imageup.ru/img233/4957059/1000006425.jpg',
                               caption=f"""
Вывожу информацию о пользователе:
🆔 Id: {user_id}
🔁 Репутация: {rank}
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
🆔 Id: {user_id}
🔁 Репутация: Нету в базе
Шанс скама: {chance_of_scam}%
🚮 Слито скамеров: 0
🔍 Искали в базе: 0
🐝 Stand base
        """)

@bot.message_handler(commands=['чекми'])
def check_me_handler(message):
    user_id = message.from_user.id
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user_data = cursor.fetchone()
    if user_data:
        user_id, rank, mute_until, ban_until, slitoscammerov, iskalivbase, zaiavki, evidence = user_data
        
        # Тот же код для отображения данных о пользователе
        if rank in ['Админ', 'Владелец', 'Директор']:
            bot.send_photo(chat_id=message.chat.id, photo='https://imageup.ru/img58/4957060/1000006422.jpg',
                           caption=f"""
Вывожу информацию о вас:
🆔 Id: {user_id}
🔁 Репутация: {rank}
Шанс скама: 0%
🚮 Заявки: {zaiavki}
🔍 Искали в базе: {iskalivbase}
🐝 Stand base
            """)
        elif rank == 'Гарант':
            bot.send_photo(chat_id=message.chat.id, photo='https://imageup.ru/img58/4957061/1000006419.jpg',
                           caption=f"""
Вывожу информацию о вас:
🆔 Id: {user_id}
🔁 Репутация: {rank}
Шанс скама: 0%
🚮 Слито Скамеров: {slitoscammerov}
🔍 Искали в базе: {iskalivbase}
🐝 Stand base
            """)
        elif rank == 'Возможно скаммер':
            chance_of_scam = 60
            bot.send_photo(chat_id=message.chat.id, photo='https://imageup.ru/img181/4957063/1000006420.jpg',
                           caption=f"""
Вывожу информацию о вас:
🆔 Id: {user_id}
🔁 Репутация: {rank}
🛰️ Доказательство: {evidence}
Шанс скама: {chance_of_scam}%
🚮 Слито скамеров: {slitoscammerov}
🔍 Искали в базе: {iskalivbase}
🐝 Stand base
            """)
        elif rank == 'Скаммер':
            chance_of_scam = 99
            bot.send_photo(chat_id=message.chat.id, photo='https://imageup.ru/img2/4957062/1000006417.jpg',
                           caption=f"""
Вывожу информацию о вас:
🆔 Id: {user_id}
🔁 Репутация: {rank}
🛰️ Доказательство: {evidence}
Шанс скама: {chance_of_scam}%
🚮 Слито скамеров: {slitoscammerov}
🔍 Искали в базе: {iskalivbase}
🐝 Stand base
            """)
        else:
            chance_of_scam = 0
            if rank == 'Волонтёр':
                chance_of_scam = 10
                bot.send_photo(chat_id=message.chat.id, photo='https://imageup.ru/img274/4957067/1000006523.jpg',
                               caption=f"""
Вывожу информацию о вас:
🆔 Id: {user_id}
🔁 Репутация: {rank}
Шанс скама: {chance_of_scam}%
🚮 Слито скамеров: {slitoscammerov}
🔍 Искали в базе: {iskalivbase}
🐝 Stand base
                """)
            elif rank == 'Нету в базе':
                chance_of_scam = 38
                bot.send_photo(chat_id=message.chat.id, photo='https://imageup.ru/img53/4957058/1000006423.jpg',
                               caption=f"""
Вывожу информацию о вас:
🆔 Id: {user_id}
🔁 Репутация: {rank}
Шанс скама: {chance_of_scam}%
🚮 Слито скамеров: {slitoscammerov}
🔍 Искали в базе: {iskalivbase}
🐝 Stand base
                """)
            elif rank == 'Стажёр':
                chance_of_scam = 20
                bot.send_photo(chat_id=message.chat.id, photo='https://imageup.ru/img263/4957066/1000006522.jpg',
                               caption=f"""
Вывожу информацию о вас:
🆔 Id: {user_id}
🔁 Репутация: {rank}
Шанс скама: {chance_of_scam}%
🚮 Слито скамеров: {slitoscammerov}
🔍 Искали в базе: {iskalivbase}
🐝 Stand base
                """)
            elif rank == 'Проверен гарантом':
                chance_of_scam = 23
                bot.send_photo(chat_id=message.chat.id, photo='https://imageup.ru/img233/4957059/1000006425.jpg',
                               caption=f"""
Вывожу информацию о вас:
🆔 Id: {user_id}
🔁 Репутация: {rank}
Шанс скама: {chance_of_scam}%
🚮 Слито скамеров: {slitoscammerov}
🔍 Искали в базе: {iskalivbase}
🐝 Stand base
                """)
    else:
        chance_of_scam = 38  # Устанавливаем шанс скама, если пользователь не найден
        bot.send_photo(chat_id=message.chat.id, photo='https://imageup.ru/img53/4957058/1000006423.jpg',
                       caption=f"""
Вывожу информацию о вас:
🆔 Id: {user_id}
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
        bot.reply_to(message, "Используйте: /мут (id или юзернейм) (время в минутах)")
        return

    user_data = get_user_data(parts[1])
    if user_data:
        user_id = user_data[0]
        duration = int(parts[2])
        set_mute(user_id, duration)
        bot.reply_to(message, f"Пользователь {user_id} замучен на {duration} минут.")
    else:
        bot.reply_to(message, "Пользователь не найден.")

@bot.message_handler(commands=['делмут'])
def delete_mute_handler(message):
    parts = message.text.split()
    if len(parts) != 5:
        bot.reply_to(message, "Используйте: /делмут (id или юзернейм) (причина) (кол-во) (время в минутах)")
        return

    user_data = get_user_data(parts[1])
    if user_data:
        user_id = user_data[0]
        reason = parts[2]
        message_count = int(parts[3])
        duration = int(parts[4])
        delete_messages(message.chat.id, user_id, message_count)  # Удаление сообщений
        set_mute(user_id, duration)
        bot.reply_to(message, f"Пользователь {user_id} замучен на {duration} минут с удалением {message_count} сообщений.")
    else:
        bot.reply_to(message, "Пользователь не найден.")

@bot.message_handler(commands=['бан'])
def ban_handler(message):
    parts = message.text.split()
    if len(parts) != 3:
        bot.reply_to(message, "Используйте: /бан (id или юзернейм) (время в минутах)")
        return

    user_data = get_user_data(parts[1])
    if user_data:
        user_id = user_data[0]
        duration = int(parts[2])
        set_ban(user_id, duration)
        bot.reply_to(message, f"Пользователь {user_id} забанен на {duration} минут.")
    else:
        bot.reply_to(message, "Пользователь не найден.")

@bot.message_handler(commands=['делбан'])
def delete_ban_handler(message):
    parts = message.text.split()
    if len(parts) != 5:
        bot.reply_to(message, "Используйте: /делбан (id или юзернейм) (причина) (кол-во) (время в минутах)")
        return

    user_data = get_user_data(parts[1])
    if user_data:
        user_id = user_data[0]
        reason = parts[2]
        message_count = int(parts[3])
        duration = int(parts[4])
        delete_messages(message.chat.id, user_id, message_count)  # Удаление сообщений
        set_ban(user_id, duration)
        bot.reply_to(message, f"Пользователь {user_id} забанен на {duration} минут с удалением {message_count} сообщений.")
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
        bot.reply_to(message, f"Мут у пользователя {user_id} снят.")
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
        bot.reply_to(message, f"Бан у пользователя {user_id} снят.")
    else:
        bot.reply_to(message, "Пользователь не найден.")

@bot.message_handler(commands=['скам'])
def add_scammer_handler(message):
    parts = message.text.split()
    if len(parts) < 4:
        bot.reply_to(message, "Используйте: /скам (id или юзернейм) (причина) (доказательства)")
        return

    user_data = get_user_data(parts[1])
    if user_data:
        user_id = user_data[0]
        reason = parts[2]
        evidence = " ".join(parts[3:])
        add_scammer(user_id, reason, evidence)
        bot.reply_to(message, f"Пользователь {user_id} добавлен в скаммеры.")
    else:
        bot.reply_to(message, "Пользователь не найден.")

@bot.message_handler(commands=['нескам'])
def remove_scammer_handler(message):
    parts = message.text.split()
    if len(parts) != 2:
        bot.reply_to(message, "Используйте: /нескам (id или юзернейм)")
        return

    user_data = get_user_data(parts[1])
    if user_data:
        user_id = user_data[0]
        remove_scammer(user_id)
        bot.reply_to(message, f"Пользователь {user_id} убран из скаммеров.")
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
        bot.reply_to(message, f"Ранг пользователя {user_id} изменен на {new_rank}.")
    else:
        bot.reply_to(message, "Пользователь не найден.")

@bot.message_handler(commands=['снятьранг'])
def remove_rank_handler(message):
    parts = message.text.split()
    if len(parts) != 2:
        bot.reply_to(message, "Используйте: /снятьранг (id или юзернейм)")
        return

    user_data = get_user_data(parts[1])
    if user_data:
        user_id = user_data[0]
        remove_rank(user_id)
        bot.reply_to(message, f"Ранг у пользователя {user_id} снят.")
    else:
        bot.reply_to(message, "Пользователь не найден.")

@bot.message_handler(commands=['траст'])
def trust_handler(message):
    parts = message.text.split()
    if len(parts) != 2:
        bot.reply_to(message, "Используйте: /траст (id или юзернейм)")
        return

    user_data = get_user_data(parts[1])
    if user_data:
        user_id = user_data[0]
        set_rank(user_id, 'Проверен гарантом')  # Установить ранг как "Проверен гарантом"
        bot.reply_to(message, f"Пользователь {user_id} стал 'Проверен гарантом'.")
    else:
        bot.reply_to(message, "Пользователь не найден.")

# Запуск бота
bot.polling()
