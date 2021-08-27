import discord
from discord import guild
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_choice, create_option

bot = commands.Bot(command_prefix="/")
slash = SlashCommand(bot, sync_commands=True)

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

@bot.command()
async def ping(ctx):await ctx.channel.send(f"Pong! {round(bot.latency * 1000)}ms")    

@slash.slash()
async def clear(ctx, amount=2):
    await ctx.channel.purge(limit=amount)

bot.load_extension('entities.war')
bot.run('ODc5NDExOTAxMzkyNjQ2MTQ0.YSPWJw.JjcYRwhwoKN6uF8hPsmkRZu5ksI')

#/newwar title:tit region:reg date:data attackers:atk defenders:def