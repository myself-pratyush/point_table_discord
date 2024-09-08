import discord
from discord.ext import commands
import os
import json

# Define the intents your bot will use
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Initialize the bot with intents and a command prefix
bot = commands.Bot(command_prefix="!", intents=intents)

# Load or create a JSON file to store points
POINTS_FILE = 'points.json'

def load_points():
    try:
        with open(POINTS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_points(points):
    with open(POINTS_FILE, 'w') as f:
        json.dump(points, f)

# Event triggered when the bot is ready and connected to Discord
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

# A command to add points to a user (admin only)
@bot.command()
@commands.has_permissions(administrator=True)
async def add_points(ctx, user: discord.Member, points: int):
    point_data = load_points()

    # Add or update points for the user
    if str(user.id) in point_data:
        point_data[str(user.id)] += points
    else:
        point_data[str(user.id)] = points

    save_points(point_data)
    await ctx.send(f'{user.name} has been awarded {points} points!')

# A command to show the leaderboard
@bot.command()
async def leaderboard(ctx):
    point_data = load_points()

    # Sort users by points in descending order
    sorted_users = sorted(point_data.items(), key=lambda x: x[1], reverse=True)

    if not sorted_users:
        await ctx.send("No points have been awarded yet.")
        return

    # Create a leaderboard message
    leaderboard_message = "**Leaderboard:**\n"
    for i, (user_id, points) in enumerate(sorted_users, start=1):
        user = await bot.fetch_user(int(user_id))  # Fetch user by ID
        leaderboard_message += f"{i}. {user.global_name}: {points} points\n"

    await ctx.send(leaderboard_message)

# A command to view points for a specific user
@bot.command()
async def points(ctx, user: discord.Member):
    point_data = load_points()
    user_points = point_data.get(str(user.id), 0)
    await ctx.send(f'{user.name} has {user_points} points.')

# Run the bot using the token from environment variables
bot.run(os.getenv('DISCORD_TOKEN'))
