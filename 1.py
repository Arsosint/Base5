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
    cursor.execute("UPDATE users SET rank=?, slitoscammerov=slitoscammerov+1, zaiavki=zaiavki+1 WHERE user_id=?", ('Скаммер', user_id))
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
    # ... (предыдущий код)
    cursor.execute("UPDATE users SET iskalivbase=iskalivbase+1 WHERE user_id=?", (user_id,))
    conn.commit()

@bot.message_handler(commands=['чекми'])
def check_me_handler(message):
    # ... (предыдущий код)
    cursor.execute("UPDATE users SET iskalivbase=iskalivbase+1 WHERE user_id=?", (user_id,))
    conn.commit()

@bot.message_handler(commands=['делбан'])
def del_ban_handler(message):
    parts = message.text.split()
    if len(parts) != 5:
        bot.reply_to(message, "Используйте: /делбан (id) (причина) (время) (кол-во)")
        return
    user_id = int(parts[1])
    reason = ' '.join(parts[2:-2])
    duration = int(parts[-2])
    delete_count = int(parts[-1])
    
    # Проверяем права пользователя
    if message.from_user.id in [owner_id]:
        set_ban(user_id, duration)
        bot.delete_messages(chat_id=message.chat.id, message_ids=[message.message_id])
        bot.delete_messages(chat_id=message.chat.id, message_ids=range(message.message_id - delete_count, message.message_id))
        bot.send_message(chat_id=message.chat.id, text=f"Пользователь {user_id} забанен на {duration} минут. Причина: {reason}")
    else:
        bot.reply_to(message, "У вас недостаточно прав для выполнения этой команды.")

@bot.message_handler(commands=['делмут'])
def del_mute_handler(message):
    parts = message.text.split()
    if len(parts) != 5:
        bot.reply_to(message, "Используйте: /делмут (id) (причина) (время) (кол-во)")
        return
    user_id = int(parts[1])
    reason = ' '.join(parts[2:-2])
    duration = int(parts[-2])
    delete_count = int(parts[-1])
    
    # Проверяем права пользователя
    if message.from_user.id in [owner_id]:
        set_mute(user_id, duration)
        bot.delete_messages(chat_id=message.chat.id, message_ids=[message.message_id])
        bot.delete_messages(chat_id=message.chat.id, message_ids=range(message.message_id - delete_count, message.message_id))
        bot.send_message(chat_id=message.chat.id, text=f"Пользователь {user_id} заглушен на {duration} минут. Причина: {reason}")
    else:
        bot.reply_to(message, "У вас недостаточно прав для выполнения этой команды.")

@bot.message_handler(commands=['мут'])
def mute_handler(message):
    parts = message.text.split()
    if len(parts) != 4:
        bot.reply_to(message, "Используйте: /мут (id) (причина) (время)")
        return
    user_id = int(parts[1])
    reason = ' '.join(parts[2:-1])
    duration = int(parts[-1])
    
    # Проверяем права пользователя
    if message.from_user.id in [owner_id]:
        set_mute(user_id, duration)
        bot.reply_to(message, f"Пользователь {user_id} заглушен на {duration} минут. Причина: {reason}")
    else:
        bot.reply_to(message, "У вас недостаточно прав для выполнения этой команды.")

@bot.message_handler(commands=['бан'])
def ban_handler(message):
    parts = message.text.split()
    if len(parts) != 4:
        bot.reply_to(message, "Используйте: /бан (id) (причина) (время)")
        return
    user_id = int(parts[1])
    reason = ' '.join(parts[2:-1])
    duration = int(parts[-1])
    
    # Проверяем права пользователя
    if message.from_user.id in [owner_id]:
        set_ban(user_id, duration)
        bot.reply_to(message, f"Пользователь {user_id} забанен на {duration} минут. Причина: {reason}")
    else:
        bot.reply_to(message, "У вас недостаточно прав для выполнения этой команды.")

