import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import os
from dotenv import load_dotenv

load_dotenv()
# Configure the bot
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True  # Enable message content intent

bot = commands.Bot(command_prefix="!", intents=intents)

# Join voice channel
@bot.command(name="join")
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
    else:
        await ctx.send("You need to be in a voice channel to use this command!")

# Leave voice channel
@bot.command(name="leave")
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Disconnected from the voice channel!")
    else:
        await ctx.send("I'm not in a voice channel!")

# Play music from URL
@bot.command(name="play")
async def play(ctx, url: str):
    if ctx.voice_client is None:
        await ctx.send("I'm not connected to a voice channel! Use `!join` to connect.")
        return
    
    # Define the YouTube downloader options
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        audio_url = info['url']

    # Play the audio
    ctx.voice_client.stop()
    ctx.voice_client.play(discord.FFmpegPCMAudio(audio_url), after=lambda e: print(f"Finished playing: {e}"))
    await ctx.send(f"Now playing: {info['title']}")

# Stop playing
@bot.command(name="stop")
async def stop(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("Stopped the music!")
    else:
        await ctx.send("No music is playing!")

# Bot token
# Run the bot
bot.run(os.getenv('BOT_TOKEN_DJ'))
