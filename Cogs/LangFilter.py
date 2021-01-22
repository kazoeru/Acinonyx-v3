import asyncio, discord, re, random, os
from   datetime import datetime
from   discord.ext import commands
from   Cogs import Utils, DisplayName, Message

def setup(bot):
    # Add the bot and deps
    settings = bot.get_cog("Settings")
    bot.add_cog(LangFilter(bot, settings))

class ProfanitiesFilter(object):
    def __init__(self, filterlist, ignore_case=True, replacements="$@%-?!", 
                complete=True, inside_words=False):
        """
        Inits the profanity filter.

        filterlist -- a list of regular expressions that
        matches words that are forbidden
        ignore_case -- ignore capitalization
        replacements -- string with characters to replace the forbidden word
        complete -- completely remove the word or keep the first and last char?
        inside_words -- search inside other words?
        
        Code from here https://stackoverflow.com/a/3533322
        
        Credit to leoluk

        """

        self.badwords = filterlist
        self.ignore_case = ignore_case
        self.replacements = replacements
        self.complete = complete
        self.inside_words = inside_words

    def _make_clean_word(self, length):
        """
        Generates a random replacement string of a given length
        using the chars in self.replacements.

        """
        return ''.join([random.choice(self.replacements) for i in
                range(length)])

    def __replacer(self, match):
        value = match.group()
        if self.complete:
            return self._make_clean_word(len(value))
        else:
            return value[0]+self._make_clean_word(len(value)-2)+value[-1]

    def clean(self, text):
        """Cleans a string from profanity."""

        regexp_insidewords = {
            True: r'(%s)',
            False: r'\b(%s)\b',
            }

        regexp = (regexp_insidewords[self.inside_words] % 
                '|'.join(self.badwords))

        r = re.compile(regexp, re.IGNORECASE if self.ignore_case else 0)

        return r.sub(self.__replacer, text)


'''if __name__ == '__main__':

    f = ProfanitiesFilter(['bad', 'un\w+'], replacements="-")    
    example = "I am doing bad ungood badlike things."

    print f.clean(example)
    # Returns "I am doing --- ------ badlike things."

    f.inside_words = True    
    print f.clean(example)
    # Returns "I am doing --- ------ ---like things."

    f.complete = False    
    print f.clean(example)
    # Returns "I am doing b-d u----d b-dlike things."'''
    
