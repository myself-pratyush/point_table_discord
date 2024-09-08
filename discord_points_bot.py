import discord
from discord.ext import commands
import os

# Define the intents your bot will use
intents = discord.Intents.default()
intents.message_content = True  # Enable reading message content

# Initialize the bot with intents
bot = commands.Bot(command_prefix="!", intents=intents)

# A simple event
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

# A simple command
@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

# Run the bot using the token from environment variables
bot.run(os.getenv('DISCORD_TOKEN'))
