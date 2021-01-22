import discord
from discord.ext import commands
from Cogs        import Utils
from Cogs        import Settings



def setup(bot):
    settings = bot.get_cog("Settings")
    bot.add_cog(DotaBase(bot, settings))

class DotaBase(commands.Cog):

    def __init__(self, bot, settings):
        self.bot = bot
        self.settings = settings
        global Utils, DisplayName
        Utils = self.bot.get_cog("Utils")
        DisplayName = self.bot.get_cog("DisplayName")

    @commands.command()
    async def hero(self, ctx, *, hero = None):
        """Mencari informasi seputar hero DOTA 2.
        Kamu dapat menggunakan command ini dengan option:
        • Nama hero
        • Hero ID

        **Contoh**
        • acx hero sf
        • acx hero inker
        • acx hero furi"""
        print("Command hero dialihkan ke MangoByte")
        
    @commands.command()
    async def item(self, ctx, *, item = None):
        """Mencari informasi seputar item DOTA 2
        
        **Contoh:**
        • acx item shadow blade
        • acx item tango"""
        print("Command item dialihkan ke MangoByte")
        
    @commands.command()
    async def ability(self, ctx, ability = None):
        """Mencari informasi seputar ability hero DOTA 2
        
        **Contoh:**
        • acx ability rocket flare
        • acx ability laser
        • acx ability sprout"""
        print("Command ability dialihkan ke MangoByte")

    @commands.command()
    async def talents(self, ctx, *, hero = None):
        """Mencari informasi talent dari hero DOTA 2.
        Kamu dapat menggunakan command ini dengan option:
        • Nama hero
        • Hero ID

        **Contoh:**
        `acx talents shadow fiend`"""
        print("Command talent dialihkan ke MangoByte")

    @commands.command()
    async def lore(self, ctx, *, name=None):
        """Mencari lore/knowledge (pengetahuan) dari hero, ability, item dalam game DOTA 2
        Jika tidak memasukan [name] aku akan memberikan secara random

        **Contoh:**
        • acx lore bristleback
        • acx lore shadow blade
        • acx lore venomous gale"""
        print("Command lore dialihkan ke MangoByte")