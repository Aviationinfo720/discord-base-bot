import os
import discord
from discord import Embed
import time
import random
from discord.ext import tasks
from discord.ext import commands
import yt_dlp as youtube_dl
import websockets.exceptions
from typing import Optional
from typing import Callable, Optional
from discord import app_commands
# import yaml
import datetime
import websockets
from spotipy import Spotify
from characterai import aiocai
from characterai import pycai
import functools 
from spotipy.oauth2 import SpotifyClientCredentials
# import easy_pil
import sqlite3
import asyncio
from PyCharacterAI import get_client
from PyCharacterAI.exceptions import SessionClosedError
from datetime import timedelta
import logging
import json 
from spotifysearch.client import Client
import time
import traceback
import tracemalloc
import spotipy
from discord.ui import View, Button
from spotipy.oauth2 import SpotifyOAuth



tracemalloc.start()

# Elements per page
cai = pycai(token="9d8e1b7469829fbe9db06dd701ea0a604fc45e30")
L = 5
music_queue = []  # Music queue
current_song = None
busy = False  # Add a busy flag to track if the bot is busy

spotifyclient = Client(
    client_id="effd6099f3124090b83aaeef730e824a",
    client_secret="ad655f55959345a9afa9004a4902fc15"
    # redirect_uri="https://docs.google.com/forms/d/e/1FAIpQLSchYnSa-HW9FDvv0Ctsybj3UhDw0zGonxby5WuJ8FTjt3_BTQ/viewform?usp=sf_link",  # Set to "http://localhost:8080" for local development
    # scope="user-library-read"  # Adjust the scope as needed
)

SPOTIFY_CLIENT_ID = 'effd6099f3124090b83aaeef730e824a'
SPOTIFY_CLIENT_SECRET = 'ad655f55959345a9afa9004a4902fc15'

auth_manager = SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
sp = spotipy.Spotify(auth_manager=auth_manager)
# Paths to images
image_paths = {
    "lufthansa": "C:/Anwesh/Python-Projects/Aviationbot/lufthansa.jpeg",
    "british": "C:/Anwesh/Python-Projects/Aviationbot/British_Airlines.jpeg",
    "airchina": "C:/Anwesh/Python-Projects/Aviationbot/Air_China.jpeg",
    "airindia": "C:/Anwesh/Python-Projects/Aviationbot/Air_India.jpeg",
    "singapore": "C:/Anwesh/Python-Projects/Aviationbot/Singapore_Airlines.jpeg",
}

# yt-dlp options

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'ytsearch',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'options': '-vn'
}


ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

sevenfortysevenpics = [discord.File(open(image_paths[key], "rb")) for key in image_paths]

MY_GUILD = discord.Object(id=1290614052115976323)
PUNISHMENT_LOG = 1290913389895221249
MODERATOR_ROLE_ID = [1290907676288487526, 1290907287682027586, 1290614351870427207]
MIKU_ID = 1290993538439315507
WARNSON_PATH = "H:/My Drive/jjkinfo_jsons/warnings.json"
DATA_FILE = "H:/My Drive/jjkinfo_jsons/leveling.json"

CHAR = '5mhs-itLvD620IWrWLamTb2_yoj4gnm-o_LTX5LPRNE'


chat = None

def load_user_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

user_data = load_user_data()

# Save user data to the JSON file
def save_user_data():
    with open(DATA_FILE, "w") as f:
        json.dump(user_data, f, indent=4)

ai_token = "9d8e1b7469829fbe9db06dd701ea0a604fc45e30"

class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.character_client = None  # PyCharacterAI client
        self.me = None  # Character AI account
        self.chat = None  # Character AI chat session
        self.greeting_message = None  # Initial greeting from AI
        self.chat_channel = None  # Channel for bot interaction
        self.tree = app_commands.CommandTree(self)

    async def on_ready(self):
        logging.info(f'Logged in as {self.user} (ID: {self.user.id})')
        self.tree.copy_global_to(guild=MY_GUILD)
        synced = await self.tree.sync(guild=MY_GUILD)
        print(f"Synced {len(synced)} commands")

        # Get the Discord channel where the bot will listen for messages
        self.chat_channel = self.get_channel(MIKU_ID)

        if self.chat_channel is None:
            logging.error(f"Channel with ID {MIKU_ID} not found.")
            return

        logging.info(f"Bot is ready and will send messages to {self.chat_channel.name}.")
        
        # Initialize the Character AI session
        await self.init_character_ai()

    async def init_character_ai(self):
        try:
            # Authenticate with Character AI
            self.character_client = await get_client(token=ai_token)
            self.me = await self.character_client.account.fetch_me()
            logging.info(f'Authenticated as @{self.me.username} in Character AI')

            # Create a new chat session with the character
            self.chat, self.greeting_message = await self.character_client.chat.create_chat(CHAR)

            # Send the initial greeting from Character AI to the Discord channel
            if self.greeting_message:
                await self.chat_channel.send(self.greeting_message.get_primary_candidate().text)

        except Exception as e:
            logging.error(f"Error initializing Character AI session: {e}")

    async def on_message(self, message: discord.Message):
        # Ignore the bot's own messages
        if message.author == self.user:
            return

        user_id = str(message.author.id)

        if user_id not in user_data:
            user_data[user_id] = {'xp': 0, 'level': 1}

        xp_gained = 10
        user_data[user_id]['xp'] += xp_gained
        await self.check_level_up(message.author)

        save_user_data()

        print(f"{message.author} now has {user_data[user_id]['xp']} XP.")

        # Only respond to messages in the specified channel
        if message.channel.id == MIKU_ID:
            if self.chat:
                try:
                    # Send the user's message to Character AI and receive the reply
                    if message.content != "":
                        answer = await self.character_client.chat.send_message(CHAR, self.chat.chat_id, message.content)#, streaming=True)

                    printed_length = 0
                
                    text = answer.get_primary_candidate().text
                    if len(text) != 0:
                        await message.channel.send(text[printed_length:])

                    printed_length = len(text)

                except SessionClosedError:
                    logging.error("Character AI session closed.")
                    await message.channel.send("Character AI session has been closed. Please wait while I reconnect.")
                    await self.init_character_ai()

                except Exception as e:
                    logging.error(f"Error sending message to Character AI: {e}")
                    await message.channel.send("There was an error communicating with the AI. Please try again later.")
            else:
                await message.channel.send("AI chat session is not active yet. Please wait.")

    async def close(self):
        # Close the Character AI session when shutting down the bot
        if self.character_client:
            await self.character_client.close_session()
        await super().close()

    async def check_level_up(self, user: discord.User):
        user_id = str(user.id)
        xp = user_data[user_id]['xp']
        current_level = user_data[user_id]['level']
        xp_channel = client.get_channel(1293203259397242984)

        # Example leveling formula: 100 XP per level
        next_level_xp = 100 * current_level

        if xp >= next_level_xp:
            user_data[user_id]['level'] += 1
            new_level = user_data[user_id]['level']

            # Notify the user about their level up
            await xp_channel.send(f"Congratulations {user.mention}! You've leveled up to level {new_level}.")
            await user.send(f"Congratulations! You've leveled up to level {new_level} in the Anime chats and random.")

            # Optionally give a role when they level up
            # await self.give_role_for_level(user, new_level)

            # Save the updated level to JSON
            save_user_data()

                
