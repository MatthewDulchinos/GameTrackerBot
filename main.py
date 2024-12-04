import discord
from db_manager import init_db
from config_loader import load_config
from bot_events import handle_private_message, handle_thread_message

# Load the constants from the YAML file
config = load_config('config.yaml')

TOKEN = config['bot_token']
FORUM_CHANNEL_ID = config['forum_channel_id']
MAX_PLAYERS = config['max_players']
DB_PATH = config['database_path']
WHITELISTED_USERS = config['whitelisted_users']

# Initialize the bot
intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True
client = discord.Client(intents=intents)

# Initialize the database
init_db(DB_PATH)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if isinstance(message.channel, discord.DMChannel):
        await handle_private_message(message, client, FORUM_CHANNEL_ID, DB_PATH, WHITELISTED_USERS, MAX_PLAYERS)
    elif isinstance(message.channel, discord.Thread):
        await handle_thread_message(message, client, MAX_PLAYERS, DB_PATH, WHITELISTED_USERS)

client.run(TOKEN)
