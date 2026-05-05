import telebot
import random
import json
import time
import threading

API_TOKEN = '8745869355:AAHW2YJ-sFzPzLzMRSHia0F0QijCpa06rbI'
bot = telebot.TeleBot(API_TOKEN)

with open('items.json', 'r') as f:
    item_data = json.load(f)['items']

players = {}
active_drops = {}

def get_player(user_id, name):
    if user_id not in players:
        players[user_id] = {"name": name, "hp": 100, "sp": 100, "xp": 0, "level": 1, "gold": 500, "bag": [], "vault": []}
    return players[user_id]

def drop_manager(chat_id):
    while True:
        time.sleep(300)
        item = random.choice(item_data)
        password = str(random.randint(1000, 9999))
        drop_msg = bot.send_message(chat_id, f"📦 **NEW DROP!**\nItem: `{item['name']}`\nType: {item['type']}\n\n👉 Password: `{password}`")
        active_drops[chat_id] = {"password": password, "item": item, "msg_id": drop_msg.message_id}

@bot.message_handler(commands=['start'])
def start(message):
    get_player(str(message.from_user.id), message.from_user.first_name)
    bot.reply_to(message, "🎮 Strike & Survive Active! Items will drop soon.")
    threading.Thread(target=drop_manager, args=(message.chat.id,), daemon=True).start()

@bot.message_handler(commands=['bag'])
def show_bag(message):
    u = get_player(str(message.from_user.id), message.from_user.first_name)
    items = ", ".join(u['bag']) if u['bag'] else "Empty"
    bot.reply_to(message, f"🎒 Your Bag: {items}")

@bot.message_handler(commands=['eat'])
def eat_item(message):
    u = get_player(str(message.from_user.id), message.from_user.first_name)
    if not u['bag']:
        bot.reply_to(message, "Your bag is empty!")
        return
    # Simple logic: eat the first item if it's food
    item_name = u['bag'].pop(0)
    u['hp'] = min(100, u['hp'] + 20)
    u['sp'] = min(100, u['sp'] + 10)
    bot.reply_to(message, f"😋 You ate {item_name}! ❤️+20 ⚡+10")

@bot.message_handler(commands=['punch'])
def punch(message):
    bot.reply_to(message, "👊 You punched the air! (In future updates, you can punch players)")

@bot.message_handler(func=lambda m: True)
def handle_msg(message):
    cid = message.chat.id
    if cid in active_drops and message.text == active_drops[cid]["password"]:
        u = get_player(str(message.from_user.id), message.from_user.first_name)
        item = active_drops[cid]["item"]
        u['bag'].append(item['name'])
        bot.reply_to(message, f"✅ Grabbed `{item['name']}`!")
        del active_drops[cid]

bot.infinity_polling()