def is_mod(interaction: discord.Interaction):
    for role_id in MODERATOR_ROLE_ID:
        if interaction.user.get_role(role_id) is not None:
            return True
    return False


def save_warnings(data):
    with open(WARNSON_PATH, 'w') as f:
        json.dump(data, f, indent=4)

def load_warnings():
    try:
        if os.path.exists(WARNSON_PATH):
            with open(WARNSON_PATH, 'r') as f:
                return json.load(f)
        return {"users": []}
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return {"users": []}
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {"users": []}

def appealbutton(self_pass, userid, msg_id, namevalue, reasonvalue):
    class AppealButtons(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)

        @discord.ui.button(label="Decline Appeal", style=discord.ButtonStyle.red)
        async def declineappeal(self, interaction: discord.Interaction, button: discord.ui.Button):
            button.disabled = True
            await interaction.response.edit_message(view=None)
            channel = await client.fetch_channel(PUNISHMENT_LOG)
            msg = await channel.fetch_message(msg_id)
            _user = await client.fetch_user(userid)
            await _user.send("Sorry but your ban appeal has not been accepted.")

        @discord.ui.button(label="Accept Appeal", style=discord.ButtonStyle.green)
        async def acceptappeal(self, interaction: discord.Interaction, button: discord.ui.Button):
            button.disabled = True
            await interaction.response.edit_message(view=None)
            _user = await client.fetch_user(userid)
            await _user.send("Your ban appeal has been accepted. Please do be nice next time!")

    return AppealButtons()

class showspotifybutton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

class VcControlView(discord.ui.View):
    def __init__(self, voice_client):
        super().__init__()
        self.voice_client = voice_client

    @discord.ui.button(label='Pause', style=discord.ButtonStyle.danger)
    async def pause(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.voice_client.is_playing():
            self.voice_client.pause()
            button.label = 'Resume'
            button.style = discord.ButtonStyle.success
        elif self.voice_client.is_paused():
            self.voice_client.resume()
            button.label = 'Pause'
            button.style = discord.ButtonStyle.danger
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label='Skip', style=discord.ButtonStyle.primary)
    async def skip(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.voice_client.stop()
        await interaction.response.edit_message(view=self)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        partial = functools.partial(ytdl.extract_info, url, download=not stream)
        data = await loop.run_in_executor(None, partial)

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

async def search_youtube(query):
    loop = asyncio.get_event_loop()
    partial = functools.partial(ytdl.extract_info, f"ytsearch:{query}", download=False)
    info = await loop.run_in_executor(None, partial)
    if 'entries' not in info or len(info['entries']) == 0:
        raise ValueError('No results found for the query.')
    return info['entries'][0]['webpage_url']

class FFmpegPCMAudio(discord.FFmpegPCMAudio):
    def __init__(self, source, *, executable='ffmpeg', pipe=False, stderr=None, before_options=None, options=None):
        super().__init__(source, executable=executable, pipe=pipe, stderr=stderr, before_options=before_options, options=options)
        self.start_time = time.time()

    @property
    def duration(self):
        return self._duration

    @duration.setter
    def duration(self, duration):
        self._duration = duration

    @property
    def elapsed_time(self):
        return time.time() - self.start_time
    
async def search_youtube(query):
    search_url = f"ytsearch:{query}"
    info = await asyncio.get_event_loop().run_in_executor(None, lambda: ytdl.extract_info(search_url, download=False))
    if 'entries' in info and len(info['entries']) > 0:
        return info['entries'][0]['webpage_url']
    else:
        print(f"No results found for the query: {query}")  # Debug information
        return None

class MusicQueue:
    def __init__(self):
        self.queue = []
    
    def add_song(self, song_info):
        self.queue.append(song_info)
    
    def get_next_song_info(self):
        if self.queue:
            return self.queue[0]  # Peek at the first item
        return None
    
    def remove_next_song(self):
        if self.queue:
            return self.queue.pop(0)
        return None
    
    def is_empty(self):
        return len(self.queue) == 0

music_queue = MusicQueue()

# busy = False  # Add a busy flag to track if the bot is busy

class Feedback(discord.ui.Modal, title='Feedback'):
    name = discord.ui.TextInput(label='Name', placeholder='Your name here...')
    feedback = discord.ui.TextInput(
        label='Whats your opinions on this server?',
        style=discord.TextStyle.long,
        placeholder='Type your feedback here...',
        required=False,
        max_length=300,
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'Thanks for your feedback, {self.name.value}!', ephemeral=True)
        log_channel = interaction.guild.get_channel(PUNISHMENT_LOG)

        embed = discord.Embed(title=f'Feedback from {self.name.value}!', color=discord.Colour.yellow())
        embed.set_thumbnail(url=interaction.user.avatar)
        embed.description = self.feedback.value
        await log_channel.send(embed=embed)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)
        traceback.print_exception(type(error), error, error.__traceback__)

