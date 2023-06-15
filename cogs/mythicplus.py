import discord, json, logging
from discord.ext import commands
from datetime import datetime as dt
from lib.utils import get_config
from helpers import db_manager

# remove this if there's a better way to get the config data for the choices parameter
config = get_config('./config/mythicplus.json')
activeGroupIDs = []
# gotta decide what to use as the string when no one is signed up, if any at all?
DEFAULT_ENTRY = ""

class MythicKeyGroup():
  def __init__(self, groupOwner):
    self.groupOwner = groupOwner
    self.tank = ""
    self.healer = ""
    self.dps = []
  
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
      "dps":self.dps,
    }
  
  def reset_group(self): 
    self.tank = ""
    self.healer = ""
    self.dps = []

  def remove_user(self, user):
    # match user:
    #   case self.tank:
    #     self.tank = ""
    #     return 0
    #   case self.healer:
    #     self.healer = ""
    #     return 1
    #   case default:
    #     if user in self.dps:
    #       self.dps.remove(user)
    #       return 2
    if user == self.tank:
      self.tank = ""
      return "tank"
    elif user == self.healer:
      self.healer = ""
      return "healer"
    elif user in self.dps:
      self.dps.remove(user)
      return "dps"
  
  def getGroupList(self):
    groupList = [self.tank, self.healer]
    groupList.extend(self.dps)
    return groupList

class ButtonView(discord.ui.View): 
  def __init__(self, embed, msg, group, timeout=None):
    super().__init__(timeout=timeout)
    self.embed = embed
    self.msg = msg
    self.group = group
    self.dpsCount = 0

  @discord.ui.button(label="Tank", row=0, style=discord.ButtonStyle.primary, emoji=discord.PartialEmoji.from_str("<:tank_icon_white:1117620737558196244>"))
  async def tank_button(self, button, interaction):
    user = interaction.user.id
    if user in self.group.getGroupList():
      await interaction.response.send_message("You've already signed up for this group!", ephemeral=True)
    elif self.group.tank:
      await interaction.response.send_message("This group is full on tanks!", ephemeral=True) 
    else:
      self.group.tank = user
      self.embed.set_field_at(index=0,name="Tank:",value=f"<@{user}>")
      await interaction.response.defer()
      await interaction.edit_original_response(content=self.msg, embed=self.embed)

  @discord.ui.button(label="Healer", row=0, style=discord.ButtonStyle.primary, emoji=discord.PartialEmoji.from_str("<:healer_icon_white:1117620718155354162>"))
  async def heal_button(self, button, interaction):
    user = interaction.user.id
    if user in self.group.getGroupList():
      await interaction.response.send_message("You've already signed up for this group!", ephemeral=True)
    elif self.group.healer:
      await interaction.response.send_message("This group is full on healers!", ephemeral=True) 
    else:
      self.group.healer = user
      self.embed.set_field_at(index=1,name="Healer:",value=f"<@{user}>", inline=False)
      await interaction.response.defer()
      await interaction.edit_original_response(content=self.msg, embed=self.embed)

  @discord.ui.button(label="DPS", row=0, style=discord.ButtonStyle.primary, emoji=discord.PartialEmoji.from_str("<:dps_icon_white:1117620696818921493>"))
  async def dps_button(self, button, interaction):
    user = interaction.user.id
    if user in self.group.getGroupList():
      await interaction.response.send_message("You've already signed up for this group!", ephemeral=True)
    elif len(self.group.dps) >= 3:
      await interaction.response.send_message("This group is full on DPS!", ephemeral=True) 
    else:
      embed_dict = self.embed.to_dict()
      dps_value = embed_dict["fields"][2]["value"]
      self.group.dps.append(user)
      dps_value += f"\n<@{user}>"
      self.embed.set_field_at(index=2,name="DPS:",value=dps_value)
      await interaction.response.defer()
      await interaction.edit_original_response(content=self.msg, embed=self.embed)

  @discord.ui.button(label="Remove Self", row=0, style=discord.ButtonStyle.secondary)
  async def remove_self_button(self, button, interaction):
    user = interaction.user.id
    role = self.group.remove_user(user)
    if role == "tank":
      self.embed.set_field_at(index=0,name="Tank:",value=DEFAULT_ENTRY)
    elif role == "healer":
      self.embed.set_field_at(index=1,name="Healer:",value=DEFAULT_ENTRY, inline=False)
    elif role == "dps":
      dps_value = ""
      for x in self.group.dps:
        dps_value += f"\n<@{x}>"
      self.embed.set_field_at(index=2,name="DPS:",value=dps_value)
          
    await interaction.response.defer()
    await interaction.edit_original_response(content=self.msg, embed=self.embed)

  # TODO: make this button only visible to the group owner
  # actually, I'm just going to hide this button for now, I don't think it'll be useful other than for debugging
  # @discord.ui.button(label="Reset Group", row=1, style=discord.ButtonStyle.secondary)
  # async def reset_group_button(self, button, interaction):
  #   self.group.reset_group()
  #   embed_dict = self.embed.to_dict()
  #   self.embed.set_field_at(index=0,name="Tank:",value=DEFAULT_ENTRY)
  #   self.embed.set_field_at(index=1,name="Healer:",value=DEFAULT_ENTRY, inline=False)
  #   self.embed.set_field_at(index=2,name="DPS:",value=DEFAULT_ENTRY)
  #   await interaction.response.defer()
  #   await interaction.edit_original_response(content=self.msg, embed=self.embed)

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
    embed = discord.Embed(
      title=f"+{level} {self.config['season2']['dungeons'][dungeon]}",
      description="",
      colour=0x00b0f4,
      timestamp=dt.now()
    )
  
    embed.add_field(name="Tank:", value=DEFAULT_ENTRY, inline=True)
    embed.add_field(name="Healer:", value=DEFAULT_ENTRY, inline=False)
    embed.add_field(name="DPS:", value=DEFAULT_ENTRY, inline=True)
        
    result = db_manager.get_mythic_plus_ping((ctx.guild.id,))
    ping_intro = f"Hey <@&{result[0]}>, " if result is not None else ""
    author = ctx.author.id
    msg = ping_intro + f"<@{author}> is looking for a mythic+ group!"
    await ctx.respond(msg, embed=embed, view=ButtonView(embed, msg, MythicKeyGroup(author)))

def setup(bot):
  bot.add_cog(MythicPlus(bot, get_config('./config/mythicplus.json')))
  print(f"Mythicplus cog loaded - {__name__}")

def teardown(bot):
  bot.remove_cog(MythicPlus(bot, get_config('./config/mythicplus.json')))
  print("Mythicplus cog unloaded")