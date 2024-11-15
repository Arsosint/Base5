import telebot
from telebot import types
import time

API_TOKEN = 'YOUR_API_TOKEN'
bot = telebot.TeleBot(API_TOKEN)

user_roles = {}  # Хранит роли пользователей
user_muted_until = {}  # Хранит время, до которого пользователь замучен
user_banned_until = {}  # Хранит время, до которого пользователь забанен

# Определение ролей
roles = ['Стажёр', 'Владелец', 'Директор', 'Волонтёр', 'Админ', 'Гарант']

def is_admin(user_id):
    role = user_roles.get(user_id)
    return role in ['Владелец', 'Директор', 'Админ', 'Гарант']

def is_trust(user_id):
    role = user_roles.get(user_id)
    return role in ['Владелец', 'Директор', 'Гарант']

@bot.message_handler(commands=['мут'])
def mute_user(message):
    if is_admin(message.from_user.id):
        params = message.text.split()[1:]
        if len(params) < 3:
            bot.reply_to(message, "Необходимо указать юзера, причину и время.")
            return
        user_id, reason, duration = params[0], ' '.join(params[1:-1]), int(params[-1])
        user_muted_until[user_id] = time.time() + duration * 60
        bot.reply_to(message, f"Пользователь {user_id} замучен на {duration} минут по причине: {reason}")

@bot.message_handler(commands=['бан'])
def ban_user(message):
    if is_admin(message.from_user.id):
        params = message.text.split()[1:]
        if len(params) < 3:
            bot.reply_to(message, "Необходимо указать юзера, причину и время.")
            return
        user_id, reason, duration = params[0], ' '.join(params[1:-1]), int(params[-1])
        user_banned_until[user_id] = time.time() + duration * 60
        bot.reply_to(message, f"Пользователь {user_id} забанен на {duration} минут по причине: {reason}")

@bot.message_handler(commands=['делмут'])
def delete_mute(message):
    if is_admin(message.from_user.id):
        params = message.text.split()[1:]
        if len(params) < 3:
            bot.reply_to(message, "Необходимо указать юзера, причину и количество сообщений.")
            return
        user_id, reason, num_messages = params[0], ' '.join(params[1:-1]), int(params[-1])
        user_muted_until[user_id] = time.time() + 5 * 60  # Пример, замученный на 5 минут
        bot.reply_to(message, f"Пользователь {user_id} замучен на 5 минут и последние {num_messages} сообщений удалены.")

@bot.message_handler(commands=['оффтоп'])
def off_topic(message):
    if is_trust(message.from_user.id):
        params = message.text.split()[1:]
        if len(params) < 1:
            bot.reply_to(message, "Необходимо указать юзера.")
            return
        user_id = params[0]
        user_muted_until[user_id] = time.time() + 5 * 60
        bot.reply_to(message, f"Пользователь {user_id} в оффтоп на 5 минут.")

@bot.message_handler(commands=['ранг'])
def set_rank(message):
    if is_trust(message.from_user.id):
        params = message.text.split()[1:]
        if len(params) < 2:
            bot.reply_to(message, "Необходимо указать ID пользователя и ранг.")
            return
        user_id, rank = params[0], params[1]
        if rank in roles:
            user_roles[user_id] = rank
            bot.reply_to(message, f"Ранг для пользователя {user_id} установлен на {rank}.")
        else:
            bot.reply_to(message, "Некорректный ранг.")

@bot.message_handler(commands=['снять_ранг'])
def remove_rank(message):
    if is_trust(message.from_user.id):
        params = message.text.split()[1:]
        if len(params) < 1:
            bot.reply_to(message, "Необходимо указать ID пользователя.")
            return
        user_id = params[0]
        user_roles.pop(user_id, None)
        bot.reply_to(message, f"Ранг для пользователя {user_id} снят.")

# Проверка на mute или ban перед обработкой других команд
@bot.middleware_handler(update_types=['message'])
def check_mute_ban(message):
    if message.from_user.id in user_muted_until and time.time() < user_muted_until[message.from_user.id]:
        bot.reply_to(message, "Вы замучены и не можете писать.")
        return False

    if message.from_user.id in user_banned_until and time.time() < user_banned_until[message.from_user.id]:
        bot.reply_to(message, "Вы забанены и не можете писать.")
        return False

    return True

bot.polling(none_stop=True)
