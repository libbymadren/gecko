import discord, json, logging
from discord.ext import commands
from datetime import datetime as dt
from lib.utils import get_config

# remove this if there's a better way to get the config data for the choices parameter
config = get_config('./config/mythicplus.json')
activeGroupIDs = []
DEFAULT_ENTRY = "Still required!"


class MythicKeyGroup():
  def __init__(self, groupOwner, keyLevel, dungeon, embed):
    self.groupOwner = groupOwner
    self.dungeon = dungeon
    self.keyLevel = keyLevel
    self.tank = []
    self.healer = []
    self.dps = []
    self.players = set()
    self.embed = embed
  

  def set_tank(self, player):
    
    # if self.tanks in 
    # if not self.tanks:

    pass


  def get_group(self):
    return {
      "groupOwner":self.groupOwner,
      "dungeon":self.dungeon,
      "keyLevel":self.keyLevel,
      "tank":self.tank,
      "healer":self.healer,
      "dps":self.dps
    }

# TODO: for tank and healer, make sure that people cannot sign up for the role after someone already has
# for DPS, make sure more than 3 people can't sign up
class ButtonView(discord.ui.View): 
  @discord.ui.button(label="Tank", row=0, style=discord.ButtonStyle.primary)
  async def tank_button(self, button, interaction):
    embed.set_field_at(index=0,name="Tank:",value=f"<@{interaction.user.id}>")
    await interaction.response.defer()
    await interaction.edit_original_response(content=msg, embed=embed)

  @discord.ui.button(label="Healer", row=0, style=discord.ButtonStyle.primary)
  async def heal_button(self, button, interaction):
    embed.set_field_at(index=1,name="Healer:",value=f"<@{interaction.user.id}>")
    await interaction.response.defer()
    await interaction.edit_original_response(content=msg, embed=embed)

  @discord.ui.button(label="DPS", row=0, style=discord.ButtonStyle.primary)
  async def dps_button(self, button, interaction):
    embed_dict = embed.to_dict()
    currentDpsVal = embed_dict["fields"][2]["value"]
    if currentDpsVal == DEFAULT_ENTRY:
      dps_value = embed_dict["fields"][2]["value"] + f"\n<@{interaction.user.id}>"


    embed.set_field_at(index=2,name="DPS:",value=dps_value)
    await interaction.response.defer()
    await interaction.edit_original_response(content=msg, embed=embed)

  @discord.ui.button(label="Remove Self", row=0, style=discord.ButtonStyle.secondary)
  async def remove_self_button(self, button, interaction):
    embed_dict = embed.to_dict()
    embed.set_field_at(index=0,name="Tank:",value=DEFAULT_ENTRY)
    embed.set_field_at(index=1,name="Healer:",value=DEFAULT_ENTRY)
    embed.set_field_at(index=2,name="DPS:",value=DEFAULT_ENTRY)
    await interaction.response.defer()
    await interaction.edit_original_response(content=msg, embed=embed)

  @discord.ui.button(label="Reset Group", row=0, style=discord.ButtonStyle.secondary)
  async def reset_group_button(self, button, interaction):
    embed_dict = embed.to_dict()
    embed.set_field_at(index=0,name="Tank:",value=DEFAULT_ENTRY)
    embed.set_field_at(index=1,name="Healer:",value=DEFAULT_ENTRY)
    embed.set_field_at(index=2,name="DPS:",value=DEFAULT_ENTRY)
    await interaction.response.defer()
    await interaction.edit_original_response(content=msg, embed=embed)

class MythicPlus(commands.Cog):
  def __init__(self, bot, config):
    self.bot = bot
    self.config = config

  @commands.Cog.listener()
  async def on_member_join(self, member):
    channel = member.guild.system_channel
    if channel is not None:
      await channel.send(f'Welcome {member.mention}.')

  @commands.slash_command(description = "Starts a key group.")
  async def keys(self, ctx, level: discord.Option(int), dungeon: discord.Option(str, choices = config['season2']['dungeons'])):
    # again, this is bad practice, but I'm not familiar enough w/ this to know how I should maintain this embed's state
    global embed

    embed = discord.Embed(
      title=f"+{level} {self.config['season2']['dungeons'][dungeon.upper()]}",
      description="",
      colour=0x00b0f4,
      timestamp=dt.now()
    )
  
    embed.add_field(name="Tank:", value=DEFAULT_ENTRY, inline=True)
    embed.add_field(name="Healer:", value=DEFAULT_ENTRY, inline=True)
    embed.add_field(name="DPS:", value=DEFAULT_ENTRY, inline=True)
        
    global msg
    msg = f"<@{ctx.author.id}> is looking for a mythic+ group!"
    await ctx.respond(msg, embed=embed, view=ButtonView())

def setup(bot):
  bot.add_cog(MythicPlus(bot, get_config('./config/mythicplus.json')))
  print(f"Mythicplus cog loaded - {__name__}")

def teardown(bot):
  bot.remove_cog(MythicPlus(bot, get_config('./config/mythicplus.json')))
  print("Mythicplus cog unloaded")
    