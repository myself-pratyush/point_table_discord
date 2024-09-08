import discord
from discord.ext import commands
import os
import psycopg2

# Define intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Initialize the bot with intents and command prefix
bot = commands.Bot(command_prefix="!", intents=intents)

# Database connection setup
DATABASE_URL = os.getenv("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL, sslmode="require")
cur = conn.cursor()

# Create a table for points if it doesn't exist
cur.execute("""
CREATE TABLE IF NOT EXISTS points (
    user_id BIGINT PRIMARY KEY,
    points INTEGER
);
""")
conn.commit()

# Function to add points to a user
def add_points_db(user_id, points):
    cur.execute("""
    INSERT INTO points (user_id, points)
    VALUES (%s, %s)
    ON CONFLICT (user_id)
    DO UPDATE SET points = points.points + EXCLUDED.points;
    """, (user_id, points))
    conn.commit()

# Function to get the leaderboard
def get_leaderboard_db():
    cur.execute("SELECT user_id, points FROM points ORDER BY points DESC")
    return cur.fetchall()

# Event triggered when the bot is ready
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

# Add points to a user (admin only)
@bot.command()
@commands.has_permissions(administrator=True)
async def add_points(ctx, user: discord.Member, points: int):
    add_points_db(user.id, points)
    await ctx.send(f'{user.name} has been awarded {points} points!')

# Show the leaderboard
@bot.command()
async def leaderboard(ctx):
    leaderboard_data = get_leaderboard_db()
    
    if not leaderboard_data:
        await ctx.send("No points have been awarded yet.")
        return

    leaderboard_message = "**Leaderboard:**\n"
    for i, (user_id, points) in enumerate(leaderboard_data, start=1):
        user = await bot.fetch_user(user_id)
        leaderboard_message += f"{i}. {user.name}: {points} points\n"

    await ctx.send(leaderboard_message)

# Run the bot with the token from environment variables
bot.run(os.getenv('DISCORD_TOKEN'))
