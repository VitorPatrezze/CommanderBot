import discord
from entities.army import Army
from entities.player import Player
from entities.war import War
from entities.db import create_war, load_war, load_army, enlist
from discord_slash import cog_ext
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext

#Como conseguir tirar esse guild_ids
guild_ids=[879524619218997278]
    
class WarCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    def create_embed(war):
        embed = discord.Embed(title=f"{war.title}  -  {war.region}  -  {war.date}  -  Atackers: {war.attackers}  -  Defenders: {war.defenders}", color = discord.Color.dark_red())
        embed.set_thumbnail(url='https://images.ctfassets.net/j95d1p8hsuun/29peK2k7Ic6FsPAVjHWs8W/06d3add40b23b20bbff215f6979267e8/NW_OPENGRAPH_1200x630.jpg')
        string = ''
        for i in range(1,len(war.army.comp)+1):
            string = string +  f"**Group {i}\n**" + "```" + " \n".join(f'{n+1}. {p.name}' for n,p in enumerate(war.army.comp[i-1])) + "```" + "\n"
            if i == len(war.army.comp)/2:
                embed.add_field(name="\u200b",value=string, inline=True)
                string = ''
        embed.add_field(name="\u200b", value=string, inline=True)
        embed.add_field(name="\u200b", value=Army.armyInfoString(war.army), inline=True)
        return embed    

    @cog_ext.cog_slash(guild_ids=guild_ids, description="Create a new event (war, invasion, PvP Quests, etc)")
    async def newevent(self, ctx, title, region, date, attackers, defenders):
        war = War(title,region,date,attackers,defenders,army = Army.create_army())
        create_war(ctx.guild.id, war)
        await ctx.channel.send(embed=WarCommands.create_embed(war))

    @cog_ext.cog_slash(guild_ids=guild_ids, description="Shows specified war info")
    async def war(self, ctx, war_title):
        war = load_war(ctx.guild.id, war_title)
        await ctx.channel.send(embed=WarCommands.create_embed(war))

    @cog_ext.cog_slash(guild_ids=guild_ids)
    async def enlist(self, ctx, war_title, name, role, lvl, primary, secundary='', group=0, pos=0 ):
        army = load_army(ctx.guild.id, war_title)
        player = Player(name,lvl,role,primary,secundary)
        enlist(ctx.guild.id, war_title, army, player, group, pos)
        await ctx.channel.send(f"Enlisted player {player.name}")
    
def setup(bot):
    bot.add_cog(WarCommands(bot))
