import os
import discord
import random
from entities.player import Player
from entities.db import create_war
from entities.db import load_army
from discord_slash import cog_ext
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext

#Como conseguir tirar esse guild_ids
guild_ids=[879524619218997278]

class Army: 
    def __init__(self, comp, dps, tanks, supports, weapon_count):
        self.comp = comp
        self.dps = dps
        self.tanks = tanks
        self.supports = supports
        self.weapon_count = weapon_count
    
    def init_weapon_count():
        dicts = {}
        weapons = ['Sword and Shield', 'Rapier', 'Hatchet', 'Spear', 'Great Axe', 'War Hammer', 'Bow', 'Musket', 'Fire Staff', 'Life Staff', 'Ice Gauntlet']
        for i in weapons:
            dicts[i] = 0
        return dicts

    def create_army():
        comp = [[Player(name='-',lvl='',role='',primary='',secundary='') for p in range(5)] for e in range(10)]
        army = Army(comp,0,0,0,Army.init_weapon_count())
        return army
    
class War:
    def __init__(self,title,region,date,attackers,defenders,army):
        self.title = title
        self.region = region
        self.date = date
        self.attackers = attackers
        self.defenders = defenders
        self.army = army

    def create_embed(war):
        embed = discord.Embed(title=f"{war.title}  -  {war.region}  -  {war.attackers}  -  {war.defenders}  - {war.date}", color = discord.Color.dark_red())
        string = ''
        for i in range(1,len(war.army.comp)+1):
            string = string +  f"**Group {i}\n**" + "```" + " \n".join('{0}. {1}'.format(n+1, p.name) for n,p in enumerate(war.army.comp[i-1])) + "```" + "\n"
            if i == len(war.army.comp)/2:
                embed.add_field(name="\u200b",value=string, inline=True)
                string = ''
        embed.add_field(name="\u200b",value=string, inline=True)
        army_info = '\n**Tanks**\nWarhammer\nGreataxe\nSword and Shield\n\n**Supports**\nLife Staff\n\n**DPS**\nBow\nMusket\nHatchet\nRapier\nIce Gauntlet'
        embed.add_field(name="\u200b",value=army_info,inline=True)
        return embed

class WarCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(guild_ids=guild_ids, description="Create a new event (war, invasion, PvP Quests, etc)")
    async def newevent(self, ctx, title, region, date, attackers, defenders):
        war = War(title,region,date,attackers,defenders,army = Army.create_army())
        create_war(ctx.guild.id, war)
        await ctx.channel.send(embed=War.create_embed(war))

    @cog_ext.cog_slash(guild_ids=guild_ids, description="Shows specified war info")
    async def war(self, ctx, war_title):
        load_army(ctx.guild.id, war_title)
        await ctx.channel.send("war")

    #criar grupo "war"
    # @cog_ext.cog_slash(guild_ids=guild_ids)
    # async def enlist(self, ctx, player, war):
    #     army = War.load_army()
    #     return
    
def setup(bot):
    bot.add_cog(WarCommands(bot))
