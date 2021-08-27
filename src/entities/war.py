import os
import discord
import random
from entities.player import Player
from entities.db import save_war
from discord_slash import cog_ext
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext

#Como conseguir tirar esse guild_ids
guild_ids=[879524619218997278]

class War:
    def __init__(self,title,region,date,attackers,defenders,army):
        self.title = title
        self.region = region
        self.date = date
        self.attackers = attackers
        self.defenders = defenders
        self.army = army

    def create_army(groups):
        #army = [["-"]*5]*groups
        army = [[Player(name=str(p+1),lvl='lvl',role='',primary='',secundary='') for p in range(5)] for e in range(10)]
        return army

    def create_embed(war):
        embed = discord.Embed(title=f"{war.title}  -  {war.attackers}  -  {war.defenders}  -  {war.region}  - {war.date}")
        string = ''
        for i in range(1,len(war.army)+1):
            string = string +  f"**Group {i}\n**" + "```" + " \n".join(p.name for p in war.army[i-1]) + "```" + "\n"
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
    async def newwar(self, ctx, title, region = "Windsward", date = "20/09 20:00", attackers = "Guilda X", defenders = "Guilda Y"):
        groups = 10
        war = War(title,region,date,attackers,defenders,army = War.create_army(groups))
        guild_id = str(879524619218997278)
        save_war(guild_id, war)
        embed = War.create_embed(war)
        await ctx.channel.send(embed=embed)

    #criar grupo "war"
    # @cog_ext.cog_slash(guild_ids=guild_ids)
    # async def enlist(self, ctx, player, war):
    #     army = War.load_army()
    #     return

    @cog_ext.cog_slash(guild_ids=guild_ids)
    async def _slashtest(self, ctx:SlashContext):
        await ctx.send("deu certo porra")
    
def setup(bot):
    bot.add_cog(WarCommands(bot))
