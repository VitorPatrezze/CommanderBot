import discord
from discord import flags
from discord_slash.utils.manage_commands import create_choice, create_option
from entities.army import Army
from entities.player import Player
from entities.war import War
from entities.db import create_war, load_war, load_army, enlist, wars_list
from discord_slash import cog_ext
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext

#Como conseguir tirar esse guild_ids
guild_ids=[879524619218997278]
    
class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def create_embed(war):
        embed = discord.Embed(title=f"{war.title.title()}  -  {war.region.title()}  -  {war.date}\nAtackers: {war.attackers}  -  Defenders: {war.defenders}", color = discord.Color.dark_red())
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
        msg = await ctx.send(f"`Creating new war with title '{title}'`")
        war = War(title.lower(),region.lower(),date,attackers,defenders,army = Army.create_army())
        create_war(ctx.guild.id, war)  #saves war to DB
        embed = Commands.create_embed(war)
        await msg.edit(content="",embed=embed)

    @cog_ext.cog_slash(guild_ids=guild_ids, description="Shows specified war info")
    async def war(self, ctx, war_title):
        msg = await ctx.send(f"`Getting info about war {war_title}`")
        guild_id = ctx.guild.id
        valid_wars = wars_list(guild_id)
        if war_title.lower() not in valid_wars:
            await msg.edit(f"`There is no war with title '{war_title}' for this guild`")
        else:
            war = load_war(guild_id, war_title.lower())
            await msg.edit(content='',embed=Commands.create_embed(war))

    @cog_ext.cog_slash(guild_ids=guild_ids, description="Enlist in an existing war", 
        options=[
            create_option(name = "war_title",
                description="What war you want to enlist",
                required=True,
                option_type=3),
            create_option(name = "name",
                description="Choose your name",
                required=True,
                option_type=3),
            create_option(name = "role",
                description="Choose your role",
                required=True,
                option_type=3,
                choices=[create_choice(name=w.title(),value=w) for w in Player.valid_roles]),
            create_option(name="level",
                description="Choose your level",
                required=True,
                option_type=4),
            create_option(name = "weapon",
                description="Choose your weapon",
                required=True,
                option_type=3,
                choices=[create_choice(name=w.title(),value=w) for w in Player.valid_weapons]),
            create_option(name="group",
                description="Optional: specify a group to enter",
                required=False,
                option_type=4),
            create_option(name="position",
                description="Optional: If you specified a group, you must specify a position in that group",
                required=False,
                option_type=4)
            ])
    async def enlist(self, ctx, war_title, name, role, level, weapon, group=0, position=0 ):
        guild_id = ctx.guild.id
        msg = await ctx.send(f"`Enlisting player {name} in war '{war_title}'`")
        valid_wars = wars_list(guild_id)
        if war_title.lower() not in valid_wars:
            await msg.edit(content=f"`There is no war with title '{war_title}' for this guild`")
        elif int(level) > Player.maximum_level or int(level) < 0 :
            await msg.edit(content=f"`{level} is not a valid level`")
        else:
            army = load_army(guild_id, war_title.lower())
            player = Player(name.lower(), str(level), role.lower(), weapon.lower(),secundary='')
            war_is_full = enlist(guild_id, war_title.lower(), army, player, group, position)
            if war_is_full:
                await msg.edit(content=f"`Could not enlist {name}, war is already full or desired group and position are invalid. Enlisting in defined position ('group' and 'position' parameters for /enlist) will remove old and add new player`")
            else:
                await msg.edit(content=f"`Enlisted player {player.name} in war '{war_title}' !`")
    
    @cog_ext.cog_slash(guild_ids=guild_ids, description="Remove player from war",
        options=[
            create_option(name = "war_title",
                description="What war you want to enlist",
                required=True,
                option_type=3),
            create_option(name="group",
                description="Optional: specify a group to enter",
                required=True,
                option_type=4),
            create_option(name="position",
                description="Optional: If you specified a group, you must specify a position in that group",
                required=True,
                option_type=4)
            ])
    async def remove(self, ctx, war_title, group, position):
        guild_id = ctx.guild.id
        msg = await ctx.send(f"`Removing player in group {group} and position {position} from war {war_title}`")
        valid_wars = wars_list(guild_id)
        if war_title.lower() not in valid_wars:
            await msg.edit(content=f"`There is no war with title '{war_title}' for this guild`")
        else:
            empty_player = Player(name='-',lvl='',role='',primary='',secundary='')
            army = load_army(guild_id, war_title.lower())
            enlist(guild_id, war_title.lower(), army, empty_player, group, position)
            await msg.edit(content=f"`Player in group {group} and position {position} was removed from war {war_title}`")

    @cog_ext.cog_slash(guild_ids=guild_ids,
        options=[
            create_option(name = "weapon",
                description="Choose your weapon",
                required=True,
                option_type=3,
                choices=[create_choice(name=w.title(),value=w) for w in Player.valid_weapons]),
            create_option(name = "role",
                description="Choose your role",
                required=True,
                option_type=3,
                choices=[create_choice(name=w.title(),value=w) for w in Player.valid_roles]),
            create_option(name="lvl",
                description="Choose your level",
                required=True,
                option_type=4)])
    async def teste(self, ctx, weapon):
        msg = await ctx.send(f"`weaponizing {weapon}`")
        await msg.edit(content = f"`Selected weapon {weapon} !`")

def setup(bot):
    bot.add_cog(Commands(bot))
    