class LangFilter(commands.Cog):

    # Init with the bot reference, and a reference to the settings var
    def __init__(self, bot, settings, replacements = "@#$%&"):
        self.bot = bot
        self.settings = settings
        self.replacements = replacements
        global Utils, DisplayName
        Utils = self.bot.get_cog("Utils")
        DisplayName = self.bot.get_cog("DisplayName")
        
        
    async def test_message(self, message):
        # Implemented to bypass having message called twice
        return { "Ignore" : False, "Delete" : False }

    async def message_edit(self, before, message):
        return await self.message(message)

    async def message(self, message):
        # Check the message and see if we should allow it - always yes.
        word_list = self.settings.getServerStat(message.guild, "FilteredWords")
        if not len(word_list):
            # No filter
            return { "Ignore" : False, "Delete" : False }
    
        # Check for admin/bot-admin
        ctx = await self.bot.get_context(message)
        if Utils.is_bot_admin(ctx):
            return { "Ignore" : False, "Delete" : False }
        
        f = ProfanitiesFilter(word_list, replacements=self.replacements)
        f.ignore_case = True
        f.inside_words = True
        
        new_msg = f.clean(message.content)
        if not new_msg == message.content:
            # Something changed
            new_msg = "Halo *{}*\nBerdasarkan perhitungan ku, ini adalah versi terbaru dari pesan tersebut:\n".format(DisplayName.name(message.author)) + new_msg
            em = discord.Embed(color = 0XFF8C00, description = new_msg)
            em.set_footer(text = "{}#{}".format(ctx.author.name, ctx.author.discriminator),
                          icon_url = "{}".format(ctx.author.avatar_url))
            await message.channel.send(new_msg)
            return { "Ignore" : False, "Delete" : True }
        return { "Ignore" : False, "Delete" : False }
        
    
    @commands.command(pass_context=True)
    async def addfilter(self, ctx, *, words = None):
        """Filter chat, menambahkan kata-kata yang bersifat offensive/tidak layak(admin-server only).

        Gunakan tanda koma (,) untuk memisahkan kata1 dan kata2.
        Contoh:
        acx!addfilter kata1, kata2, kata3, dst"""
        if not await Utils.is_admin_reply(ctx): return
            
        if words == None:
            em = discord.Embed(color = 0XFF8C00, description = "> Chat filer, menambahkan kata-kata yang bersifat offensive/tidak layak(admin-server only)\n"
                                                               "> Gunakan tanda koma (,) untuk memisahkan kata1 dan kata2\n> \n"
                                                               "> **Panduan**\n"
                                                               "> `{}addfilter kata1, kata2, dst`\n> \n"
                                                               "> Untuk melihat list filter chat ketik `{}listfilter`.\n"
                                                               "> Untuk menghapus silahkan cek `{}help remfilter`"
                                                               .format(ctx.prefix,
                                                                       ctx.prefix,
                                                                       ctx.prefix))
            em.set_author(name = "Add filter chat", icon_url = "https://cdn.discordapp.com/attachments/518118753226063887/725569194304733435/photo.jpg")
            em.set_footer(text = "Request by : {}".format(ctx.author.name), icon_url = "{}".format(ctx.author.avatar_url))                
            return await ctx.send(embed=em)
            
        serverOptions = self.settings.getServerStat(ctx.guild, "FilteredWords")
        words = "".join(words.split())
        optionList = words.split(',')
        addedOptions = []
        for option in optionList:
            option = option.replace("(", "\(").replace(")", "\)")
            if not option.lower() in serverOptions:
                # Only add if not already added
                addedOptions.append(option.lower())
        if not len(addedOptions):
            msg = 'Tidak ada kata baru yang ditambahkan.'
            em = discord.Embed(color = 0XFF8C00, description = msg)
            em.set_footer(text = "{}#{}".format(ctx.author.name, ctx.author.discriminator),
                          icon_url = "{}".format(ctx.author.avatar_url))
            return await ctx.send(embed = em)
        
        for option in addedOptions:
            serverOptions.append(option)

        self.settings.setServerStat(ctx.guild, "FilteredWords", serverOptions)
            
        if len(addedOptions) == 1:
            msg = '*1* kata telah ditambahkan kedalam chat filter list.'
            em = discord.Embed(color = 0XFF8C00, description = msg)
            em.set_footer(text = "{}#{}".format(ctx.author.name, ctx.author.discriminator),
                          icon_url = "{}".format(ctx.author.avatar_url))
            await ctx.send(embed = em)
        else:
            msg = '*{}* kata telah ditambahkan kedalam chat filter list.'.format(len(addedOptions))
            em = discord.Embed(color = 0XFF8C00, description = msg)
            em.set_footer(text = "{}#{}".format(ctx.author.name, ctx.author.discriminator),
                          icon_url = "{}".format(ctx.author.avatar_url))
            await ctx.send(embed = em)
            
            
    @commands.command(pass_context=True)
    async def remfilter(self, ctx, *, words = None):
        """Menghapus kata yang telah terdaftar dalam filter chat (admin-server only).
        Gunakan tanda koma (,) untuk memisahkan kata1 dan kata2
        Contoh:
        acx!remfilter kata1, kata2, dst"""
        if not await Utils.is_admin_reply(ctx): return
            
        if words == None:
            em = discord.Embed(color = 0XFF8C00, description = "> Menghapus kata yang telah terdaftar dalam filter chat (admin-server only)\n"
                                                               "> Gunakan tanda koma (,) untuk memisahkan kata1 dan kata2\n> \n"
                                                               "> **Panduan**\n"
                                                               "> `{}remfilter kata1, kata2, dst`\n> \n"
                                                               "> Untuk melihat list filter chat ketik `{}listfilter`.\n"
                                                               "> Untuk menambahkan silahkan cek `{}help addfilter`"
                                                               .format(ctx.prefix,
                                                                       ctx.prefix,
                                                                       ctx.prefix))
            em.set_author(name = "Add filter chat", icon_url = "https://cdn.discordapp.com/attachments/518118753226063887/725569194304733435/photo.jpg")
            em.set_footer(text = "Request by : {}".format(ctx.author.name), icon_url = "{}".format(ctx.author.avatar_url))                
            return await ctx.send(embed=em)
            
        serverOptions = self.settings.getServerStat(ctx.guild, "FilteredWords")
        words = "".join(words.split())
        optionList = words.split(',')
        addedOptions = []
        for option in optionList:
            # Clear any instances of \( to (
            # Reset them to \(
            # This should allow either \( or ( to work correctly -
            # While still allowing \\( or whatever as well
            option = option.replace("\(", "(").replace("\)", ")")
            option = option.replace("(", "\(").replace(")", "\)")
            if option.lower() in serverOptions:
                # Only add if not already added
                addedOptions.append(option.lower())
        if not len(addedOptions):
            msg = 'Aku tidak menemukan kata itu dalam list.'
            em = discord.Embed(color = 0XFF8C00, description = msg)
            em.set_footer(text = "{}#{}".format(ctx.author.name, ctx.author.discriminator),
                          icon_url = "{}".format(ctx.author.avatar_url))
            return await ctx.send(embed = em)
        
        for option in addedOptions:
            serverOptions.remove(option)

        self.settings.setServerStat(ctx.guild, "FilteredWords", serverOptions)
            
        if len(addedOptions) == 1:
            msg = '*1* kata telah di hapus dari filter chat.'
            em = discord.Embed(color = 0XFF8C00, description = msg)
            em.set_footer(text = "{}#{}".format(ctx.author.name, ctx.author.discriminator),
                          icon_url = "{}".format(ctx.author.avatar_url))
            await ctx.send(embed = em)
        else:
            msg = '*{}* kata telah di hapus dari filter chat.'.format(len(addedOptions))
            em = discord.Embed(color = 0XFF8C00, description = msg)
            em.set_footer(text = "{}#{}".format(ctx.author.name, ctx.author.discriminator),
                          icon_url = "{}".format(ctx.author.avatar_url))
            await ctx.send(embed = em)
        
        
    @commands.command(pass_context=True)
    async def listfilter(self, ctx):
        """Menampilkan list filter chat (admin-server only)."""
        if not await Utils.is_admin_reply(ctx): return
            
        serverOptions = self.settings.getServerStat(ctx.guild, "FilteredWords")
        
        if not len(serverOptions):
            return await ctx.send("Filter chat kosong!")
        
        string_list = ", ".join(serverOptions)
        
        msg = "__**Chat filter list:**__\n" + string_list
        
        await Message.Message(message=msg).send(ctx)
        
    @commands.command(pass_context=True)
    async def clearfilter(self, ctx):
        """Menghapus semua filter chat yang terdaftar dalam list (admin-server only)."""
        if not await Utils.is_admin_reply(ctx): return
            
        serverOptions = self.settings.getServerStat(ctx.guild, "FilteredWords")
        self.settings.setServerStat(ctx.guild, "FilteredWords", [])
        
        if len(serverOptions) == 1:
            msg = '*1* kata telah di hapus dari filter chat.'
            em = discord.Embed(color = 0XFF8C00, description = msg)
            em.set_footer(text = "{}#{}".format(ctx.author.name, ctx.author.discriminator),
                          icon_url = "{}".format(ctx.author.avatar_url))
            await ctx.send(embed = em)
        else:
            msg = '*{}* kata telah di hapus dari filter chat.'.format(len(serverOptions))
            em = discord.Embed(color = 0XFF8C00, description = msg)
            em.set_footer(text = "{}#{}".format(ctx.author.name, ctx.author.discriminator),
                          icon_url = "{}".format(ctx.author.avatar_url))
            await ctx.send(embed = em)
            
    @commands.command(pass_context=True)
    async def dumpfilter(self, ctx):
        """Menyimpan backup filter chat dalam format .txt dan upload ke pengirim (bot-admin only)."""
        if not await Utils.is_bot_admin_reply(ctx): return
        
        serverOptions = self.settings.getServerStat(ctx.guild, "FilteredWords")
        
        if not len(serverOptions):
            msg = "┐(￣ヘ￣;)┌\nServer *{}*  tidak memiliki Filter chat yang telah disetting\n".format(ctx.guild.name)
            msg += "Kamu dapat menambahkan filter chat dengan cara\n"
            msg += "`{}addfilter`".format(ctx.prefix)
            em = discord.Embed(color = 0XFF8C00, description = msg)
            em.set_footer(text = "{}#{}".format(ctx.author.name, ctx.author.discriminator),
                          icon_url = "{}".format(ctx.author.avatar_url))
            return await ctx.send(embed = em)
            
        timeStamp = datetime.today().strftime("%Y-%m-%d %H.%M")
        filename = "{}-ChatFilter-{}.txt".format(ctx.guild.id, timeStamp)
        msg = "\n".join(serverOptions)
        
        msg = msg.encode('utf-8')
        with open(filename, "wb") as myfile:
            myfile.write(msg)
            
        await ctx.send(file=discord.File(filename))
        os.remove(filename)
        
    
    '''@commands.command(pass_context=True)
    async def setfilter(self, ctx, url = None):
        """Sets the word list to a passed text file url, or attachment contents (bot-admin only)."""
        if not await Utils.is_bot_admin_reply(ctx): return
            
        if url == None and len(ctx.message.attachments) == 0:
            await ctx.send("Usage: `{}setfilter [url or attachment]`".format(ctx.prefix))
            return
        
        if url == None:
            url = ctx.message.attachments[0].url
            
        '''