class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Create Ticket", style=discord.ButtonStyle.green)
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        category = discord.utils.get(guild.categories, name="Tickets")
        if not category:
            category = await guild.create_category("Tickets")

        channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            category=category
        )

        await channel.set_permissions(interaction.guild.default_role, read_messages=False)
        await channel.set_permissions(interaction.user, read_messages=True, send_messages=True)

        embed = discord.Embed(title="Ticket Created", description="A moderator will be with you shortly.")
        await channel.send(embed=embed)

        await interaction.response.send_message(f"Ticket created: {channel.mention}", ephemeral=True)

class CloseTicketView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.red)
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not any(role.id == MODERATOR_ROLE_ID for role in interaction.user.roles):
            await interaction.response.send_message("You don't have permission to close this ticket.", ephemeral=True)
            return

        await interaction.channel.delete()
        await interaction.response.send_message("Ticket closed and channel deleted.", ephemeral=True)


class Pagination(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, get_page: Callable):
        self.interaction = interaction
        self.get_page = get_page
        self.total_pages: Optional[int] = None
        self.index = 1
        super().__init__(timeout=100)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user == self.interaction.user:
            return True
        else:
            emb = discord.Embed(
                description=f"Only the author of the command can perform this action.",
                color=16711680
            )
            await interaction.response.send_message(embed=emb, ephemeral=True)
            return False

    async def navigate(self):
        emb, self.total_pages = await self.get_page(self.index)
        if self.total_pages == 1:
            await self.interaction.response.send_message(embed=emb)
        elif self.total_pages > 1:
            self.update_buttons()
            await self.interaction.response.send_message(embed=emb, view=self)

    async def edit_page(self, interaction: discord.Interaction):
        emb, self.total_pages = await self.get_page(self.index)
        self.update_buttons()
        await interaction.response.edit_message(embed=emb, view=self)

    def update_buttons(self):
        self.children[0].disabled = self.index == 1
        self.children[1].disabled = self.index == 1
        self.children[2].disabled = self.index == self.total_pages
        self.children[3].disabled = self.index == self.total_pages

    @discord.ui.button(emoji="⏮️", style=discord.ButtonStyle.blurple)
    async def first_page(self, interaction: discord.Interaction, button: discord.Button):
        self.index = 1
        await self.edit_page(interaction)

    @discord.ui.button(emoji="◀️", style=discord.ButtonStyle.blurple)
    async def previous(self, interaction: discord.Interaction, button: discord.Button):
        self.index -= 1
        await self.edit_page(interaction)

    @discord.ui.button(emoji="▶️", style=discord.ButtonStyle.blurple)
    async def next(self, interaction: discord.Interaction, button: discord.Button):
        self.index += 1
        await self.edit_page(interaction)

    @discord.ui.button(emoji="⏭️", style=discord.ButtonStyle.blurple)
    async def last_page(self, interaction: discord.Interaction, button: discord.Button):
        self.index = self.total_pages
        await self.edit_page(interaction)

    async def on_timeout(self):
        # Remove buttons on timeout
        message = await self.interaction.original_response()
        await message.delete()

    @staticmethod
    def compute_total_pages(total_results: int, results_per_page: int) -> int:
        return ((total_results - 1) // results_per_page) + 1


class BanAppeal(discord.ui.Modal, title='Ban Appeal'):
    name = discord.ui.TextInput(label='Name', placeholder='Your name here...', required=True)
    reason = discord.ui.TextInput(
        label="Why do you request a ban appeal?",
        style=discord.TextStyle.long,
        placeholder='Type your reason here(No Small Answers)',
        required=True,
        max_length=300,
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"The mods will look into your appeal, {self.name.value}. We will get back to you in your DM's", ephemeral=True
        )

        log_channel = interaction.guild.get_channel(PUNISHMENT_LOG)

        embed = discord.Embed(title=f'Ban appeal from {self.name.value}', color=discord.Colour.yellow())
        embed.set_thumbnail(url=interaction.user.avatar)
        embed.description = self.reason.value
        _uembed = await log_channel.send(embed=embed)
        await _uembed.edit(view=appealbutton(self, interaction.user.id, _uembed.id, self.name.value, self.reason.value))

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)
        traceback.print_exception(type(error), error, error.__traceback__)

intents = discord.Intents.default()
intents.members = True
intents.presences = True
intents.message_content = True
client = MyClient(intents=intents)

