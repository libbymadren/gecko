import discord, json, logging
from discord.commands import SlashCommandGroup
from discord.ext import commands
import time as t
import datetime as dt
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
  def __init__(self, embed, msg, ctx, group, timeout=None):
    super().__init__(timeout=timeout)
    self.embed = embed
    self.msg = msg
    self.ctx = ctx
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
      if user != self.group.groupOwner:
        await self.ctx.respond(f"Hey <@{self.group.groupOwner}>! A new tank just signed up for your group!", ephemeral=True)

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
      if user != self.group.groupOwner:
        await self.ctx.respond(f"Hey <@{self.group.groupOwner}>! A new healer just signed up for your group!", ephemeral=True)

  @discord.ui.button(label="DPS", row=0, style=discord.ButtonStyle.primary, emoji=discord.PartialEmoji.from_str("<:dps_icon_white:1117620696818921493>"))
  async def dps_button(self, button, interaction):
    user = interaction.user.id
    if user in self.group.getGroupList():
      await interaction.response.send_message("You've already signed up for this group!", ephemeral=True)
    if len(self.group.dps) >= 3:
      await interaction.response.send_message("This group is full on DPS!", ephemeral=True) 
    else:
      embed_dict = self.embed.to_dict()
      dps_value = embed_dict["fields"][2]["value"]
      self.group.dps.append(user)
      dps_value += f"\n<@{user}>"
      self.embed.set_field_at(index=2,name="DPS:",value=dps_value)
      await interaction.response.defer()
      await interaction.edit_original_response(content=self.msg, embed=self.embed)
      if user != self.group.groupOwner:
        await self.ctx.respond(f"Hey <@{self.group.groupOwner}>! A new DPS just signed up for your group!", ephemeral=True)

  @discord.ui.button(label="Remove Self", row=1, style=discord.ButtonStyle.secondary)
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

  # we'll see if people actually want the close group button
  @discord.ui.button(label="Close Group", row=1, style=discord.ButtonStyle.secondary)
  async def close_group_button(self, button, interaction):
    if interaction.user.id != self.group.groupOwner:
      await interaction.response.send_message("Only the group owner can do that!", ephemeral=True)
    elif button.label == "Undo Close Group":
      self.enable_all_items()
      button.label = "Close Group"
      await interaction.response.defer()
      await interaction.edit_original_response(content=self.msg, embed=self.embed, view=self)
    else:
      self.disable_all_items()
      button.disabled = False
      button.label = "Undo Close Group"
      await interaction.response.defer()
      await interaction.edit_original_response(content="~~" + self.msg + "~~", embed=self.embed, view=self)

