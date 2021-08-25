from asyncio.windows_events import NULL
import discord
from discord.ext import commands
import random
import csv

class War:
    def __init__(self,title,location,date,attackers,deffenders,army):
        self.title = title
        self.location = location
        self.date = date
        self.attackers = attackers
        self.deffenders = deffenders
        self.army = army
    
    def save_army(army):
        with open('army.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            [writer.writerow(r) for r in army]
        return

    def load_army():
        with open('army.csv', 'r') as csvfile:
            reader = csv.reader(csvfile)
            army = [[str(e) for e in r] for r in reader]
        return army

    def create_army(groups):
        army = [[f"{random.randint(1123, 9534)}"]*5]*groups
        War.save_army(army)
        return army

    def create_embed(title, army):
        embed = discord.Embed(title=title)

        for i in range(1,len(army)+1):
            embed.add_field(name = f"Group {i}",value=" - ".join(army[i-1]), inline=False)
        return embed

class WarCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases = ['w'])
    async def war(self, ctx, title = "Guerra", location = NULL, date = NULL, attackers = NULL, deffenders = NULL, groups = 10):
        war = War(title,location,date,attackers,deffenders, War.create_army(groups))
        embed = War.create_embed(war.title, war.army)
        await ctx.channel.send(embed=embed)

    @commands.command()
    async def enlist(self,ctx,name):
        army = War.load_army()
        return

    @commands.command()
    async def army(self,ctx):
        await ctx.channel.send(embed=War.create_embed("See army", War.load_army()))
    
def setup(bot):
    bot.add_cog(WarCommands(bot))