def generate_unix_time_code():
    return int(time.time())


# @client.event
# async def on_member_join(member):

#     embed = discord.Embed(title=f"Hello there {member.nick}")

#     channel = client.get_channel(1267058564971630728)
#     if channel:
    

# @client.listen('on_message')
# async def on_message(message):
#     if message.channel.id == MIKU_ID and not message.author.bot:
#         print(f'Message from {message.author}: {message.content}')

@client.tree.command(name="roll")
async def roll_dice(interaction: discord.Interaction):
    """Rolls dice 6 sided"""
    roll = random.randint(1,6)
    await interaction.response.send_message(f'The number is {roll}')

# @client.tree.command()
# async def setuprules(interaction: discord.Interaction, channel: discord.TextChannel):
#     embed = discord.Embed(
#         title="🚨Rules🚨",
#         description="Yes, rules are boring and following it is as crap as eating your poop. But to make a good server, we need to add some rules to maintain equibrilim amongst all!",
#         # colour=
#     )

#     embed.add_field(name="**1. Stay SFW (No gore or 18+ Adultery Content)**", value=1, inline=True)
#     embed.add_field(name="**2. Mild Swearing is allowed but not in a way to hurt others in a bad way**", value=2, inline=True)
#     embed.add_field(name="**3. Respect every member and their opinions. Yes the pineaple on pizza fights can continue but keep it on a maintainable level**", value=3, inline=True)    
#     embed.add_field(name="**4. Have fun!**", value=4, inline=True)
#     embed.set_image(url="https://cdn.discordapp.com/attachments/1267071262669275226/1267085526595272756/RULES.png?ex=66a780da&is=66a62f5a&hm=d72632e08e8004c6a5e60091b1853f495a38f1de32609fe6b421dcc785a2bd56&")

#     await channel.send(embed=embed)
#     await interaction.response.send_message(content="done", ephemeral=True)

@client.tree.command()
async def show_warnings(interaction: discord.Interaction, member: discord.Member):
    async def get_page(page: int):
        data = load_warnings()

        # Find the user entry
        user_entry = next((user for user in data["users"] if user["user_id"] == member.id), None)

        if user_entry is None or "warnings" not in user_entry or not user_entry["warnings"]:
            await interaction.response.send_message(f"{member.mention} has no warnings.", ephemeral=True)
            return

        warnings = user_entry["warnings"]
        total_warnings = len(warnings)
        start_index = (page - 1) * L
        end_index = min(start_index + L, total_warnings)
        current_warnings = warnings[start_index:end_index]

        emb = discord.Embed(title="User Warnings", description="")
        for index, warning in enumerate(current_warnings, start=start_index + 1):
            emb.add_field(name=f"Warning {index}", value=f"Time: <t:{warning['time']}:f>\nMessage: {warning['message']}", inline=False)
        emb.set_author(name=f"Requested by {interaction.user}")
        n = Pagination.compute_total_pages(total_warnings, L)
        emb.set_footer(text=f"Page {page} of {n}")
        return emb, n

    await Pagination(interaction, get_page).navigate()

@client.tree.command()
async def hello(interaction: discord.Interaction):
    """Says Hello!"""
    await interaction.response.send_message(f'Hi, {interaction.user.mention}')

@client.tree.command()
@app_commands.describe(first_value='The first value you want to add something to', second_value='The value you want to add to the first value')
async def add(interaction: discord.Interaction, first_value: int, second_value: int):
    """Adds numbers!"""
    await interaction.response.send_message(f'{first_value} + {second_value} = {first_value + second_value}')


@client.tree.command()
@app_commands.rename(text_to_send='text')
@app_commands.describe(text_to_send='Text to send in the current channel')
async def send(interaction: discord.Interaction, text_to_send: str):
    """Sends text into the current channel!"""
    await interaction.response.send_message(text_to_send)

@client.tree.command()
@app_commands.describe(member='The member you want to get the joined date from; defaults to the user who uses the command')
async def joined(interaction: discord.Interaction, member: Optional[discord.Member] = None):
    """Shows when a member joined the server!"""
    member = member or interaction.user
    await interaction.response.send_message(f'{member} joined {discord.utils.format_dt(member.joined_at)}')

@client.tree.context_menu(name="Show Current Spotify")
async def user_spotify(interaction: discord.Interaction, member: discord.Member):
    user = interaction.guild.get_member(member.id)

    for activity in user.activities:
        if type(activity) == discord.Spotify:
            list_as_string = ', '.join(map(str, activity.artists))
#            await interaction.response.send_message(f"**{user.display_name}** is listening to **{activity.album}** by **{list_as_string}** on Spotify")

            spotify_showembed = Embed(
                description=f"🎵 **{user.display_name}** is listening to **{activity.title}** on **{activity.album}** by **{list_as_string}** on Spotify",
                color=discord.Colour.green(),
                url=activity.track_url
                )

            spotify_showembed.set_image(url=activity.album_cover_url)
            view = showspotifybutton()
            view.add_item(discord.ui.Button(label="Go to track", style=discord.ButtonStyle.link, url=activity.track_url))
            await interaction.response.send_message(embed=spotify_showembed, view=view)

        else:
            spotify_notlistening = Embed(
                description=f"😔 **{user.display_name}** isnt listening to spotify :(",
                color=discord.Colour.red(),
                )

            await interaction.response.send_message(embed=spotify_notlistening)
    else:
        spotify_notlistening = Embed(
            description=f"😔 **{user.display_name}** isnt listening to spotify :(",
            color=discord.Colour.red(),
            )

        await interaction.response.send_message(embed=spotify_notlistening)


