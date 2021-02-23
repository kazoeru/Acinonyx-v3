import asyncio
import discord
import random
from   discord.ext import commands
from   Cogs import Settings
from   Cogs import DisplayName
from   Cogs import Nullify
from   Cogs import DL
import urllib

def setup(bot):
    # Add the bot
    settings = bot.get_cog("Settings")
    bot.add_cog(Ascii(bot, settings))
    
class Ascii(commands.Cog):
    
    def __init__(self, bot, settings):
        self.bot = bot
        self.settings = settings
        global Utils, DisplayName
        Utils = self.bot.get_cog("Utils")
        DisplayName = self.bot.get_cog("DisplayName")

    @commands.command(pass_context=True, no_pm=True)
    async def ascii(self, ctx, *, text : str = None):
        """Beautify text
        
        Font list:
        http://artii.herokuapp.com/fonts_list."""
        
        LangCheck = self.settings.getUserStat(ctx.message.author, ctx.message.guild, "Language")

        if LangCheck == None:
            # Author belum memilih bahasa
            await self.language_not_set(ctx)

        if text == None:
            if LangCheck == "ID":
                em = discord.Embed(color = 0XFF8C00,
                                   description = "> **Panduan**\n"
                                                 "> `{}ascii [font (optional)] [text]`\n> \n"
                                                 "> Font list dapat dilihat dibawah ini\n"
                                                 "> http://artii.herokuapp.com/fonts_list"
                                                 .format(ctx.prefix))
                em.set_author(name = "ASCII", url = "http://artii.herokuapp.com/fonts_list", icon_url = "https://cdn.discordapp.com/attachments/518118753226063887/725569194304733435/photo.jpg")
                em.set_footer(text = "Saat mengetik command, tanda [] tidak usah digunakan\n{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                await ctx.channel.send(embed = em)
                return

            if LangCheck == "EN":
                em = discord.Embed(color = 0XFF8C00,
                                   description = ">>> **Usage**\n"
                                                 "`{}ascii [font (optional)] [text]`\n\n"
                                                 "You can see the font list below this\n"
                                                 "http://artii.herokuapp.com/fonts_list"
                                                 .format(ctx.prefix))
                em.set_author(name = "ASCII", url = "http://artii.herokuapp.com/fonts_list", icon_url = "https://cdn.discordapp.com/attachments/518118753226063887/725569194304733435/photo.jpg")
                em.set_footer(text = "When typing commands, you don't need to use the [] sign\n{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                await ctx.channel.send(embed = em)
                return

        # Get list of fonts
        fonturl = "http://artii.herokuapp.com/fonts_list"
        response = await DL.async_text(fonturl)
        fonts = response.split()

        font = None
        # Split text by space - and see if the first word is a font
        parts = text.split()
        if len(parts) > 1:
            # We have enough entries for a font
            if parts[0] in fonts:
                # We got a font!
                font = parts[0]
                text = ' '.join(parts[1:])
    
        url = "http://artii.herokuapp.com/make?{}".format(urllib.parse.urlencode({'text':text}))
        if font:
            url += '&font={}'.format(font)
        response = await DL.async_text(url)
        em = discord.Embed(color = 0XFF8C00, description = "```python\n{}```".format(response))
        em.set_footer(text = "{}".format(ctx.author),
                      icon_url = "{}".format(ctx.author.avatar_url))
        await ctx.channel.send(embed = em)

    async def language_not_set(self, ctx):
        msg  = "<:indonesia:798977282886467635> **INDONESIA**\n"
        msg += "Kamu belum mengatur bahasa untuk bot ini.\n\n"
        msg += "<:English:798978134711599125> **ENGLISH**\n"
        msg += "You haven't set the language for this bot.\n\n"
        msg += "*Pilih dibawah ini / Select it below*"

        em = discord.Embed(color = 0XFF8C00, description = msg)
        em.set_footer(text = "{}".format(ctx.author),
                      icon_url = "{}".format(ctx.author.avatar_url))
        msg = await ctx.send(embed = em, delete_after = 15)
        await msg.add_reaction('<:indonesia:798977282886467635>')
        await msg.add_reaction('<:English:798978134711599125>')

        while True:
            try:
                reaction, user = await self.bot.wait_for(event='reaction_add',)
                if user == ctx.author:
                    emoji = str(reaction.emoji)
                    if emoji == '<:indonesia:798977282886467635>':
                        await msg.delete()

                        member = ctx.author
                        self.settings.setUserStat(member, ctx.guild, "Language", "ID")

                        msg  = "o(>ω<)o Horeeee~!\n"
                        msg += "Kamu telah mengatur bot ini dengan bahasa indonesia.\n"
                        msg += "Silahkan ulangi command yang baru saja kamu gunakan."
                        em = discord.Embed(color = 0XFF8C00, description = msg)
                        em.set_footer(text = "{}".format(ctx.author),
                                      icon_url = "{}".format(ctx.author.avatar_url))
                        await ctx.send(embed = em)

                    if emoji == '<:English:798978134711599125>':
                        await msg.delete()

                        member = ctx.author
                        self.settings.setUserStat(member, ctx.guild, "Language", "EN")

                        msg  = "o(>ω<)o Yaaaaay~!\n"
                        msg += "You have configured this bot in English.\n"
                        msg += "Please repeat the command that you just used."
                        em = discord.Embed(color = 0XFF8C00, description = msg)
                        em.set_footer(text = "{}".format(ctx.author),
                                      icon_url = "{}".format(ctx.author.avatar_url))
                        await ctx.send(embed = em)
            except Exception as e:
                await msg.send("```\n{}\n```".format(e))
