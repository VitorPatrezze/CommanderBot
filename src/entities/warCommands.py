import discord
from entities.army import Army
from entities.player import Player
from entities.war import War
from entities.db import create_war, load_war, load_army, enlist, wars_list
from discord_slash import cog_ext
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext

#Como conseguir tirar esse guild_ids
guild_ids=[879524619218997278]
    
class WarCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    def create_embed(war):
        embed = discord.Embed(title=f"{war.title}  -  {war.region}  -  {war.date}\nAtackers: {war.attackers}  -  Defenders: {war.defenders}", color = discord.Color.dark_red())
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
        war = War(title.lower(),region.lower(),date,attackers,defenders,army = Army.create_army())
        create_war(ctx.guild.id, war)
        await ctx.channel.send(embed=WarCommands.create_embed(war))

    @cog_ext.cog_slash(guild_ids=guild_ids, description="Shows specified war info")
    async def war(self, ctx, war_title):
        guild_id = ctx.guild.id
        valid_wars = wars_list(guild_id)
        print(valid_wars)
        if war_title.lower() not in valid_wars:
            await ctx.channel.send(f"`There is no war with title '{war_title}' for this guild`")
        else:
            war = load_war(guild_id, war_title.lower())
            await ctx.channel.send(embed=WarCommands.create_embed(war))

    @cog_ext.cog_slash(guild_ids=guild_ids)
    async def enlist(self, ctx, war_title, name, role, level, weapon, secundary='', group=0, pos=0 ):
        guild_id = ctx.guild.id
        valid_weapons = ['sword and shield', 'rapier', 'hatchet', 'spear', 'great axe', 'warhammer', 'bow', 'musket', 'fire staff', 'life staff', 'ice gauntlet']
        valid_roles = ['tanks', 'supports', 'dps']
        valid_wars = wars_list(guild_id)
        if war_title.lower() not in valid_wars:
            await ctx.channel.send(f"`There is no war with title '{war_title}' for this guild`")
        elif role.lower() not in valid_roles:
            await ctx.channel.send(f"`'{role}' is not a valid role`")
        elif not isinstance(level, int):
            await ctx.channel.send(f"`'{level}' is not a valid level (must be a number)`")
        elif weapon.lower() not in valid_weapons:
            await ctx.channel.send(f"`'{weapon}' is not a valid weapon`")
        else:
            army = load_army(guild_id, war_title.lower())
            player = Player(name.lower(), level.lower(), role.lower(), weapon.lower(), secundary.lower())
            war_is_full = enlist(guild_id, war_title.lower(), army, player, group, pos)
            if war_is_full:
                await ctx.channel.send(f"`Could not enlist, war is already full or desired group and position are invalid. Enlisting in defined position ('group' and 'pos' parameters for /enlist) will remove old and add new player`")
            else:
                await ctx.channel.send(f"`Enlisted player {player.name} in war '{war_title}'`")
    
def setup(bot):
    bot.add_cog(WarCommands(bot))
