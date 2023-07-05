import discord, json, logging
from discord.ext import commands
from discord.commands import SlashCommandGroup
from helpers import db_manager
import marshal

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

  # DEPRECATING THIS - will refactor when database is re-done
  # @commands.slash_command(description = "Set up a mythic+ ping for your server!")
  # async def setup_ping(self, ctx): # a slash command will be created with the name "ping"
  #   if not ctx.author.guild_permissions.administrator:
  #     await ctx.response.send_message("You are not authorized to run this command.", ephemeral=True)
  #   else:
  #     guild = ctx.guild
  #     await ctx.respond("**Mythic+ setup:** Choose a role to be pinged whenever a new mythic+ group is formed.", view=SelectView(guild))

  # @commands.slash_command(description = "Reset your server's mythic+ ping.")
  # async def reset_ping(self, ctx):
  #   if not ctx.author.guild_permissions.administrator:
  #     await ctx.response.send_message("You are not authorized to run this command.", ephemeral=True)
  #   else:
  #     guild_id = ctx.guild.id
  #     db_manager.remove_mythic_plus_ping((guild_id,))
  #     await ctx.response.send_message("Mythic+ ping removed!")

  async def is_admin(ctx):
    return ctx.author.guild_permissions.administrator
  
  def initialized(self, guild_id):
    if db_manager.get_guild_id((guild_id,)) is not None:
      return True
    return False
  
  setup = SlashCommandGroup("setup","setup")

  @setup.command()
  @commands.check(is_admin)
  async def init(self, ctx):
    if self.initialized(ctx.guild.id):
      await ctx.respond("You have already initialized gecko for this server!", ephemeral=True)
    else:
      guild_id = ctx.guild.id
      db_manager.initialize_server((guild_id, None))
      await ctx.response.send_message("Server initialized!")
      self.initialized = True
  
  @setup.command()
  @commands.check(is_admin)
  async def add_keys_channel(self, ctx):
    if not self.initialized:
      await ctx.response.send_message("Please use `/setup init` before running this command.", ephemeral=True)
    else:
      guild_id = ctx.guild.id
      channel_id = ctx.channel.id
      db_manager.add_keys_channel((channel_id, guild_id))
      await ctx.respond("This channel can now use `/keys` commands!", ephemeral=True)

  @init.error
  @add_keys_channel.error
  async def setup_error(self, ctx, error):
    if isinstance(error, discord.errors.CheckFailure):
      await ctx.respond("You do not have permission to run this command.", ephemeral=True)
    else:
      raise error

def setup(bot):
  bot.add_cog(Setup(bot))
  print(f"Setup cog loaded - {__name__}")

def teardown(bot):
  bot.remove_cog(Setup(bot))
  print("Setup cog unloaded")
    