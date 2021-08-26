from os import name
import discord
import random
import csv
from asyncio.windows_events import NULL
from discord_slash import cog_ext
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext

guild_ids=[879524619218997278]

class War:
    def __init__(self,title,region,date,attackers,deffenders,army):
        self.title = title
        self.region = region
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
        #army = [["-"]*5]*groups
        army = [[str(random.randint(1000,10000000)) for e in range(5)] for e in range(10)]
        War.save_army(army)
        return army

    def create_embed(war):
        embed = discord.Embed(title=f"{war.title}  -  {war.attackers}  -  {war.deffenders}  -  {war.region}  - {war.date}")
        string = ''
        for i in range(1,len(war.army)+1):
            string = string +  f"**Group {i}\n**" + "```" + " \n".join(war.army[i-1]) + "```" + "\n"
            if i == len(war.army)/2:
                embed.add_field(name="\u200b",value=string, inline=True)
                string = ''
        embed.add_field(name="\u200b",value=string, inline=True)
        composition = '\n**Tanks**\nWarhammer\nGreataxe\nSword and Shield\n\n**Supports**\nLife Staff\n\n**DPS**\nBow\nMusket\nHatchet\nRapier\nIce Gauntlet'
        embed.add_field(name="\u200b",value=composition,inline=True)

        return embed

class WarCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(guild_ids=guild_ids, description="Create a new war")
    async def newwar(self, ctx, title, region = "Windsward", date = "20/09 20:00", attackers = "Guilda X", deffenders = "Guilda Y"):
        groups = 10
        war = War(title,region,date,attackers,deffenders, War.create_army(groups))
        embed = War.create_embed(war)
        await ctx.channel.send(embed=embed)

    # @cog_ext.cog_slash(guild_ids=guild_ids)
    # async def enlist(self, ctx, player, war):
    #     army = War.load_army()
    #     return

    @cog_ext.cog_slash(guild_ids=guild_ids)
    async def _slashtest(self, ctx:SlashContext):
        await ctx.send("deu certo porra")
    
def setup(bot):
    bot.add_cog(WarCommands(bot))
