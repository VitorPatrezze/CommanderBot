import discord
import datetime
from discord import flags
from discord_slash.utils.manage_commands import create_choice, create_option
from entities.army import Army
from entities.player import Player
from entities.war import War
from entities.db import save_war, load_war, load_army, enlist, wars_list, add_member, load_char
from discord_slash import cog_ext
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from discord_components import DiscordComponents, Button, ButtonStyle, InteractionEventType

#Como conseguir tirar esse guild_ids
guild_ids=[879524619218997278]
    
class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    war_buttons = [[
        Button(style = ButtonStyle.blue, label = 'Character Info', id="char_info"),
        Button(style = ButtonStyle.green, label = 'Enlist', id = "enlist"),
        Button(style = ButtonStyle.red, label = 'De-list', id = "delist"),
        Button(style = ButtonStyle.grey, label = 'Refresh', id = "refresh"),
        Button(style = ButtonStyle.grey, label = 'Help', id = "help")]]

    async def char_info_callback(guild_id, event, panel, war_number):
        char = load_char(guild_id, event.author.id)
        if char != None:
            string = Player.to_string(char)
        else:
            string = "`You don't have a character in this guild. To create or update one, use '/character <name> <role> <weapon> <level>'`"
        await event.respond(type = 4, content = string)
        return

    async def enlist_callback(guild_id, event, panel, war_number):
        army = load_army(guild_id, war_number)
        player = load_char(guild_id, event.author.id)
        if player == None:
            await event.respond(content = "`You don't have a character in this guild. To create or update one, use '/character <name> <role> <weapon> <level>'`")
            return
        else:
            war_is_full = enlist(guild_id, war_number, army, player, 0, 0)
            if war_is_full:
                await event.respond(content=f"`Could not enlist {player.name}, war is already full or desired group and position are invalid. Enlisting in defined position ('group' and 'position' parameters for /enlist) will remove old and add new player`")
            else:
                await event.respond(content=f"`Enlisted player {player.name} in war '{war_number}' !`")
            return
    
    async def delist_callback(guild_id, event, msg, war_number):  
        army = load_army(guild_id, war_number)
        player = load_char(guild_id, event.author.id)
        if player == None:
            await event.respond(content = "`You don't have a character in this guild. To create or update one, use '/character <name> <role> <weapon> <level>'`")
            return
        else:
            for g in range(len(army.comp)):
                for p in range(len(army.comp[g])):
                    if army.comp[g][p].name == player.name:
                        enlist(guild_id, war_number, army, Player.null_player(), g + 1 , p + 1)
            await event.respond(content=f"`All instances of player '{player.name}' were removed from war {war_number}`")
            return

    async def refresh_callback(guild_id, event, panel, war_number):
        war = load_war(guild_id, war_number)
        await panel.edit(
            embed = Commands.create_embed(war_number, war),
            components = Commands.war_buttons
        )
        await event.respond(content = "`War panel refreshed`")
        return
    
    async def help_callback(guild_id, event, msg, war_number):
        await event.respond(
            type = 4,   
            content = f"`If you want to enter the war, you can use this two methods:\n" + 
            '   1. Create a character in this guild using command "/character <name> <role> <weapon> <level>" and then enlist using the green button under the war panel.\n'+
            '   2. Use command "/enlist <war_number> <name> <role> <level> <weapon> <group> <position>" where group and position are optional.\n'+
            'Using the "De-list" button will remove all instances of your character from the war. If another character has the same name, it will be de-listed too.\n'+
            'If you want to see a specific war panel, use the command "/war <war_number>".`'
        )
        return

    def create_embed(war_number, war):
        embed = discord.Embed(title=f"{war_number}. {war.title}  -  {war.region}  -  {war.date}\nAttackers: {war.attackers}  -  Defenders: {war.defenders}", color = discord.Color.dark_red())
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

    def members_list_embed(members_list):
        embed = discord.Embed(title=f"`{len(members_list)}x` Guild members", color = discord.Color.dark_blue())
        string = ''
        e = 1
        for p in members_list:
            string = string + f"**{p.name}** - {p.role.title()}\n"
            if members_list.index(p) == e*20 - 1:
                embed.add_field(name="\u200b", value="```" + string + "```", inline=True)
                string = ''
                e += 1
                if e == 4 :
                    break
        if string != '':
            embed.add_field(name="\u200b", value=string, inline=True)
        return embed

    @cog_ext.cog_slash(guild_ids=guild_ids, description="Create a new event (war, invasion, PvP Quests, etc)") #only guild leaders can use
    async def new_war(self, ctx, title, region, date, attackers, defenders):
        msg = await ctx.send(f"`Creating new war with title '{title}'`")
        war = War(title,region,date,attackers,defenders,army = Army.create_army())
        war_number = save_war(ctx.guild.id, war)  #saves war to DB
        embed = Commands.create_embed(war_number, war)
        await msg.edit(content="",embed=embed)

    @cog_ext.cog_slash(guild_ids=guild_ids, description="Update your character in this guild", #only guild members can use
        options=[
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
                description=f"Level between 0 and {Player.maximum_level}",
                required=True,
                option_type=4),
            create_option(name = "weapon",
                description="Choose your weapon",
                required=True,
                option_type=3,
                choices=[create_choice(name=w.title(),value=w) for w in Player.valid_weapons])
        ]) 
    async def character(self, ctx, name, role, weapon, level):
        guild_id = ctx.guild.id
        msg = await ctx.send(f"`Updating '{name}' as character for {ctx.author.name}`")
        if int(level) > Player.maximum_level or int(level) < 0 :
            await msg.edit(content=f"`{level} is not a valid level`")
        else:
            add_member(guild_id, ctx.author.id, Player(name, level, role, weapon))
            await msg.edit(content=f"`'{name}' is now {ctx.author.name}'s character`")       

    @cog_ext.cog_slash(guild_ids=guild_ids, description="Shows specified war info")
    async def war(self, ctx, war_number):
        msg = await ctx.channel.send(f"`Getting info about war {war_number}`")
        guild_id = ctx.guild.id
        valid_wars = wars_list(guild_id)
        if war_number not in valid_wars:
            await msg.edit(f"`There is no war with number '{war_number}' for this guild`")
        else:
            war = load_war(guild_id, war_number)
            embed = Commands.create_embed(war_number, war)
            panel = await ctx.channel.send(content='', embed=embed, components = Commands.war_buttons)
            await msg.delete()
            while True:
                event = await self.bot.wait_for("button_click")
                if event.channel is not ctx.channel:   #discord bots doesn't care which guild is using buttons. We do this confirmation to avoid confusion.
                    return 
                if event.channel == ctx.channel:
                    callbacks = {
                            "char_info" : Commands.char_info_callback,
                            "enlist" : Commands.enlist_callback,
                            "delist" : Commands.delist_callback,
                            "refresh" : Commands.refresh_callback,
                            "help" : Commands.help_callback
                        }
                    func = callbacks[event.component.id]
                    if func is None:
                        await event.channel.respond(type = 4, content = "Something went wrong. Please try again.")  #if the bot is too slow or doesn't get the button id, it will send this in the channel
                    else: 
                        await func(guild_id, event, panel, war_number)

    @cog_ext.cog_slash(guild_ids=guild_ids, description="Enlist in an existing war", 
        options=[
            create_option(name = "war_number",
                description="What war you want to enlist",
                required=True,
                option_type=4),
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
    async def enlist(self, ctx, war_number, name, role, level, weapon, group=0, position=0 ):
        guild_id = ctx.guild.id
        msg = await ctx.send(f"`Enlisting player {name} in war '{war_number}'`")
        valid_wars = wars_list(guild_id)
        if str(war_number) not in valid_wars:
            await msg.edit(content=f"`There is no war with number '{war_number}' for this guild`")
        elif int(level) > Player.maximum_level or int(level) < 0 :
            await msg.edit(content=f"`{level} is not a valid level`")
        else:
            army = load_army(guild_id, war_number)
            player = Player(name, str(level), role.lower(), weapon.lower())
            war_is_full = enlist(guild_id, war_number, army, player, group, position)
            if war_is_full:
                await msg.edit(content=f"`Could not enlist {name}, war is already full or desired group and position are invalid. Enlisting in defined position ('group' and 'position' parameters for /enlist) will remove old and add new player`")
            else:
                await msg.edit(content=f"`Enlisted player {player.name} in war '{war_number}' !`")
    
    @cog_ext.cog_slash(guild_ids=guild_ids, description="Remove player from war", #only guild leaders can use
        options=[
            create_option(name = "war_number",
                description="What war you want to enlist",
                required=True,
                option_type=4),
            create_option(name="group",
                description="Optional: specify a group to enter",
                required=True,
                option_type=4),
            create_option(name="position",
                description="Optional: If you specified a group, you must specify a position in that group",
                required=True,
                option_type=4)
            ])
    async def remove(self, ctx, war_number, group, position):
        guild_id = ctx.guild.id
        msg = await ctx.send(f"`Removing player in group {group} and position {position} from war {war_number}`")
        valid_wars = wars_list(guild_id)
        if str(war_number) not in valid_wars:
            await msg.edit(content=f"`There is no war with number '{war_number}' for this guild`")
        else:
            army = load_army(guild_id, war_number)
            enlist(guild_id, war_number, army, Player.null_player(), group, position)
            await msg.edit(content=f"`Player in group {group} and position {position} was removed from war {war_number}`")

def setup(bot):
    bot.add_cog(Commands(bot))
    