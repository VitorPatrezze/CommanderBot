import discord
from discord import guild
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_choice, create_option
from discord_components import *

bot = commands.Bot(command_prefix="/")
slash = SlashCommand(bot, sync_commands=True)

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))
    DiscordComponents(bot)

bot.load_extension('commands')
bot.run('ODc5NDExOTAxMzkyNjQ2MTQ0.YSPWJw.JjcYRwhwoKN6uF8hPsmkRZu5ksI')