import discord
from discord.ext import commands

bot = commands.Bot(command_prefix=".")

bot.load_extension('events.war')

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

@bot.command()
async def ping(ctx):
	await ctx.channel.send(f"Pong! {round(bot.latency * 1000)}ms")    

@bot.command()
async def clear(ctx, amount=2):
    await ctx.channel.purge(limit=amount)

bot.run('ODc5NDExOTAxMzkyNjQ2MTQ0.YSPWJw.JjcYRwhwoKN6uF8hPsmkRZu5ksI')