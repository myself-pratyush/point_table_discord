import discord
from discord.ext import commands
import os
import psycopg2

# Define the intents your bot will use
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Initialize the bot with intents and a command prefix
bot = commands.Bot(command_prefix="!", intents=intents)

# Load or create a JSON file to store points
DATABASE_URL = os.getenv("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL, sslmode="require")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS points (
    user_id BIGINT PRIMARY KEY,
    points INTEGER
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

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.command()
@commands.has_permissions(administrator=True)
async def add_points(ctx, user: discord.Member, points: int):
    add_points_db(user.id, points)
    await ctx.send(f'{user.name} has been awarded {points} points!')

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

bot.run(os.getenv('DISCORD_TOKEN'))