@bot.message_handler(commands=['ранг'])
def set_rank_handler(message):
    parts = message.text.split()
    if len(parts) != 3:
        bot.reply_to(message, "Используйте: /ранг (id) (ранг)")
        return
    user_id = int(parts[1])
    new_rank = parts[2]
    
    # Проверяем права пользователя
    if message.from_user.id in [owner_id]:
        set_rank(user_id, new_rank)
        bot.reply_to(message, f"Пользователю {user_id} установлен ранг: {new_rank}")
    else:
        bot.reply_to(message, "У вас недостаточно прав для выполнения этой команды.")

@bot.message_handler(commands=['снятьранг'])
def remove_rank_handler(message):
    parts = message.text.split()
    if len(parts) != 2:
        bot.reply_to(message, "Используйте: /снятьранг (id)")
        return
    user_id = int(parts[1])
    
    # Проверяем права пользователя
    if message.from_user.id in [owner_id]:
        set_rank(user_id, 'Нету в базе')
        bot.reply_to(message, f"Ранг пользователя {user_id} снижен до 'Нету в базе'")
    else:
        bot.reply_to(message, "У вас недостаточно прав для выполнения этой команды.")

@bot.message_handler(commands=['Скам'])
def add_scammer_handler(message):
    parts = message.text.split()
    if len(parts) != 5:
        bot.reply_to(message, "Используйте: /Скам (id) (причина) (доказательство) (репутация)")
        return
    user_id = int(parts[1])
    reason = ' '.join(parts[2:4])
    evidence = parts[4]
    reputation = 'Скаммер'
    
    # Проверяем права пользователя
    if message.from_user.id in [owner_id]:
        add_scammer(user_id, reason, reputation, evidence)
        bot.reply_to(message, f"Пользователю {user_id} присвоен ранг 'Скаммер'. Причина: {reason}, Доказательство: {evidence}")
    else:
        bot.reply_to(message, "У вас недостаточно прав для выполнения этой команды.")

@bot.message_handler(commands=['нескам'])
def remove_scammer_handler(message):
    parts = message.text.split()
    if len(parts) != 2:
        bot.reply_to(message, "Используйте: /нескам (id)")
        return
    user_id = int(parts[1])
    
    # Проверяем права пользователя
    if message.from_user.id in [owner_id]:
        remove_scammer(user_id, "Исправлен")
        bot.reply_to(message, f"Пользователь {user_id} удален из базы как скаммер.")
    else:
        bot.reply_to(message, "У вас недостаточно прав для выполнения этой команды.")

@bot.message_handler(commands=['траст'])
def trust_handler(message):
    parts = message.text.split()
    if len(parts) != 2:
        bot.reply_to(message, "Используйте: /траст (id)")
        return
    user_id = int(parts[1])
    
    # Проверяем права пользователя
    if message.from_user.id in [owner_id]:
        set_rank(user_id, 'Проверен гарантом')
        bot.reply_to(message, f"Пользователю {user_id} выдан ранг 'Проверен гарантом'.")
    else:
        bot.reply_to(message, "У вас недостаточно прав для выполнения этой команды.")

@bot.message_handler(commands=['спасибо'])
def thank_handler(message):
    parts = message.text.split()
    if len(parts) != 2:
        bot.reply_to(message, "Используйте: /спасибо (id)")
        return
    user_id = int(parts[1])
    
    # Проверяем права пользователя
    if message.from_user.id in [owner_id]:
        add_scammer(user_id, "Благодарность", 0, "")
        bot.reply_to(message, f"Пользователю {user_id} добавлен 1 к 'Слито Скамеров'.")
    else:
        bot.reply_to(message, "У вас недостаточно прав для выполнения этой команды.")

@bot.message_handler(commands=['оффтоп'])
def offtopic_handler(message):
    parts = message.text.split()
    if len(parts) != 2:
        bot.reply_to(message, "Используйте: /оффтоп (id)")
        return
    user_id = int(parts[1])
    
    # Проверяем права пользователя
    if message.from_user.id in [owner_id]:
        set_mute(user_id, 5)
        bot.reply_to(message, f"Пользователь {user_id} заглушен на 5 минут.")
    else:
        bot.reply_to(message, "У вас недостаточно прав для выполнения этой команды.")

bot.polling(none_stop=True)
