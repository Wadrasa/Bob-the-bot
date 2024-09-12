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
    await cxt.send(f"I am Bob")

@bot.command(name="roll", help="Roll a dice")
async def roll_dice(ctx, sides: int = 6):

    dice_roll=random.randint(1, sides)
    await ctx.send(f"You rolled a {sides}-sided dice, and you got {dice_roll}!")


characters = [
    {"name": "Medic TF2", "image_url": "https://cdn.discordapp.com/attachments/1282670940790194188/1283675132283453502/F8C6DE4DE623D6E855A1B3E3E80FD0A155948277.png?ex=66e3db21&is=66e289a1&hm=a5cd331c2c0ea50005bc9647a4e455ff9f1ad9c9cb36afe7f30030eeb7b36b02&"},
    {"name": "Jetstream Sam", "image_url": "https://cdn.discordapp.com/attachments/1282670940790194188/1283675019364270133/image.png?ex=66e3db06&is=66e28986&hm=7cce013e24dc5d198a10c20cf22c9db500d7b0178ddc142bc1161ea1f5152589&"},
    {"name": "*Steve*", "image_url": "https://cdn.discordapp.com/attachments/1282670940790194188/1283676740257845288/VNktIRX.webp?ex=66e3dca0&is=66e28b20&hm=6bf0a08e7da3b8e8987bb5e75accf99393fac48ed9c73dbdb7a57706b276d8fb&"},
    {"name": "Emily", "image_url": "https://example.com/emily.jpg"},
    {"name": "Michael", "image_url": "https://example.com/michael.jpg"},
    {"name": "Anna", "image_url": "https://example.com/anna.jpg"},
    {"name": "Tom", "image_url": "https://example.com/tom.jpg"},
    {"name": "Lucy", "image_url": "https://example.com/lucy.jpg"},
    {"name": "David", "image_url": "https://example.com/david.jpg"},
    {"name": "Jessica", "image_url": "https://example.com/jessica.jpg"}
]


@bot.command(name="fmk")
async def fmk(ctx):
    # Randomly select three characters
    choices = random.sample(characters, 3)

    # Send an embed with the three options
    embed = discord.Embed(title="Fuck, Marry, Kill")

    for i, choice in enumerate(choices, start=1):
        embed.add_field(name=f"{i}. {choice['name']}", value=f"React with {i}️⃣", inline=False)
        # embed.set_image(url=choice["image_url"])  # Add the image

    # Send the embed message
    message = await ctx.send(embed=embed)

    # Add reactions for each choice
    await message.add_reaction("1️⃣")
    await message.add_reaction("2️⃣")
    await message.add_reaction("3️⃣")

    for choice in choices:
        image_embed = discord.Embed()
        image_embed.set_image(url=choice["image_url"])
        await ctx.send(embed=image_embed)

    # Dictionary to map emoji reactions to indexes
    emoji_map = {
        "1️⃣": 0,  # Person 1
        "2️⃣": 1,  # Person 2
        "3️⃣": 2  # Person 3
    }

    # Step 1: Choose Fuck
    await ctx.send("React with who you want to **Share your bed with**!")
    try:
        fuck_reaction, _ = await bot.wait_for("reaction_add", timeout=30.0,
                                              check=lambda reaction, user: user == ctx.author and str(
                                                  reaction.emoji) in emoji_map)
        fuck_choice = choices[emoji_map[str(fuck_reaction.emoji)]]
    except:
        await ctx.send("You're slow, you need to be faster!")
        return

    # Step 2: Choose Marry
    await ctx.send("React with who you want to **Spend your life with**!")
    try:
        marry_reaction, _ = await bot.wait_for("reaction_add", timeout=30.0,
                                               check=lambda reaction, user: user == ctx.author and str(
                                                   reaction.emoji) in emoji_map and choices[emoji_map[
                                                   str(reaction.emoji)]] != fuck_choice)
        marry_choice = choices[emoji_map[str(marry_reaction.emoji)]]
    except:
        await ctx.send("Don't you wanna marry someone? It sure seems like cuz ur so slow")
        return

    # Step 3: The last one is automatically "Kill"
    kill_choice = [person for person in choices if person != fuck_choice and person != marry_choice][0]

    # Send final message with the choices
    await ctx.send(
        f"You chose to **Spend a night with** {fuck_choice['name']}, **Share your life with** {marry_choice['name']}, and **Brutally murder** {kill_choice['name']}. 😈")



bot.run(config.TOKEN)