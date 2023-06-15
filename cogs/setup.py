import discord, json, logging
from discord.ext import commands
import sqlite3
from helpers import db_manager

class SelectView(discord.ui.View):
  def __init__(self, guild, timeout=180):
    super().__init__(timeout=timeout)
    self.guild = guild

  @discord.ui.role_select(max_values = 1)
  async def select_callback(self, select, interaction): 
    ping = (self.guild.id, select.values[0].id)
    db_manager.add_mythic_plus_ping(ping)
    await interaction.response.send_message(f"Mythic+ ping selected!")

class Setup(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.slash_command(description = "Set up a mythic+ ping for your server!")
  async def setup_ping(self, ctx): # a slash command will be created with the name "ping"
    if not ctx.author.guild_permissions.administrator:
      await ctx.response.send_message("You are not authorized to run this command.", ephemeral=True)
    else:
      guild = ctx.guild
      await ctx.respond("**Mythic+ setup:** Choose a role(s) to be pinged whenever a new mythic+ group is formed.", view=SelectView(guild))

  @commands.slash_command(description = "Reset your server's mythic+ ping.")
  async def reset_ping(self, ctx):
    if not ctx.author.guild_permissions.administrator:
      await ctx.response.send_message("You are not authorized to run this command.", ephemeral=True)
    else:
      guild_id = ctx.guild.id
      db_manager.remove_mythic_plus_ping((guild_id,))
      await ctx.response.send_message("Mythic+ ping removed!")

def setup(bot):
  bot.add_cog(Setup(bot))
  print(f"Setup cog loaded - {__name__}")

def teardown(bot):
  bot.remove_cog(Setup(bot))
  print("Setup cog unloaded")
    