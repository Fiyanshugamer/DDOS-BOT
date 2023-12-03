import configparser
import os
import time
import math
from pycraft import PyCraftClient
from mineflayer.pathfinder import goals

# Function to read configuration from a file
def read_config():
    config = configparser.ConfigParser()
    try:
        config.read('config.ini')
        server_address = config.get('Server', 'Address', fallback='localhost')
        server_port = config.getint('Server', 'Port', fallback=25565)
        base_username = config.get('Bot', 'Username', fallback='your_bot_username')
        bot_count = config.getint('Bot', 'Count', fallback=1)
        join_delay = config.getfloat('Bot', 'JoinDelay', fallback=1.0)
        message = config.get('Bot', 'Message', fallback='Hello from the bot!')
        message_delay = config.getfloat('Bot', 'MessageDelay', fallback=5.0)
        login_command = config.get('Bot', 'LoginCommand', fallback='')
        anti_afk_enabled = config.getboolean('Bot', 'AntiAFKEnabled', fallback=True)
        reconnect_delay = config.getfloat('Bot', 'ReconnectDelay', fallback=60.0)
        return server_address, server_port, base_username, bot_count, join_delay, message, message_delay, login_command, anti_afk_enabled, reconnect_delay
    except Exception as e:
        print(f"Error reading config: {e}")
        return 'localhost', 25565, 'your_bot_username', 1, 1.0, 'Hello from the bot!', 5.0, '', True, 60.0

# Function to write configuration to a file
def write_config(server_address, server_port, base_username, bot_count, join_delay, message, message_delay, login_command, anti_afk_enabled, reconnect_delay):
    try:
        config = configparser.ConfigParser()
        config['Server'] = {'Address': server_address, 'Port': str(server_port)}
        config['Bot'] = {
            'Username': base_username,
            'Count': str(bot_count),
            'JoinDelay': str(join_delay),
            'Message': message,
            'MessageDelay': str(message_delay),
            'LoginCommand': login_command,
            'AntiAFKEnabled': str(anti_afk_enabled),
            'ReconnectDelay': str(reconnect_delay)
        }
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
        print("Config file written successfully.")
    except Exception as e:
        print(f"Error writing config: {e}")


if not os.path.exists('config.ini'):
    write_config('localhost', 25565, 'your_bot_username', 1, 1.0, 'Hello from the bot!', 5.0, '', True, 60.0)

# Read configuration from the file
server_address, server_port, base_username, bot_count, join_delay, message, message_delay, login_command, anti_afk_enabled, reconnect_delay = read_config()

def on_chat_message(packet):
    try:
        chat_message = packet.json_data.get('message', '')
        print(f"Received chat message: {chat_message}")
    except Exception as e:
        print(f"Error processing chat message: {e}")

def send_message(bot, message):
    try:
        bot.send_chat(message)
    except Exception as e:
        print(f"Error sending message: {e}")

def execute_login_command(bot, login_command):
    try:
        if login_command:
            bot.send_chat(login_command)
    except Exception as e:
        print(f"Error executing login command: {e}")

def perform_anti_afk_movement(bot):
    try:
        
        radius = 5
        angle_increment = 0.1
        for angle in range(0, 360, int(1/angle_increment)):
            x = radius * math.cos(math.radians(angle))
            z = radius * math.sin(math.radians(angle))
            bot.player.set_position(x, bot.player.position.y, z)
            time.sleep(1)  
    except Exception as e:
        print(f"Error performing anti-AFK movement: {e}")


def connect_and_login_bots():
    try:
        bot_username = ""  # Declare bot_username before the loop

        for i in range(1, bot_count + 1):
            # Create a PyCraftClient instance for each bot
            bot = PyCraftClient()

           
            bot.register('play.chat', on_chat_message)

           
            bot.connect(server_address, server_port)

           
            bot_username = f"{base_username}_{i}"
            bot.login(bot_username)

        
            time.sleep(join_delay)
            execute_login_command(bot, login_command)

            send_message(bot, message)

            while True:
                time.sleep(message_delay)
                send_message(bot, message)

                # Perform anti-AFK movement if enabled
                if anti_afk_enabled:
                    perform_anti_afk_movement(bot)

     
        return bot_username
    except Exception as e:
        print(f"Error connecting and logging in bots: {e}")
        return ""

def reconnect(bot):
    while True:
        try:
            bot.connect(server_address, server_port)
            bot.login(bot_username)  # Use the last used bot_username
            execute_login_command(bot, login_command)
            break
        except Exception as e:
            print(f"Reconnect failed: {e}")
            time.sleep(reconnect_delay)

# Main function to manage bot connections
def manage_bots():
    while True:
        try:
            connect_and_login_bots()
        except Exception as e:
            print(f"An error occurred: {e}")
            print("Attempting to reconnect...")
            reconnect(bot)

manage_bots()