@client.tree.command(name="myspotify")
async def myspotify(interaction: discord.Interaction, member: Optional[discord.Member] = None):
    """Shows what a user is listening to on Spotify"""
    member = member or interaction.user
    user = interaction.guild.get_member(member.id)

    spotify_activity = None  # Flag to check if Spotify is found

    # Iterate over the user's activities and look for Spotify
    for activity in user.activities:
        if isinstance(activity, discord.Spotify):
            spotify_activity = activity
            break  # We found Spotify, no need to check further

    if spotify_activity:
        list_as_string = ', '.join(spotify_activity.artists)

        # Create the embed to show song info
        spotify_showembed = Embed(
            description=f"🎵 **{user.display_name}** is listening to **{spotify_activity.title}** on **{spotify_activity.album}** by **{list_as_string}** on Spotify",
            color=discord.Colour.green(),
            url=spotify_activity.track_url
        )

        spotify_showembed.set_image(url=spotify_activity.album_cover_url)

        # Create a button to go to the track
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="Go to track", style=discord.ButtonStyle.link, url=spotify_activity.track_url))

        await interaction.response.send_message(embed=spotify_showembed, view=view)

    else:
        # If not listening to Spotify
        spotify_notlistening = Embed(
            description=f"😔 **{user.display_name}** isn't listening to Spotify.",
            color=discord.Colour.red(),
        )
        
        # Check if interaction has already been responded to
        if interaction.response.is_done():
            # If already responded, use follow-up
            await interaction.followup.send(embed=spotify_notlistening)
        else:
            # Send initial response
            await interaction.response.send_message(embed=spotify_notlistening)

@client.tree.command()
@app_commands.describe(input="Any song which you want to find")
async def searchspotifysongs(interaction: discord.Interaction, input: str):
    """Search your favourite songs"""

    currentchannel = client.get_channel(interaction.MIKU_id)

    track_name = input
    search_results = spotifyclient.search(track_name).get_tracks()

    for track in search_results:
            artists = ", ".join(artist.name for artist in track.artists)
            spotify_showembed = Embed(
                title=f"Track: **{track.name}** - Artists: **{artists}**",
                color=discord.Colour.green(),
                url=track.url
                )

            spotify_showembed.set_image(url=track.album.images[0].url)
            view = showspotifybutton()
            view.add_item(discord.ui.Button(label="Go to track", style=discord.ButtonStyle.link, url=track.url))
            await interaction.response.send_message(embed=spotify_showembed, view=view)

@client.tree.command(name="find_artist", description="Search your favourite artist")
@app_commands.describe(artist_name="The name of the artist you want to find")
async def find_artist(interaction: discord.Interaction, *, artist_name: str):
    """Searches your favourite artist"""

    search_results = sp.search(q=artist_name, type="artist")

    if search_results["artists"]["items"]:
        artist = search_results["artists"]["items"][0]
        profile_picture_url = artist["images"][0]["url"]

        spotify_showembed = Embed(
            title=f"Artist: **{artist['name']}**",
            color=discord.Colour.green()
        )
        
        spotify_showembed.set_image(url=profile_picture_url)

        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="Go to Artist", style=discord.ButtonStyle.link, url=artist['external_urls']['spotify']))

        await interaction.response.send_message(embed=spotify_showembed, view=view)
    else:
        spotify_showembed = Embed(
            title=f"😔 No results found for the artist: {artist_name}",
            color=discord.Colour.red()
        )
        await interaction.response.send_message(embed=spotify_showembed)



@client.tree.command()
@app_commands.describe(member='The member you want to kick')
@app_commands.check(is_mod)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: Optional[str] = None):
    """Kicks a member"""
    await member.kick(reason=reason)
    await interaction.response.send_message(
        f'Kicked {member} by {interaction.user} for ***"{reason}"*** at <t:{generate_unix_time_code()}:F>'
    )

@kick.error
async def role_error(interaction: discord.Interaction, error):
    await interaction.response.send_message("Apparently, you don't have permission to kick anyone :(", ephemeral=True)

@client.tree.command()
@app_commands.describe(member='The member you want to ban')
@app_commands.check(is_mod)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: Optional[str] = None):
    """Bans the member"""
    await member.ban(reason=reason)
    await interaction.response.send_message(
        f'Banned {member} by {interaction.user} for ***"{reason}"*** at <t:{generate_unix_time_code()}:F>'
    )

@ban.error
async def role_error(interaction: discord.Interaction, error):
    await interaction.response.send_message("Apparently, you don't have permission to ban anyone :(", ephemeral=True)

@client.tree.command()
@app_commands.rename(timeouttime="time")
@app_commands.describe(member="The member you want to timeout", timeouttime="The amount of time to timeout a user (Minutes)")
@app_commands.check(is_mod)
async def timeout(interaction: discord.Interaction, member: discord.Member, timeouttime: Optional[int] = None, reason: Optional[str] = None):
    """Timeouts the member"""
    timeout_duration = timedelta(minutes=timeouttime)
    await member.timeout(timeout_duration, reason=reason)
    await interaction.response.send_message(
        f"User has been timed out for {timeouttime} minutes for the reason of ***\"{reason}\"*** at <t:{generate_unix_time_code()}:F>"
    )

@timeout.error
async def role_error(interaction: discord.Interaction, error):
    await interaction.response.send_message("Apparently, you don't have permission to timeout anyone :(", ephemeral=True)

