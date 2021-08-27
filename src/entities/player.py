from discord_slash import cog_ext
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext

class Player:
    def __init__(self,name,lvl,role,primary,secundary):
        self.name = name
        self.lvl = lvl
        self.role = role
        self.primary = primary
        self.secundary = secundary
    