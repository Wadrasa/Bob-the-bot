import random
import config
from sys import executable

import discord
from discord.app_commands import describe
from discord.ext import commands
import asyncio
import yt_dlp as youtube_dl
import os
import imageio_ffmpeg as ffmpeg

ffmpeg_path = ffmpeg.get_ffmpeg_exe()


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

youtube_dl.utils.bug_reports_message = lambda: ''

discord.Embed

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
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # bind to ipv4
}
ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # Take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, executable=ffmpeg_path, **ffmpeg_options), data=data)

@bot.command(name='join', help='Joins a voice channel')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send(f"{ctx.message.author.name} is not connected to a voice channel")
        return
    else:
        channel = ctx.message.author.voice.channel

    await channel.connect()

@bot.command(name='leave', help='Leaves the voice channel')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.send("The bot is not connected to a voice channel.")

@bot.command(name='play', help='Plays a song from YouTube')
async def play(ctx, url):
    try:
        server = ctx.message.guild
        voice_channel = server.voice_client

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=bot.loop, stream=True)
            voice_channel.play(player, after=lambda e: print(f"Player error: {e}") if e else None)

        await ctx.send(f'Now playing: {player.title}')
    except Exception as e:
        print(e)
        await ctx.send("Couldn't play the audio, we're very sorry")

@bot.command(name='pause', help='Pauses the audio')
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        voice_client.pause()
        await ctx.send("Audio paused.")
    else:
        await ctx.send("No audio is playing currently.")

@bot.command(name='resume', help='Resumes the audio')
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_paused():
        voice_client.resume()
        await ctx.send("Audio resumed.")
    else:
        await ctx.send("Audio is not paused.")

@bot.command(name='stop', help='Stops the audio')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        voice_client.stop()
        await ctx.send("Audio stopped.")
    else:
        await ctx.send("No audio is playing currently.")

@bot.event
async def on_ready():
    print("Bot Ready!!")
    print(f"Logged in as {bot.user.name}")


@bot.command(name="ping", help="pong")
async def ping(ctx):
    await ctx.send("pong")

@bot.command(name="hello", help="You can say hello to a bot! (Get some friends...)")
async def hello(cxt):
    await cxt.send(f"OMG HIIIIII")

@bot.command(name="roll", help="Roll a dice")
async def roll_dice(ctx, sides: int = 6):

    dice_roll=random.randint(1, sides)
    await ctx.send(f"You rolled a {sides}-sided dice, and you got {dice_roll}!")

bot.run(config.TOKEN)

# import random
# import discord
# from discord.ext import commands
#
# bot = commands.Bot(commands_prefix="!")
#
# characters = [
#     {"name": "John", "image_url": "https://example.com/john.jpg"},
#     {"name": "Sarah", "image_url": "https://example.com/sarah.jpg"},
#     {"name": "Jake", "image_url": "https://example.com/jake.jpg"},
#     {"name": "Emily", "image_url": "https://example.com/emily.jpg"},
#     {"name": "Michael", "image_url": "https://example.com/michael.jpg"},
#     {"name": "Anna", "image_url": "https://example.com/anna.jpg"},
#     {"name": "Tom", "image_url": "https://example.com/tom.jpg"},
#     {"name": "Lucy", "image_url": "https://example.com/lucy.jpg"},
#     {"name": "David", "image_url": "https://example.com/david.jpg"},
#     {"name": "Jessica", "image_url": "https://example.com/jessica.jpg"}
# ]
#
# @bot.command(name="fmk")
# async def fmk(ctx):
#     choices = random.sample(characters, 3)
#
#     embed = discord.Embed(title="Fuck, Marry, Kill")
#
#     for i, choice in enumerate(choices, start=1):
#         embed.add_field(name=f"{i}. {choice['name']}", value=f"react with {i}, inline=false)