@client.tree.command(name="warn", description="Warn a user")
@app_commands.describe(member="The member to warn", reason="The reason for the warning")
@app_commands.check(is_mod)
async def warn(interaction: discord.Interaction, member: discord.Member, reason: str):
    """Warns the user"""
    data = load_warnings()

    # Find the user or create a new entry
    user_entry = next((user for user in data["users"] if user["user_id"] == member.id), None)
    if user_entry is None:
        user_entry = {
            "name": member.name,
            "user_id": member.id,
            "warnings": []
        }
        data["users"].append(user_entry)

    current_time = generate_unix_time_code()
    warning_entry = {
        "message": reason,
        "time": current_time
    }
    
    user_entry["warnings"].append(warning_entry)
    save_warnings(data)
    
    warn_embed = Embed(description=f"***{member.mention} has been warned by {interaction.user.mention} for reason :- ***{reason}", color=discord.Color.red())
    await interaction.response.send_message(embed=warn_embed)


@warn.error
async def warn_error(interaction: discord.Interaction, error: Exception):
    await interaction.response.send_message("Aparently, you dont have permision to warn anyone :(", ephemeral=True)

@client.tree.command(name="get_warns", description="Get a member's warn history")
@app_commands.describe(member="The member you want to get their warning log")
@app_commands.check(is_mod)
async def get_warns(interaction: discord.Interaction, member: discord.Member):
    """Get a member's warn history"""

    data = load_warnings()

    # Find the user entry
    user_entry = next((user for user in data["users"] if user["user_id"] == member.id), None)

    if user_entry is None or not user_entry["warnings"]:
        await interaction.response.send_message(f"{member.mention} has no warnings.", ephemeral=True)
        return

    # Create an embed to show the warnings
    show_warnings = Embed(title=f"Warn History for {member.name} \n", color=discord.Color.red())

    for warning in user_entry["warnings"]:
        show_warnings.add_field(name=f"<t:{warning["time"]}:f>", value=warning["message"], inline=False)

    await interaction.response.send_message(embed=show_warnings)


@client.tree.command()
@app_commands.describe(member="The member whose warnings you want to clear")
@app_commands.check(is_mod)
async def clearwarnings(interaction: discord.Interaction, member: discord.Member):
    """Clears all warnings of a user"""
    with open(WARNSON_PATH, 'r') as f:
        user_data = json.load(f)

    # Find the user entry
    user_entry = next((user for user in user_data["users"] if user["name"] == member.name), None)
    if user_entry:
        user_entry["warnings"] = []
        await interaction.response.send_message(f"All warnings for {member.mention} have been cleared.")
    else:
        await interaction.response.send_message(f"No warnings found for {member.mention}.")

    # Save updated data to file
    with open(WARNSON_PATH, 'w') as f:
        json.dump(user_data, f, indent=4)

voiceclint = None

@client.tree.command(name='join', description='Bot joins the voice channel')
async def join(interaction: discord.Interaction):
    global voiceclint
    if not interaction.user.voice:
        await interaction.response.send_message("You are not connected to a voice channel", ephemeral=True)
        return
    
    channel = interaction.user.voice.channel
    voiceclint = await channel.connect()
    await interaction.response.send_message(f"Joined {channel.name}")

@client.tree.command(name='leave', description='Bot leaves the voice channel')
async def leave(interaction: discord.Interaction):
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("Disconnected from the voice channel")
    else:
        await interaction.response.send_message("I'm not in a voice channel", ephemeral=True)

DEFAULT_VOLUME = 50  # Default volume level (1-100)

@client.tree.command()
async def terminate(interaction: discord.Interaction):
    """Terminates the bot (CAN ONLY BE USED BY THE DEVLOPER)"""
    if interaction.user.id == 1130883869625815232:
        try:
            await interaction.response.send_message("Terminating", ephemeral=True)
            await client.close()
            print("Here***********:")
            
        except SystemExit as systemexit:
            print("systemexit:", systemexit)
    
    else:
        await interaction.response.send_message("The Devloper of the bot (overtue.) can only use this command", ephemeral=True)

@client.tree.command(name="queue")
async def queue(interaction: discord.Interaction):
    if music_queue.is_empty():
        await interaction.response.send_message("The queue is empty.")
    else:
        current_song_info = music_queue.get_next_song_info()
        queue_str = f"Current song: {current_song_info['title']}\n\nQueue:\n"
        for i, song in enumerate(music_queue.queue[1:], 1):
            queue_str += f"{i}. {song['title']}\n"
        await interaction.response.send_message(queue_str)
        
@client.tree.command(name="play")
async def play(interaction: discord.Interaction, *, search: str):
    await interaction.response.defer()
    try:
        url = await search_youtube(search)
        player = await YTDLSource.from_url(url, loop=client.loop, stream=True)
        if interaction.user.voice is None:
            await interaction.followup.send("You are not connected to a voice channel.")
            return

        if interaction.guild.voice_client is None:
            await interaction.user.voice.channel.connect()

        interaction.guild.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)
        await interaction.followup.send(f'Now playing: {player.title}', view=VcControlView(interaction.guild.voice_client))
    except Exception as e:
        await interaction.followup.send(f"An error occurred: {e}")

