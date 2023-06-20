# First test code - will likely change. Probably all of it maybe even perhaps?

import discord, os, time
from discord.ext import commands
from dotenv import dotenv_values
from lib.utils import get_logger, get_config
import sqlite3

env = dict(dotenv_values(".env"))

geckoConfig = get_config(f"{env['CONFIG_DIR']}/gecko.json")

logger = get_logger(
  name = f"gecko_{int(time.time())}",
  configFile= geckoConfig.get("loggingConfigPath", f"{env['CONFIG_DIR']}/logger.json")
)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(allowed_mentions=discord.AllowedMentions(roles=True, users=True, everyone=False), intents=intents)

# Not used atm - if we want anything that isnt a slash_command I think we need this?
@bot.event
async def on_message(message):
  if not message.author.bot:
    await bot.process_commands(message)

@bot.slash_command(description = "Load a cog")
@commands.is_owner()
async def load(ctx, extension):
  bot.load_extension(f'cogs.{extension}')
  await ctx.send(f'Loaded {extension} cog')

@bot.slash_command(description = "Unload a cog")
@commands.is_owner()
async def unload(ctx, extension):
  bot.unload_extension(f'cogs.{extension}')
  await ctx.send(f'Unloaded {extension} cog')

@bot.slash_command(description = "Reload a cog")
@commands.is_owner()
async def reload(ctx, extension):
  bot.reload_extension(f'cogs.{extension}')
  await ctx.send(f'Reloaded {extension} cog')

# TODO: move this to db_manager once more tables are added
@bot.event
async def on_ready():
  db = sqlite3.connect('database.db')
  cursor = db.cursor()
  cursor.execute(
    '''
    CREATE TABLE IF NOT EXISTS mythic_plus_pings(
    guild_id INTEGER PRIMARY KEY,
    ping_role INTEGER
    )
    '''
  )
  db.commit()

if __name__ == "__main__":
  # load cogs
  for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
      bot.load_extension(f'cogs.{filename[:-3]}')
  
  bot.run(env['DISCORD_TOKEN'])