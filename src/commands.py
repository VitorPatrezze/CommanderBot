import discord
from discord.ext.commands.core import has_permissions
from discord_slash.context import ComponentContext, SlashContext
from discord_slash.utils.manage_commands import create_choice, create_option
from discord_slash.utils.manage_components import create_button, create_actionrow
from discord_slash.model import ButtonStyle
from entities.army import Army
from entities.player import Player
from entities.war import War
from entities.db import (
    save_war,
    load_war,
    load_army,
    enlist,
    wars_ids_list,
    add_member,
    load_char,
    init_guild,
    delete_guild,
    all_wars,
    update_war_outcome,
)
from discord_slash import cog_ext
from discord.ext import commands

guild_ids = []
role_name = "New World Leader"


class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        if guild.id not in guild_ids:
            guild_ids.append(guild.id)
            await guild.create_role(name=role_name, color=discord.Color.orange())
            init_guild(guild.id)

    @commands.Cog.listener()
    async def on_guild_leave(self, guild):
        guild_ids.remove(guild.id)
        delete_guild(guild.id)

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            guild_ids.append(guild.id)

    @commands.Cog.listener()
    async def on_component(self, ctx: ComponentContext):
        button, war_number = ctx.custom_id.split(":")
        callbacks = {
            "char_info": Commands.char_info_callback,
            "enlist": Commands.enlist_callback,
            "delist": Commands.delist_callback,
            "refresh": Commands.refresh_callback,
            "help": Commands.help_callback,
        }
        func = callbacks[button]
        if func is None:
            await ctx.reply(
                content="Something went wrong. Please try again.", hidden=True
            )  # if the bot is too slow or doesn't get the button id, it will send this in the channel
        else:
            await func(ctx, war_number)

    def war_buttons(war_number):
        Buttons = [
            create_button(
                style=ButtonStyle.blue,
                label="Character Info",
                custom_id=f"char_info:{war_number}",
            ),
            create_button(
                style=ButtonStyle.green,
                label="Enlist",
                custom_id=f"enlist:{war_number}",
            ),
            create_button(
                style=ButtonStyle.red,
                label="De-list",
                custom_id=f"delist:{war_number}",
            ),
            create_button(
                style=ButtonStyle.grey,
                label="Refresh",
                custom_id=f"refresh:{war_number}",
            ),
            create_button(
                style=ButtonStyle.grey, label="Help", custom_id=f"help:{war_number}"
            ),
        ]
        return [create_actionrow(*Buttons)]

    async def has_role(ctx):
        if role_name in [x.name for x in ctx.author.roles]:
            return True
        else:
            await ctx.reply(
                content=f"`User does not have the necessary role '{role_name}' to run this command.`"
            )
            return False

    async def char_info_callback(ctx: ComponentContext, war_number):
        char = load_char(ctx.guild_id, ctx.author_id)
        if char is not None:
            string = Player.to_string(char)
        else:
            string = "`You don't have a character in this guild. To create or update one, use '/character <name> <role> <weapon> <level>'`"
        await ctx.reply(hidden=True, content=string)

    async def enlist_callback(ctx: ComponentContext, war_number):
        player = load_char(ctx.guild_id, ctx.author_id)
        if player is None:
            await ctx.reply(
                content="`You don't have a character in this guild/server. To create or update one, use '/character <name> <role> <weapon> <level>'`",
                hidden=True,
            )
        else:
            army = load_army(ctx.guild_id, war_number)
            war_is_full, group, position = enlist(ctx.guild_id, war_number, army, player, 0, 0)
            if war_is_full:
                await ctx.reply(
                    content=f"`Could not enlist {player.name}, war is already full or desired group and position are invalid.\n"
                    + "Enlisting in defined position with parameters 'group' and 'position' in /enlist command will remove old and add new player.`",
                    hidden=True,
                )
            else:
                await ctx.edit_origin(
                    content=None,
                    embed=Commands.create_embed(war_number, load_war(ctx.guild_id, war_number)),
                    components=Commands.war_buttons(war_number),
                )
                await ctx.reply(
                    content=f"`Enlisted player {player.name} in war '{war_number}', group {group} and position {position} !`",
                    hidden=True,
                )

    async def delist_callback(ctx: ComponentContext, war_number):
        army = load_army(ctx.guild_id, war_number)
        player = load_char(ctx.guild_id, ctx.author_id)
        if player == None:
            await ctx.reply(
                content="`You don't have a character in this guild. To create or update one, use '/character <name> <role> <weapon> <level>'`",
                hidden=True,
            )
            return
        else:
            for g in range(len(army.comp)):
                for p in range(len(army.comp[g])):
                    if army.comp[g][p].name == player.name:
                        enlist(
                            ctx.guild_id,
                            war_number,
                            army,
                            Player.null_player(),
                            g + 1,
                            p + 1,
                        )
            await ctx.edit_origin(
                    content=None,
                    embed=Commands.create_embed(war_number, load_war(ctx.guild_id, war_number)),
                    components=Commands.war_buttons(war_number),
                )
            await ctx.reply(
                content=f"`All instances of player '{player.name}' were removed from war {war_number}`",
                hidden=True,
            )
            return

    async def refresh_callback(ctx: ComponentContext, war_number):
        war = load_war(ctx.guild_id, war_number)
        await ctx.edit_origin(
            content=None,
            embed=Commands.create_embed(war_number, war),
            components=Commands.war_buttons(war_number),
        )
        await ctx.reply(content="`War panel refreshed`", hidden=True)

    async def help_callback(ctx: ComponentContext, war_number):
        await ctx.reply(
            hidden=True,
            content=f"`If you want to enter the war, you can use this two methods:\n"
            + '   1. Create a character in this guild using command "/character <name> <role> <weapon> <level>" and then enlist using the green button under the war panel.\n'
            + '   2. Use command "/enlist <war_number> <name> <role> <level> <weapon> <group> <position>" where group and position are optional.\n'
            + 'Using the "De-list" button will remove all instances of your character from the war. If another character has the same name, it will be de-listed too.\n'
            + 'The "Character Info" button shows your character in this guild, if you have one.\n'
            + "\n"
            + 'If you want to see a specific war panel, use the command "/war <war_number>".\n'
            + 'To see all the wars created in this guild, use command "/wars_list".\n'
            + "\n"
            + "Commands that only guild leaders can use:\n"
            + '   "/new_war <title> <region> <date> <attackers> <defenders>" : creates new war\n'
            + '   "/remove <war_number> <group> <position>" : removes character from at specified group/position from war\n'
            + '   "/war_outcome <war_number> <outcome>" : updates war outcome with (win or lose), ending it.\n'
            + "`",
        )
        return

    def create_embed(war_number, war):
        embed = discord.Embed(
            title=f"{war_number}. {war.title}  -  {war.region}  -  {war.date}\nAttackers: {war.attackers}  -  Defenders: {war.defenders}",
            color=discord.Color.dark_red(),
        )
        embed.set_thumbnail(
            url="https://pbs.twimg.com/profile_images/1392124727976546307/vBwCWL8W.jpg"
        )
        string = ""
        for i in range(1, len(war.army.comp) + 1):
            string = (
                string
                + f"**Group {i}\n**"
                + "```"
                + " \n".join(
                    f"{n+1}.{p.name}" for n, p in enumerate(war.army.comp[i - 1])
                )
                + "```"
                + "\n"
            )
            if i == len(war.army.comp) / 2:
                embed.add_field(name="\u200b", value=string, inline=True)
                string = ""
        embed.add_field(name="\u200b", value=string, inline=True)
        embed.add_field(name="\u200b", value=Army.armyInfoString(war.army), inline=True)
        if war.outcome != "":
            if war.outcome == "Win":
                string = str("""```yaml\nWin```""")
            else:
                string = str("""```fix\nLose```""")
            embed.add_field(name="\u200b", value=string)
        return embed

    def members_list_embed(members_list):
        embed = discord.Embed(
            title=f"`{len(members_list)}x` Guild members",
            color=discord.Color.dark_blue(),
        )
        string = ""
        e = 1
        for p in members_list:
            string = string + f"**{p.name}** - {p.role.title()}\n"
            if members_list.index(p) == e * 20 - 1:
                embed.add_field(
                    name="\u200b", value="```" + string + "```", inline=True
                )
                string = ""
                e += 1
                if e == 4:
                    break
        if string != "":
            embed.add_field(name="\u200b", value=string, inline=True)
        return embed

    async def show_war_panel(self, ctx: SlashContext, war_number, war):
        embed = Commands.create_embed(war_number, war)
        panel = await ctx.reply(
            content=None, embed=embed, components=Commands.war_buttons(war_number)
        )

    @cog_ext.cog_slash(
        guild_ids=guild_ids,
        description="Create a new event (war, invasion, PvP Quests, etc)",
    )  # only guild leaders can use
    async def new_war(
        self, ctx: SlashContext, title, region, date, attackers, defenders
    ):
        await ctx.defer()
        if await Commands.has_role(ctx):
            war = War(
                title,
                region,
                date,
                attackers,
                defenders,
                army=Army.create_army(),
                outcome="",
            )
            war_number = save_war(ctx.guild.id, war)  # saves war to DB
            await Commands.show_war_panel(self, ctx, war_number, war)
            return

    @cog_ext.cog_slash(
        guild_ids=guild_ids,
        description="Shows list of wars that don't have an outcome yet",
    )
    async def wars_list(self, ctx):
        guild_id = ctx.guild.id
        unfinished_wars, finished_wars = all_wars(guild_id)
        embed = discord.Embed(title="Wars list", color=discord.Color.dark_blue())
        embed.set_thumbnail(
            url="https://pbs.twimg.com/profile_images/1392124727976546307/vBwCWL8W.jpg"
        )

        string = ""
        for war in sorted(unfinished_wars, key=lambda x: int(x["id"])):
            string += f"{war['id']}. {war['title']} - {war['region']} - {war['date']}\n"
        if string == "":
            string = "No matching wars"
        embed.add_field(name="Upcoming Wars", value=string, inline=False)

        string = ""
        for war in sorted(finished_wars, key=lambda x: int(x["id"])):
            string += f"{war['id']}. {war['title']} - {war['region']} - {war['date']} - {war['outcome']}\n"
        if string == "":
            string = "No matching wars"
        embed.add_field(name="Finished Wars", value=string, inline=False)

        await ctx.send(content="", embed=embed)

    @cog_ext.cog_slash(guild_ids=guild_ids, description="Shows specified war info")
    async def war(self, ctx, war_number):
        await ctx.defer()
        guild_id = ctx.guild.id
        valid_wars = wars_ids_list(guild_id)
        if war_number not in valid_wars:
            await ctx.reply(
                content=f"`There is no war with number '{war_number}' for this guild`",
                hidden=True,
            )
        else:
            war = load_war(guild_id, war_number)
            await Commands.show_war_panel(self, ctx, war_number, war)

    @cog_ext.cog_slash(
        guild_ids=guild_ids,
        description="Enter the outcome of specified war to mark it as 'ended'",  # only guild leaders can use
        options=[
            create_option(
                name="war_number",
                description="What war you want to change the outcome",
                required=True,
                option_type=4,
            ),
            create_option(
                name="outcome",
                description="Choose the war's outcome",
                required=True,
                option_type=3,
                choices=[
                    create_choice(name="Win", value="Win"),
                    create_choice(name="Lose", value="Lose"),
                    create_choice(name="To be defined", value=""),
                ],
            ),
        ],
    )
    async def war_outcome(self, ctx, war_number, outcome):
        await ctx.defer(hidden=True)
        if await Commands.has_role(ctx):
            guild_id = ctx.guild.id
            valid_wars = wars_ids_list(guild_id)
            if str(war_number) not in valid_wars:
                await ctx.reply(
                    content=f"`There is no war with number '{war_number}' for this guild`",
                    hidden=True,
                )
            else:
                update_war_outcome(guild_id, war_number, outcome)
                await ctx.reply(
                    content=f"`Updated war {war_number} outcome to '{outcome}'!`",
                    hidden=True,
                )

    @cog_ext.cog_slash(
        guild_ids=guild_ids,
        description="Update your character in this guild/server",
        options=[
            create_option(
                name="name",
                description="Choose your name",
                required=True,
                option_type=3,
            ),
            create_option(
                name="role",
                description="Choose your role",
                required=True,
                option_type=3,
                choices=[
                    create_choice(name=w.title(), value=w) for w in Player.valid_roles
                ],
            ),
            create_option(
                name="level",
                description=f"Level between 0 and {Player.maximum_level}",
                required=True,
                option_type=4,
            ),
            create_option(
                name="weapon",
                description="Choose your weapon",
                required=True,
                option_type=3,
                choices=[
                    create_choice(name=w.title(), value=w) for w in Player.valid_weapons
                ],
            ),
        ],
    )
    async def character(self, ctx, name, role, weapon, level):
        await ctx.defer(hidden=True)
        guild_id = ctx.guild.id
        if int(level) > Player.maximum_level or int(level) < 0:
            await ctx.reply(content=f"`{level} is not a valid level`", hidden=True)
        else:
            add_member(guild_id, ctx.author.id, Player(name, level, role, weapon))
            await ctx.reply(
                content=f"`'{name}' is now {ctx.author.nick if ctx.author.nick is not None else ctx.author.name}'s character`",
                hidden=True,
            )

    @cog_ext.cog_slash(
        guild_ids=guild_ids,
        description="Enlist in an existing war",
        options=[
            create_option(
                name="war_number",
                description="What war you want to enlist",
                required=True,
                option_type=4,
            ),
            create_option(
                name="name",
                description="Choose your name",
                required=True,
                option_type=3,
            ),
            create_option(
                name="role",
                description="Choose your role",
                required=True,
                option_type=3,
                choices=[
                    create_choice(name=w.title(), value=w) for w in Player.valid_roles
                ],
            ),
            create_option(
                name="level",
                description="Choose your level",
                required=True,
                option_type=4,
            ),
            create_option(
                name="weapon",
                description="Choose your weapon",
                required=True,
                option_type=3,
                choices=[
                    create_choice(name=w.title(), value=w) for w in Player.valid_weapons
                ],
            ),
            create_option(
                name="group",
                description="Optional: specify a group to enter",
                required=False,
                option_type=4,
            ),
            create_option(
                name="position",
                description="Optional: If you specified a group, you must specify a position in that group",
                required=False,
                option_type=4,
            ),
        ],
    )
    async def enlist(
        self,
        ctx: SlashContext,
        war_number,
        name,
        role,
        level,
        weapon,
        group=0,
        position=0,
    ):
        await ctx.defer(hidden=True)
        guild_id = ctx.guild.id
        valid_wars = wars_ids_list(guild_id)
        if str(war_number) not in valid_wars:
            await ctx.reply(
                content=f"`There is no war with number '{war_number}' for this guild`",
                hidden=True,
            )
        elif int(level) > Player.maximum_level or int(level) < 0:
            await ctx.reply(content=f"`{level} is not a valid level`", hidden=True)
        else:
            army = load_army(guild_id, war_number)
            player = Player(name, str(level), role.lower(), weapon.lower())
            war_is_full, _ = enlist(guild_id, war_number, army, player, group, position)
            if war_is_full:
                await ctx.reply(
                    content=f"`Could not enlist {name}, war is already full or desired group and position are invalid. Enlisting in defined position ('group' and 'position' parameters for /enlist) will remove old and add new player`",
                    hidden=True,
                )
            else:
                await ctx.reply(
                    content=f"`Enlisted player {player.name} in war '{war_number}' !`",
                    hidden=True,
                )

    @cog_ext.cog_slash(
        guild_ids=guild_ids,
        description="Remove player from war",  # only guild leaders can use
        options=[
            create_option(
                name="war_number",
                description="What war you want to enlist",
                required=True,
                option_type=4,
            ),
            create_option(
                name="group",
                description="Optional: specify a group to enter",
                required=True,
                option_type=4,
            ),
            create_option(
                name="position",
                description="Optional: If you specified a group, you must specify a position in that group",
                required=True,
                option_type=4,
            ),
        ],
    )
    async def remove(self, ctx, war_number, group, position):
        await ctx.defer(hidden=True)
        if await Commands.has_role(ctx):
            guild_id = ctx.guild.id
            valid_wars = wars_ids_list(guild_id)
            if str(war_number) not in valid_wars:
                await ctx.reply(
                    content=f"`There is no war with number '{war_number}' for this guild`",
                    hidden=True,
                )
            else:
                army = load_army(guild_id, war_number)
                enlist(
                    guild_id, war_number, army, Player.null_player(), group, position
                )
                await ctx.reply(
                    content=f"`Player in group {group} and position {position} was removed from war {war_number}`",
                    hidden=True,
                )


def setup(bot):
    bot.add_cog(Commands(bot))