async def start_playing(interaction, voice_client):
    next_song_info = music_queue.get_next_song_info()
    if next_song_info:
        track_name, artist_names, album_cover_url, track_url = next_song_info

        youtube_search_url = f"ytsearch:{track_name} {artist_names}"
        player = await YTDLSource.from_url(youtube_search_url, loop=client.loop, stream=True)
        music_queue.remove_next_song()  # Remove the song from the queue now that it's downloading

        voice_client.play(player, after=lambda e: client.loop.create_task(play_next(interaction, voice_client)))

        embed = discord.Embed(title="Now Playing", description=f"**{track_name}** by **{artist_names}**", color=discord.Color.blue())
        embed.set_thumbnail(url=album_cover_url)
        embed.add_field(name="Spotify URL", value=track_url, inline=False)
        embed.add_field(name="Duration", value=f"0:00 / {time.strftime('%M:%S', time.gmtime(player.duration))}", inline=True)

        message = await interaction.followup.send(embed=embed, view=VcControlView(voice_client))
        
        start_update_time_task(player, message, embed, voice_client)

async def play_next(interaction, voice_client):
    if len(music_queue) > 0:
        player, channel = music_queue.pop(0)
        voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else asyncio.run_coroutine_threadsafe(play_next(interaction, voice_client), client.loop))
        await channel.send(f"Now playing: {player.title}", view=VcControlView(voice_client))
        start_update_time_task(player, interaction)
    
@tasks.loop(seconds=1)
async def update_time_task(player, message, embed, voice_client):
    try:
        while True:
            while voice_client.is_playing():
                elapsed_time = time.strftime('%M:%S', time.gmtime(time.time() - player.start_time))
                embed.set_field_at(1, name="Duration", value=f"{elapsed_time} / {time.strftime('%M:%S', time.gmtime(player.duration))}", inline=True)
                await message.edit(embed=embed)
                await asyncio.sleep(1)
    except Exception as e:
        print(f"Error updating time: {e}")

def start_update_time_task(player, interaction):
    async def update_time_task():
        try:
            message = await interaction.channel.send("Updating time...")
            while voice_client.is_playing():
                elapsed_time = time.strftime('%M:%S', time.gmtime(time.time() - player.start_time))
                embed = discord.Embed(title="Now Playing", description=player.title)
                embed.add_field(name="Duration", value=f"{elapsed_time} / {time.strftime('%M:%S', time.gmtime(player.duration))}", inline=True)
                await message.edit(embed=embed)
                await asyncio.sleep(1)
        except Exception as e:
            print(f"Error updating time: {e}")

    client.loop.create_task(update_time_task())
        
def stop_update_time_task():
    if update_time_task.is_running():
        update_time_task.cancel()

async def play_next(interaction, voice_client):
    if len(music_queue) == 0:
        stop_update_time_task()
        await voice_client.disconnect()
    else:
        await start_playing(interaction, voice_client)

async def next_song(ctx: discord.Interaction):
    global current_song
    if len(music_queue) > 0:
        next_track = music_queue.pop(0)
        current_song = next_track['track']
        await play_song(ctx, next_track['interaction'], next_track['track'])


async def play_song(ctx: discord.Interaction, interaction: discord.Interaction, track: dict):
    try:
        global voice_client
        
        track_name = track['name']
        artist_names = ', '.join(artist['name'] for artist in track['artists'])
        track_url = track['external_urls']['spotify']
        album_cover_url = track['album']['images'][0]['url'] if track['album']['images'] else None

        # Extract audio from YouTube as a workaround for Spotify audio streaming
        youtube_search_url = f"ytsearch:{track_name} {artist_names}"
        player = await YTDLSource.from_url(youtube_search_url, loop=client.loop, stream=True)
        voice_client.play(player, after=lambda e: asyncio.run_coroutine_threadsafe(next_song(ctx), client.loop))

        # Create buttons for controlling playback
        embed = discord.Embed(title="Now Playing", description=f"**{track_name}** by **{artist_names}**", color=discord.Color.blue())
        embed.set_thumbnail(url=album_cover_url)
        embed.add_field(name="Spotify URL", value=track_url, inline=False)
        embed.add_field(name="Duration", value="0:00", inline=True)  # Initial duration

        message = await interaction.followup.send(embed=embed, view=VcControlView(voice_client, None, embed))
        view = VcControlView(voice_client, message, embed)
        view.message = message
        await message.edit(view=view)

        # Update the duration in the embed while the song is playing
        current_time = 0
        while voice_client.is_playing():
            formatted_time = time.strftime('%M:%S', time.gmtime(current_time))
            total_duration = time.strftime('%M:%S', time.gmtime(player.data['duration']))
            embed.set_field_at(1, name="Duration", value=f"{formatted_time} / {total_duration}", inline=True)
            await message.edit(embed=embed)
            current_time += 1
            await asyncio.sleep(1)

        # Remove the buttons once the song is finished
        await message.edit(view=None)
    except Exception as e:
        print(f'Error: {e}')
        await interaction.followup.send('Error playing the song.', ephemeral=True)

@client.tree.command(name='skip', description='Skip the current song')
async def skip(interaction: discord.Interaction):
    if not interaction.guild.voice_client or not interaction.guild.voice_client.is_playing():
        await interaction.response.send_message('There is no song playing to skip.', ephemeral=True)
        return

    interaction.guild.voice_client.stop()
    await interaction.response.send_message('Skipped the current song.', ephemeral=True)

@client.tree.command(name='stop', description='Stop playback and clear the queue')
async def stop(interaction: discord.Interaction):
    global music_queue, busy
    music_queue = []
    busy = False
    if interaction.guild.voice_client:
        interaction.guild.voice_client.stop()
    await interaction.response.send_message('Stopped playback and cleared the queue.', ephemeral=True)

