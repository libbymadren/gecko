import discord, json, logging
from discord.ext import commands

class Setup(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.slash_command(description = "Setup gecko for your server!")
  async def setup(self, ctx): # a slash command will be created with the name "ping"
    await ctx.respond(f"Pong! Latency is {self.bot.latency}")

def setup(bot):
  bot.add_cog(Setup(bot))
  print(f"Setup cog loaded - {__name__}")

def teardown(bot):
  bot.remove_cog(Setup(bot))
  print("Setup cog unloaded")
    