import telebot
from telebot import types

API_TOKEN = '8105252956:AAHZr5AgjBDyIYh1MVkJ15hk-FZjJRKGSBM'
bot = telebot.TeleBot(API_TOKEN)

# База данных для хранения пользователей и их статусов
users_db = {}
Zaiavki = 0
Slitoscammerov = 0

# Начальный ранг
DEFAULT_RANK = 'Нету в базе'

# Функция для получения шанса скама
def get_scam_chance(rank):
    if rank == 'Волонтёр':
        return '10%'
    elif rank == 'Нету в базе':
        return '38%'
    elif rank == 'Стажёр':
        return '20%'
    elif rank == 'Проверен гарантом':
        return '23%'
    elif rank == 'Скаммер':
        return '100%'
    elif rank == 'Петух':
        return '1000%'
    return '0%'

# Команды для управления рангами
@bot.message_handler(commands=['траст'])
def give_rank_trust(message):
    user_id = message.reply_to_message.from_user.id
    users_db[user_id] = {'rank': 'Проверен гарантом', 'iskalivbase': 0}
    bot.reply_to(message, f"Ранг выдан пользователю {user_id}: Проверен гарантом.")

@bot.message_handler(commands=['Админ'])
def give_rank_admin(message):
    user_id = message.reply_to_message.from_user.id
    users_db[user_id] = {'rank': 'Админ', 'iskalivbase': 0}
    bot.reply_to(message, f"Ранг выдан пользователю {user_id}: Админ.")

@bot.message_handler(commands=['директор'])
def give_rank_director(message):
    user_id = message.reply_to_message.from_user.id
    users_db[user_id] = {'rank': 'Директор', 'iskalivbase': 0}
    bot.reply_to(message, f"Ранг выдан пользователю {user_id}: Директор.")

@bot.message_handler(commands=['владыка'])
def give_rank_owner(message):
    user_id = message.reply_to_message.from_user.id
    users_db[user_id] = {'rank': 'Владелец', 'iskalivbase': 0}
    bot.reply_to(message, f"Ранг выдан пользователю {user_id}: Владелец.")

@bot.message_handler(commands=['Стажёр'])
def give_rank_intern(message):
    user_id = message.reply_to_message.from_user.id
    users_db[user_id] = {'rank': 'Стажёр', 'iskalivbase': 0}
    bot.reply_to(message, f"Ранг выдан пользователю {user_id}: Стажёр.")

@bot.message_handler(commands=['гарант'])
def give_rank_guarantee(message):
    user_id = message.reply_to_message.from_user.id
    users_db[user_id] = {'rank': 'Гарант', 'iskalivbase': 0}
    bot.reply_to(message, f"Ранг выдан пользователю {user_id}: Гарант.")

@bot.message_handler(commands=['скам'])
def report_scammer(message):
    global Zaiavki
    parts = message.text.split()
    user_id = int(parts[1])
    reason = parts[2]
    reputation = parts[3]
    
    users_db[user_id] = {
        'rank': 'Скаммер',
        'reason': reason,
        'reputation': reputation,
        'iskalivbase': 0
    }
    
    Zaiavki += 1
    bot.reply_to(message, f"Заявка на скамера {user_id} принята. Общее количество заявок: {Zaiavki}.")

@bot.message_handler(commands=['нескам'])
def remove_scammer(message):
    parts = message.text.split()
    user_id = int(parts[1])
    reason = parts[2]
    
    if user_id in users_db:
        del users_db[user_id]
        bot.reply_to(message, f"Пользователь {user_id} удален из базы.")
    else:
        bot.reply_to(message, f"Пользователь {user_id} не найден в базе.")

@bot.message_handler(commands=['чек'])
def check_user(message):
    parts = message.text.split()
    user_id = int(parts[1])
    user_info = users_db.get(user_id, {'rank': DEFAULT_RANK, 'iskalivbase': 0})
    
    reply = f"""
🆔 Id: {user_id}
🔁 Репутация: {user_info['rank']}
Шанс скама: {get_scam_chance(user_info['rank'])}
🚮 Заявки: {Zaiavki}
🔍 Искали в базе: {user_info['iskalivbase']}
🐝 Stand base
"""
    bot.reply_to(message, reply)

@bot.message_handler(commands=['спасибо'])
def thank_user(message):
    parts = message.text.split()
    user_id = int(parts[1])
    global Slitoscammerov
    Slitoscammerov += 1
    bot.reply_to(message, f"Спасибо! Количество слитых скамеров: {Slitoscammerov}.")

@bot.message_handler(commands=['чекми'])
def check_myself(message):
    user_id = message.from_user.id
    user_info = users_db.get(user_id, {'rank': DEFAULT_RANK, 'iskalivbase': 0})
    
    reply = f"""
🆔 Id: {user_id}
🔁 Репутация: {user_info['rank']}
Шанс скама: {get_scam_chance(user_info['rank'])}
🚮 Заявки: {Zaiavki}
🔍 Искали в базе: {user_info['iskalivbase']}
🐝 Stand base
"""
    bot.reply_to(message, reply)

@bot.message_handler(commands=['бан'])
def ban_user(message):
    user_id = message.reply_to_message.from_user.id
    # Здесь вы можете добавить логику для кика пользователя

@bot.message_handler(commands=['мут'])
def mute_user(message):
    user_id = message.reply_to_message.from_user.id
    # Здесь вы можете добавить логику для мута пользователя

# Основной цикл
bot.polling()