@client.tree.command(description='Add a song to the queue')
async def add_song(interaction: discord.Interaction, query: str):
    await interaction.response.defer()

    try:
        results = sp.search(q=query, type='track', limit=1)
        if results and 'tracks' in results and results['tracks']['items']:
            track = results['tracks']['items'][0]
            track_name = track['name']
            artist_names = ', '.join(artist['name'] for artist in track['artists'])
            track_url = track['external_urls']['spotify']
            album_cover_url = track['album']['images'][0]['url'] if track['album']['images'] else None

            music_queue.add_song((track_name, artist_names, album_cover_url, track_url))
            await interaction.followup.send(f"Added **{track_name}** by **{artist_names}** to the queue", ephemeral=True)
        else:
            await interaction.followup.send('No song found!', ephemeral=True)
    except Exception as e:
        print(f'Error: {e}')
        await interaction.followup.send('Error fetching song from Spotify', ephemeral=True)

@client.tree.command(description='Remove a song from the queue')
async def remove_song(interaction: discord.Interaction, index: int):
    song = music_queue.remove_next_song(index - 1)  # Adjust for 0-based indexing
    if song:
        track_name, artist_names, _, _ = song
        await interaction.response.send_message(f"Removed {track_name} by {artist_names} from the queue", ephemeral=True)
    else:
        await interaction.response.send_message(f"No song found at position {index}", ephemeral=True)

# @tasks.loop(seconds=1)
# async def update_duration(message: discord.Message, player: YTDLSource):
#     current_time = 0

#     while player.is_playing():
#         formatted_time = time.strftime('%M:%S', time.gmtime(current_time))
#         embed = message.embeds[0]
#         embed.set_field_at(1, name="Duration", value=formatted_time, inline=True)
#         await message.edit(embed=embed)

#         current_time += 1
#         await asyncio.sleep(1)

#     # Remove the buttons once the song is finished
#     await message.edit(view=None)
    
# start_time = time.time()  # Store the start time when playback begins

# @tasks.loop(seconds=10)
# async def update_duration(interaction: discord.Interaction):
#     if interaction.guild.voice_client and interaction.guild.voice_client.is_playing():
#         current_position = interaction.guild.voice_client.source._position  # Adjust as per your source
#         current_time = time.strftime('%M:%S', time.gmtime(current_position))
        
#         # Check if there's an embed in the last message
#         if interaction.message.embeds:
#             embed = interaction.message.embeds[0]
#             embed.set_field_at(1, name="Duration", value=current_time, inline=True)
#             await interaction.edit_original_message(embed=embed)
#         else:
#             # If no embed found, create a new one and send it
#             embed = discord.Embed(title="Now Playing", color=discord.Color.blue())
#             embed.add_field(name="Duration", value=current_time, inline=True)
#             await interaction.edit_original_message(embed=embed)

# @update_duration.before_loop
# async def before_update_duration():
#     await client.wait_until_ready()


@client.tree.command(name='volume', description='Adjust the volume of the audio (1-100)')
@app_commands.describe(vol='Volume level (1-100)')
async def volume(interaction: discord.Interaction, vol: int):
    if interaction.guild.voice_client:
        if 1 <= vol <= 100:
            # Convert from 1-100 range to 0.0-2.0 range
            volume_level = vol / 50.0
            interaction.guild.voice_client.source.volume = volume_level
            await interaction.response.send_message(f'Set volume to {vol}')
        else:
            await interaction.response.send_message('Volume must be between 1 and 100', ephemeral=True)
    else:
        await interaction.response.send_message("I'm not in a voice channel", ephemeral=True)

@client.tree.command(name='pause', description='Pause the currently playing audio')
async def pause(interaction: discord.Interaction):
    if interaction.guild.voice_client and interaction.guild.voice_client.is_playing():
        interaction.guild.voice_client.pause()
        await interaction.response.send_message("Audio paused")
    else:
        await interaction.response.send_message("Not currently playing any audio", ephemeral=True)

@client.tree.command(name='resume', description='Resume the paused audio')
async def resume(interaction: discord.Interaction):
    if interaction.guild.voice_client and interaction.guild.voice_client.is_paused():
        interaction.guild.voice_client.resume()
        await interaction.response.send_message("Audio resumed")
    else:
        await interaction.response.send_message("Audio is not paused", ephemeral=True)

@client.tree.context_menu(name='Report to Moderators')
async def report_message(interaction: discord.Interaction, message: discord.Message):
    # We're sending this response message with ephemeral=True, so only the command executor can see it
    await interaction.response.send_message(
        f'Thanks for reporting this message by {message.author.mention} to our moderators.', ephemeral=True
    )

    # Handle report by sending it into a log channel
    log_channel = interaction.guild.get_channel(1290913389895221249)  # replace with your channel id

    embed = discord.Embed(title='Reported Message')
    if message.content:
        embed.description = message.content

    embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
    embed.timestamp = message.created_at

    url_view = discord.ui.View()
    url_view.add_item(discord.ui.Button(label='Go to Message', style=discord.ButtonStyle.url, url=message.jump_url))

    await log_channel.send(embed=embed, view=url_view)


@client.tree.command()
async def feedback(interaction: discord.Interaction):
    """Give feedback!"""
    await interaction.response.send_modal(Feedback())

@client.tree.command()
async def banappeal(interaction: discord.Interaction):
    """Request a ban appeal"""
    await interaction.response.send_modal(BanAppeal())

asyncio.run(client.run("MTI5NDI1MjUwODUwMzQ3ODMxNA.GhQaxI.T8xV-ScDRZjWoY4qcZSnIPnfcd-ZQpxhpK98VA"))