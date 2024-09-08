import discord
from discord.ext import commands
import os
import psycopg2
import logging
from difflib import get_close_matches

# setup logging
logging.basicConfig(level=logging.WARNING)


# Define the intents your bot will use
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Initialize the bot with intents and a command prefix
bot = commands.Bot(command_prefix="!", intents=intents)

# Handle invalid commands
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith('!'):
        command = message.content.split()[0][1:]  # Extract command
        if command not in bot.commands:  # Check if command exists
            logging.warning(f"Invalid command used: {command}")
            close_matches = get_close_matches(command, bot.commands, n=1)
            if close_matches:
                suggested_command = close_matches[0]
                await message.channel.send(f"Invalid command. Did you mean `!{suggested_command}`?")
            else:
                await message.channel.send("Invalid command. Please check your input.")
    else:
        await bot.process_commands(message)  # Ensure other commands are processed

        
# Connect to PostgreSQL database
DATABASE_URL = os.getenv("DATABASE_URL")
conn = psycopg2.connect(DATABASE_URL, sslmode="require")
cur = conn.cursor()

# Create points table if it doesn't exist
cur.execute("""
CREATE TABLE IF NOT EXISTS points (
    user_id BIGINT PRIMARY KEY,
    points INTEGER DEFAULT 0
);
""")
conn.commit()

def add_points_db(user_id, points):
    cur.execute("""
    INSERT INTO points (user_id, points)
    VALUES (%s, %s)
    ON CONFLICT (user_id)
    DO UPDATE SET points = points.points + EXCLUDED.points;
    """, (user_id, points))
    conn.commit()

def get_leaderboard_db():
    cur.execute("SELECT user_id, points FROM points ORDER BY points DESC")
    return cur.fetchall()

def get_user_points_db(user_id):
    cur.execute("SELECT points FROM points WHERE user_id = %s", (user_id,))
    result = cur.fetchone()
    return result[0] if result else 0

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.command(name='add_points', aliases=['add_point','addpoint','Add_point'])
@commands.has_permissions(administrator=True)
async def add_points(ctx, user: discord.Member, points: int):
    add_points_db(user.id, points)
    await ctx.send(f'{user.global_name} has been awarded {points} points!')

@bot.command(name='leaderboard', aliases=['Leaderboard','Leader'])
async def leaderboard(ctx):
    leaderboard_data = get_leaderboard_db()
    
    if not leaderboard_data:
        await ctx.send("No points have been awarded yet.")
        return

    leaderboard_message = "**Leaderboard:**\n"
    for i, (user_id, points) in enumerate(leaderboard_data, start=1):
        user = await bot.fetch_user(user_id)
        leaderboard_message += f"{i}. {user.global_name}: {points} points\n"

    await ctx.send(leaderboard_message)

@bot.command(name='points', aliases=['point','Point'])
async def points(ctx, user: discord.Member = None):
    # If no user is mentioned, use the command invoker
    if user is None:
        user = ctx.author

    user_points = get_user_points_db(user.id)
    await ctx.send(f'{user.global_name} has {user_points} points.')

bot.run(os.getenv('DISCORD_TOKEN'))