import asyncio
import discord
import string
import random
from   urllib.parse import quote
from   discord.ext import commands
from   Cogs import Settings, PickList
from   Cogs import Message
from   Cogs import Nullify
from   Cogs import DL

def setup(bot):
    # Add the bot and deps
    settings = bot.get_cog("Settings")
    bot.add_cog(UrbanDict(bot, settings))

# This module grabs Urban Dictionary definitions

class UrbanDict(commands.Cog):

    # Init with the bot reference, and a reference to the settings var and xp var
    def __init__(self, bot, settings):
        self.bot = bot
        self.settings = settings
        self.ua = 'CorpNewt DeepThoughtBot'
        self.random = True

    @commands.command(pass_context=True)
    @commands.is_nsfw()
    async def define(self, ctx, *, word : str = None):
        """Memberikan definisi kata yang kamu cari."""

        # Check if we're suppressing @here and @everyone mentions
        if self.settings.getServerStat(ctx.message.guild, "SuppressMentions"):
            suppress = True
        else:
            suppress = False

        if not word:
            em = discord.Embed(color = 0XFF8C00, description = "> Memberikan definisi kata yang kamu cari\n> \n"
                                                               "> **Panduan**\n"
                                                               "> `{}leaveserver [nama/id server]`"
                                                               .format(ctx.prefix))
            em.set_author(name = "Define command", icon_url = "https://cdn.discordapp.com/attachments/518118753226063887/725569194304733435/photo.jpg")
            em.set_thumbnail(url = "{}".format(ctx.message.guild.icon_url))
            em.set_footer(text = "Saat mengetik command, tanda [] tidak usah digunakan\nRequest by : {}".format(ctx.author.name), icon_url = "{}".format(ctx.author.avatar_url))
            await ctx.channel.send(msg)
            return
        url = "http://api.urbandictionary.com/v0/define?term={}".format(quote(word))
        msg = 'I couldn\'t find a definition for "{}"...'.format(word)
        title = permalink = None
        theJSON = await DL.async_json(url, headers = {'User-agent': self.ua})
        theJSON = theJSON["list"]
        if len(theJSON):
            # Got it - let's build our response
            words = []
            for x in theJSON:
                value = x["definition"]
                if x["example"]:
                    ex = x["example"].replace("*","")
                    lines = ["*{}*".format(y.strip()) if len(y.strip()) else "" for y in ex.split("\n")]
                    value += "\n\n__Example(s):__\n\n{}".format("\n".join(lines))
                words.append({
                    "name":"{} - by {} ({} 👍 / {} 👎)".format(string.capwords(x["word"]),x["author"],x["thumbs_up"],x["thumbs_down"]),
                    "value":value
                })
            return await PickList.PagePicker(title="Results For: {}".format(string.capwords(word)),list=words,ctx=ctx,max=1,url=theJSON[0]["permalink"]).pick()
        await ctx.send(Nullify.clean(msg))

    @commands.command(pass_context=True)
    async def randefine(self, ctx):
        """Gives a random word and its definition."""

        # Check if we're suppressing @here and @everyone mentions
        if self.settings.getServerStat(ctx.message.guild, "SuppressMentions"):
            suppress = True
        else:
            suppress = False

        url = "http://api.urbandictionary.com/v0/random"
        title = permalink = None
        theJSON = await DL.async_json(url, headers = {'User-agent': self.ua})
        theJSON = theJSON["list"]
        if len(theJSON):
            # Got it - let's build our response
            x = random.choice(theJSON)
            value = x["definition"]
            if x["example"]:
                ex = x["example"].replace("*","")
                lines = ["*{}*".format(y.strip()) if len(y.strip()) else "" for y in ex.split("\n")]
                value += "\n\n__Example(s):__\n\n{}".format("\n".join(lines))
            words = [{
                "name":"{} - by {} ({} 👍 / {} 👎)".format(string.capwords(x["word"]),x["author"],x["thumbs_up"],x["thumbs_down"]),
                "value":value
            }]
            return await PickList.PagePicker(title="Results For: {}".format(string.capwords(x["word"])),list=words,ctx=ctx,max=1,url=x["permalink"]).pick()
        await ctx.send(Nullify.clean(msg))
