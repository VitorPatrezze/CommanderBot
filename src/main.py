import discord
from discord.ext import commands

bot = commands.Bot(command_prefix=">")

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

@bot.command()
async def ping(ctx):
	await ctx.channel.send("pong")

bot.run('ODc5NDExOTAxMzkyNjQ2MTQ0.YSPWJw.JjcYRwhwoKN6uF8hPsmkRZu5ksI')