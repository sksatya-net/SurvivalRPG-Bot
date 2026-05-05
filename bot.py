import telebot
import random
import json
import time
import threading

# Your Bot Token
API_TOKEN = '8745869355:AAHW2YJ-sFzPzLzMRSHia0F0QijCpa06rbI'
bot = telebot.TeleBot(API_TOKEN)

# Load 100 items from items.json
with open('items.json', 'r') as f:
    item_data = json.load(f)['items']

# Database (Storing player stats)
players = {}
active_drops = {}

def get_player(user_id, name):
    if user_id not in players:
        players[user_id] = {
            "name": name, "hp": 100, "sp": 100, "xp": 0, "level": 1,
            "gold": 500, "bag": [], "vault": []
        }
    return players[user_id]

# --- THE DROP MANAGER (Runs in Background) ---
def drop_manager(chat_id):
    while True:
        time.sleep(300) # Wait 5 minutes
        num_drops = random.randint(1, 4) # 1 to 4 random drops
        
        for _ in range(num_drops):
            item = random.choice(item_data)
            password = str(random.randint(1000, 9999)) # 4-digit password
            
            drop_msg = bot.send_message(
                chat_id, 
                f"📦 **NEW DROP ALERT!**\n\nItem: `{item['name']}`\nType: {item['type']}\n\n👉 Type the password to grab: `{password}`",
                parse_mode="Markdown"
            )
            
            # Save drop info to check later
            active_drops[chat_id] = {
                "password": password, 
                "item": item, 
                "msg_id": drop_msg.message_id
            }
            time.sleep(random.randint(30, 60)) # Small gap between drops

# --- COMMANDS ---
@bot.message_handler(commands=['start'])
def start_game(message):
    user = get_player(str(message.from_user.id), message.from_user.first_name)
    bot.reply_to(message, f"🎮 Welcome {user['name']}! The Strike & Survive Arena is now ACTIVE.\n\nItems will drop every 5 minutes. Be fast!")
    # Start the drop thread
    threading.Thread(target=drop_manager, args=(message.chat.id,), daemon=True).start()

@bot.message_handler(commands=['stats'])
def show_stats(message):
    u = get_player(str(message.from_user.id), message.from_user.first_name)
    bot.reply_to(message, f"📊 **PLAYER STATS**\n\n❤️ HP: {u['hp']}/100\n⚡ SP: {u['sp']}/100\n🌟 XP: {u['xp']}\n💰 Gold: {u['gold']}")

@bot.message_handler(func=lambda m: True)
def on_message(message):
    chat_id = message.chat.id
    # Check if a drop is active and password matches
    if chat_id in active_drops and message.text == active_drops[chat_id]["password"]:
        user = get_player(str(message.from_user.id), message.from_user.first_name)
        
        if user['sp'] < 5:
            bot.reply_to(message, "🔋 You're out of energy! You need 5 SP to grab items.")
            return

        item = active_drops[chat_id]["item"]
        user['bag'].append(item['name'])
        user['sp'] -= 5
        user['xp'] += 10
        
        bot.send_message(chat_id, f"✅ **{user['name']} grabbed the {item['name']}!** 🎒")
        
        # Cleanup
        try: bot.delete_message(chat_id, active_drops[chat_id]["msg_id"])
        except: pass
        del active_drops[chat_id]

print("Bot is ready...")
bot.infinity_polling()
