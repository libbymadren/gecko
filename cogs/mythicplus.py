import discord, json, logging
from discord.ext import commands
from datetime import datetime as dt
from utils import get_config

class MyView(discord.ui.View): 
  @discord.ui.button(label="🛡 Tank", row=0, style=discord.ButtonStyle.primary)
  async def first_button_callback(self, button, interaction):
    await interaction.response.send_message("You pressed me!")

  @discord.ui.button(label="💚 Healer", row=0, style=discord.ButtonStyle.primary)
  async def second_button_callback(self, button, interaction):
    await interaction.response.send_message("You pressed me!")

  @discord.ui.button(label="⚔️ DPS", row=0, style=discord.ButtonStyle.primary)
  async def third_button_callback(self, button, interaction):
    await interaction.response.send_message("You pressed me!")


class MythicPlus(commands.Cog):
  def __init__(self, bot, config):
    self.bot = bot
    self.config = config

  @commands.Cog.listener()
  async def on_member_join(self, member):
    channel = member.guild.system_channel
    if channel is not None:
      await channel.send(f'Welcome {member.mention}.')


  # TODO - Can dungeons be stored as a list to provide options to the user, instead of freeform?
  @commands.slash_command(description = "Starts a key group.")
  async def keys(self, ctx, level: discord.Option(int), dungeon: discord.Option(str)):
    try: 
      embed = discord.Embed(
        title=f"+{level} {self.config['season2']['dungeons'][dungeon]}",
        description="",
        colour=0x00b0f4,
        timestamp=dt.now()
      )
      
      embed.add_field(name="Tank", value="This is the field value.")
      embed.add_field(name="Healer", value="This is the field value.", inline=False)
      embed.add_field(name="DPS", value="This is the field value.")
          
      await ctx.respond(f"<@{ctx.author.id}> is looking for a mythic+ group!", embed=embed, view=MyView())
    except KeyError:
      await ctx.respond("Invalid dungeon code. Please use /keycodes to see a list of all possible dungeon codes.")

def setup(bot):
  bot.add_cog(MythicPlus(bot, get_config('./config/mythicplus.json')))
  print(f"Mythicplus cog loaded - {__name__}")

def teardown(bot):
  bot.remove_cog(MythicPlus(bot, get_config('./config/mythicplus.json')))
  print("Mythicplus cog unloaded")
    