import discord
from db_manager import update_thread_db, get_thread_info, query_db


BOT_COMMANDS = "\n".join(["\n\nTo use me, use the buttons below, or one of following commands, including the \*:",
                          "**`*addme`** - adds you to the list of players",
                          "**`*removeme`** - removes you from the list of players",
                          "**`*backupme`** - adds you to the list of backup players, be sure to say `*addme` once you know you can play",
                          "**`*streamme`** - adds you to the list of streamers",
                          "**`*unstreamme`** -removes you from the list of streamers"])

class SignUpView(discord.ui.View):
    def __init__(self, thread_id, max_players: int, db_path, client):
        super().__init__(timeout=None)
        self.thread_id = thread_id
        self.max_players = max_players
        self.db_path = db_path
        self.client = client

    @discord.ui.button(label="Add Me", style=discord.ButtonStyle.green, row=0)
    async def addme(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        message = interaction.message
        user_mention = interaction.user.mention
        players, wait_list, backups, streamers, original_content = get_thread_info(self.db_path, self.thread_id)
        await add_user_to_thread(message, user_mention, players, wait_list, backups, streamers, original_content, self.max_players, self.db_path)
        await update_original_post(self.client, self.thread_id, players, wait_list, backups, streamers, original_content, self.db_path)

    @discord.ui.button(label="Back-Up Me", style=discord.ButtonStyle.blurple, row=0)
    async def backupme(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        message = interaction.message
        user_mention = interaction.user.mention
        players, wait_list, backups, streamers, original_content = get_thread_info(self.db_path, self.thread_id)
        await add_user_to_backups(message, user_mention, players, backups, original_content, self.db_path)
        await update_original_post(self.client, self.thread_id, players, wait_list, backups, streamers, original_content, self.db_path)

    @discord.ui.button(label="Remove Me", style=discord.ButtonStyle.red, row=0)
    async def removeme(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        message = interaction.message
        user_mention = interaction.user.mention
        players, wait_list, backups, streamers, original_content = get_thread_info(self.db_path, self.thread_id)
        await remove_user_from_thread(message, user_mention, players, wait_list, backups, streamers, original_content, self.db_path)
        await update_original_post(self.client, self.thread_id, players, wait_list, backups, streamers, original_content, self.db_path)

    @discord.ui.button(label="Stream Me", style=discord.ButtonStyle.grey, row=1)
    async def streamme(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        message = interaction.message
        user_mention = interaction.user.mention
        players, wait_list, backups, streamers, original_content = get_thread_info(self.db_path, self.thread_id)
        await add_user_to_streamers(message, user_mention, streamers, original_content, self.db_path)
        await update_original_post(self.client, self.thread_id, players, wait_list, backups, streamers, original_content, self.db_path)

    @discord.ui.button(label="Unstream Me", style=discord.ButtonStyle.grey, row=1)
    async def unstreamme(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        message = interaction.message
        user_mention = interaction.user.mention
        players, wait_list, backups, streamers, original_content = get_thread_info(self.db_path, self.thread_id)
        await remove_user_from_streamers(message, user_mention, streamers, original_content, self.db_path)
        await update_original_post(self.client, self.thread_id, players, wait_list, backups, streamers, original_content, self.db_path)

# Function to check if the user has the required role
def user_has_role(member, required_role_id):
    return any(role.id == required_role_id for role in member.roles)

# Function to handle private messages for thread creation
async def handle_private_message(message, client, FORUM_CHANNEL_ID, DB_PATH, WHITELISTED_USERS, MAX_PLAYERS):
    if message.content.startswith("create thread:"):
        if message.author.id in WHITELISTED_USERS:
            try:
                _, thread_info = message.content.split("create thread:", 1)
                thread_name, thread_content = [x.strip() for x in thread_info.split(",", 1)]

                forum_channel = client.get_channel(FORUM_CHANNEL_ID)
                if isinstance(forum_channel, discord.ForumChannel):
                    thread = (await forum_channel.create_thread(
                        name=thread_name,
                        content=thread_content + BOT_COMMANDS
                    ))[0]
                    print(f'Created thread with ID: {thread.id}')
                    await thread.send(view=SignUpView(thread.id, MAX_PLAYERS, DB_PATH, client))
                    
                    # Initialize player list, waitlist, backups, and streamers in the database
                    update_thread_db(DB_PATH, thread.id, [], [], [], [], thread_content)

                    await message.author.send(f"Thread '{thread_name}' created successfully!")
                else:
                    await message.author.send(f'Channel {FORUM_CHANNEL_ID} is not a forum channel.')
            except ValueError:
                await message.author.send("Please provide the thread name and content in the format: `create thread: <name>, <content>`")
        else:
            await message.author.send("You are not whitelisted to create threads.")
    else:
        await message.author.send("To create a thread, use the format: `create thread: <name>, <content>`")


# Function to handle "add me", "remove me", etc.
async def handle_thread_message(message, client, MAX_PLAYERS, DB_PATH):
    user_mention = message.author.mention
    thread_id = message.channel.id

    # Retrieve player list, waitlist, backups, and streamers from database
    players, wait_list, backups, streamers, original_content = get_thread_info(DB_PATH, thread_id)

    if "*addme" in message.content.lower():
        await add_user_to_thread(message, user_mention, players, wait_list, backups, streamers, original_content, MAX_PLAYERS, DB_PATH)
    elif "*removeme" in message.content.lower():
        await remove_user_from_thread(message, user_mention, players, wait_list, backups, streamers, original_content, DB_PATH)
    elif "*backupme" in message.content.lower():
        await add_user_to_backups(message, user_mention, players, backups, original_content, DB_PATH)
    elif "*streamme" in message.content.lower():
        await add_user_to_streamers(message, user_mention, streamers, original_content, DB_PATH)
    elif "*unstreamme" in message.content.lower():
        await remove_user_from_streamers(message, user_mention, streamers, original_content, DB_PATH)

    # Update the original post
    await update_original_post(client, thread_id, players, wait_list, backups, streamers, original_content, DB_PATH)



async def add_user_to_thread(message, user_mention, players, wait_list, backups, streamers, original_content, MAX_PLAYERS, DB_PATH):
    if user_mention in players or user_mention in wait_list:
        await message.channel.send(f"{user_mention}, you are already added!")
    else:
        # Remove the user from backups if they're in it
        if user_mention in backups:
            backups.remove(user_mention)
            await message.channel.send(f"{user_mention} has been removed from the backups list!")
        
        if len(players) < MAX_PLAYERS:
            players.append(user_mention)
            await message.channel.send(f"{user_mention} has been added to the player list!")
        else:
            wait_list.append(user_mention)
            await message.channel.send(f"{user_mention} has been added to the waitlist!")

    # Update the database
    update_thread_db(DB_PATH, message.channel.id, players, wait_list, backups, streamers, original_content)


async def remove_user_from_thread(message, user_mention, players, wait_list, backups, streamers, original_content, DB_PATH):
    if user_mention in players:
        players.remove(user_mention)
        await message.channel.send(f"{user_mention} has been removed from the player list!")
        if wait_list:
            next_player = wait_list.pop(0)
            players.append(next_player)
            await message.channel.send(f"{next_player} has been moved from the waitlist to the player list!")
    elif user_mention in wait_list:
        wait_list.remove(user_mention)
        await message.channel.send(f"{user_mention} has been removed from the waitlist!")
    elif user_mention in backups:
        backups.remove(user_mention)
        await message.channel.send(f"{user_mention} has been removed from the backup list!")
    else:
        await message.channel.send(f"{user_mention}, you are not on the list!")

    # Update the database
    update_thread_db(DB_PATH, message.channel.id, players, wait_list, backups, streamers, original_content)


# Add user to backups
async def add_user_to_backups(message, user_mention, players, backups, original_content, DB_PATH):
    if user_mention in backups:
        await message.channel.send(f"{user_mention}, you are already in the backups list!")
    else:
        # Remove the user from backups if they're in it
        if user_mention in players:
            players.remove(user_mention)
            await message.channel.send(f"{user_mention} has been removed from the player list!")
        backups.append(user_mention)
        await message.channel.send(f"{user_mention} has been added to the backups list!")

    # Update the database
    update_thread_db(DB_PATH, message.channel.id, players, [], backups, [], original_content)

# Remove user from streamers
async def remove_user_from_backups(message, user_mention, streamers, original_content, db_path):
    if user_mention in streamers:
        streamers.remove(user_mention)
        await message.channel.send(f"{user_mention} has been removed from the backups list!")
    else:
        await message.channel.send(f"{user_mention}, you are not in the backups list!")

    # Update the database
    update_thread_db(db_path, message.channel.id, [], [], [], streamers, original_content)



# Add user to streamers
async def add_user_to_streamers(message, user_mention, streamers, original_content, db_path):
    if user_mention in streamers:
        await message.channel.send(f"{user_mention}, you are already in the streamers list!")
    else:
        streamers.append(user_mention)
        await message.channel.send(f"{user_mention} has been added to the streamers list!")

    # Update the database
    update_thread_db(db_path, message.channel.id, [], [], [], streamers, original_content)

# Remove user from streamers
async def remove_user_from_streamers(message, user_mention, streamers, original_content, db_path):
    if user_mention in streamers:
        streamers.remove(user_mention)
        await message.channel.send(f"{user_mention} has been removed from the streamers list!")
    else:
        await message.channel.send(f"{user_mention}, you are not in the streamers list!")

    # Update the database
    update_thread_db(db_path, message.channel.id, [], [], [], streamers, original_content)


async def update_original_post(client, thread_id, players, wait_list, backups, streamers, original_content, DB_PATH):
    original_content_text = original_content if original_content else ""
    
    player_list_str = "\n".join(players)
    waitlist_str = "\n".join(wait_list) if wait_list else "None"
    backups_str = "\n".join(backups) if backups else "None"
    streamers_str = "\n".join(streamers) if streamers else "None"
    
    updated_content = f"{original_content_text}\n\nPlayers:\n{player_list_str}\n\nWaitlist:\n{waitlist_str}\n\nBackups:\n{backups_str}\n\nStreamers:\n{streamers_str}\n{BOT_COMMANDS}"

    # Fetch original thread
    original_thread = await client.fetch_channel(thread_id)
    #print(original_thread, thread_id, original_thread.starter_message)
    if original_thread.starter_message:
        await original_thread.starter_message.edit(content=updated_content)
    else:
        original_thread = await client.fetch_channel(thread_id)
        messages = [message async for message in original_thread.history(limit=1,oldest_first=True)]
        if messages:
            first_message = messages[0]
            await first_message.edit(content=updated_content)
        else:
            print("ERROR: this thread doesn't have a first message. Something went really wrong")        