class MythicPlus(commands.Cog):
  def __init__(self, bot: discord.Bot, config):
    self.bot = bot
    self.config = config

  async def is_valid_channel(ctx):
    keys_channels = db_manager.get_keys_channels((ctx.guild.id,))
    return (ctx.channel.id,) in keys_channels

  keys = SlashCommandGroup("keys", "Start a new mythic+ group!")

  @keys.command(description = "Start a group to run your mythic+ key!")
  @commands.check(is_valid_channel)
  @commands.cooldown(1, 900, commands.BucketType.user)
  async def lfm(
    self,
    ctx: discord.ApplicationContext, 
    level: discord.Option(int, "the level of your key", min_value=2), 
    dungeon: discord.Option(str, "the dungeon name", choices = config['season2']['dungeons']), 
    time = discord.Option(str, "[optional] the time you want to run this key in the future in the format \"XXh XXm\", eg: 15m, 1h 30m", required=False, default = 'ASAP'),
    note = discord.Option(str, "[optional] a note specifying any further info for this key", required=False, default = ''),
  ):
    parsed_time = self.parse_time(time)
    if parsed_time == False:
      await ctx.response.send_message("Incorrect time format. Please use the format `XXh XXm`, for example: 15m, 1h 30m, etc.", ephemeral=True)
    else:
      title = f"+{level} {self.config['season2']['dungeons'][dungeon]}"
      embed = self.create_embed(title, parsed_time, note)
      
      # TODO - make this no longer hardcoded when pings and database are reworked
      author = ctx.author.id
      msg = f"<@{author}> is looking to run their key! <@&1112106399367962625>"

      await ctx.respond(msg, embed=embed, view=ButtonView(embed, msg, ctx, MythicKeyGroup(author)))
    
  @keys.command(description = "Get a group together to run anyone's key!")
  @commands.check(is_valid_channel)
  @commands.cooldown(1, 900, commands.BucketType.user)
  async def lfg(
    self,
    ctx,
    title: discord.Option(str, "a title for your group"), 
    min_level: discord.Option(int, "the minimum level of the key you want to run", min_value=2), 
    max_level: discord.Option(int, "the maximum level of the key you want to run", min_value=2), 
    time = discord.Option(str, "[optional] the time you want to run this key in the future in the format \"XXh XXm\", eg: 15m, 1h 30m", required=False, default = 'ASAP'),
    note = discord.Option(str, "[optional] a note specifying any further info for this key", required=False, default = ''),
  ):
    parsed_time = self.parse_time(time)
    if parsed_time == False:
      await ctx.response.send_message("Incorrect time format. Please use the format `XXh XXm`, for example: 15m, 1h 30m, etc.", ephemeral=True)
    else:
      embed = self.create_embed(title, parsed_time, note, min_level, max_level)
      
      # TODO - make this no longer hardcoded when pings and database are reworked
      author = ctx.author.id
      msg = f"<@{author}> is looking for a group to run some keys! <@&1112106399367962625>"

      await ctx.respond(msg, embed=embed, view=ButtonView(embed, msg, ctx, MythicKeyGroup(author)))

  @lfm.error
  @lfg.error
  async def keys_error(self, ctx, error):
    # NOTE - this is an error message specific to TA's server setup. This should be changed to be something 
    # more generic at a later time.
    if isinstance(error, discord.errors.CheckFailure):
      await ctx.respond("Hey there! You are not authorized to run `/keys` in this channel. Please make your group listings in <#1110961934611791945> or <#1124845386692042813>." + 
                        " If you can't access these channels, please head to Channels & Roles (located at the top of the channel list) and select your region role (NA/OCE or EU). Thanks!", 
                        ephemeral=True)
    elif isinstance(error, commands.CommandOnCooldown):
      await ctx.respond("Whoa there! To avoid spam, you can only make a new `/keys` posting once every 15 minutes. Please wait a little bit and try again.", ephemeral=True)
    else:
      raise error
  
  def parse_time(self, time):
    if time == 'ASAP':
      return time
    try: 
      if len(time.split()) > 1:
        time_obj = t.strptime(time, "%Hh %Mm")
      else:
        if time[-1] == 'm':
          time_obj = t.strptime(time, "%Mm")
        else:
          time_obj = t.strptime(time, "%Hh")
      seconds = dt.timedelta(hours=time_obj.tm_hour, minutes=time_obj.tm_min).total_seconds()
      start_time = dt.datetime.now() + dt.timedelta(0, seconds)
      return discord.utils.format_dt(start_time, style="R")
    except ValueError:
      return False

  def create_embed(self, title, time, note, min_level=1, max_level=1):
    if note != '':
      note = '\"*' + note + '*\"'
    
    desc = ''
    if min_level >= 2 and max_level >= 2:
      desc += f"Levels: **+{min_level}** to **+{max_level}**\n"
    desc += f"When: {time}\n{note}"
    
    embed = discord.Embed(
      title=title,
      description=desc,
      colour=0x00b0f4,
      timestamp=dt.datetime.now()
    )
    embed.add_field(name="Tank:", value=DEFAULT_ENTRY, inline=True)
    embed.add_field(name="Healer:", value=DEFAULT_ENTRY, inline=False)
    embed.add_field(name="DPS:", value=DEFAULT_ENTRY, inline=True)
    return embed

def setup(bot):
  bot.add_cog(MythicPlus(bot, get_config('./config/mythicplus.json')))
  print(f"Mythicplus cog loaded - {__name__}")

def teardown(bot):
  bot.remove_cog(MythicPlus(bot, get_config('./config/mythicplus.json')))
  print("Mythicplus cog unloaded")