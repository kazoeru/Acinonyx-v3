import asyncio, discord, time, parsedatetime, random
from   datetime import datetime
from   operator import itemgetter
from   discord.ext import commands
from   Cogs import Utils, Settings, ReadableTime, DisplayName, Nullify, CheckRoles

# Disini adalah module untuk admin
# dan hanya admin server yang dapat menggunakan command disini.


def setup(bot):
    # Tambahkan bot dan depenciesnya
    settings = bot.get_cog("Settings")
    bot.add_cog(Admin(bot, settings))

class Admin(commands.Cog):

    # Tambahkan init dengan referensi bot, dan referensi dari settings var.
    def __init__(self, bot, settings):
        self.bot = bot
        self.settings = settings
        global Utils, DisplayName
        Utils = self.bot.get_cog("Utils")
        DisplayName = self.bot.get_cog("DisplayName")

    def suppressed(self, guild, msg):
        # Cek apakah Acinonyx harus melakukan suppressing mention @here dan @everyone?
        if self.settings.getServerStat(guild, "SuppressMentions"):
            return Nullify.clean(msg)
        else:
            return msg
    
    async def test_message(self, message):
        # Diimplementasikan untuk melewati metode.call ini dua kali.
        return { "Ignore" : False, "Delete" : False }

    async def message_edit(self, before_message, message):
        # Proses pengeditan melalui function message jika diperukan.
        return await self.message(message)
        
    async def message(self, message):
        # Periksa message dan lihat apakah bot ini menyetujuinya? (default yes)
        # Pembatalan message tidak diperlukan dalam module ini.
        ignore = False
        delete = False
        res    = None
        # Periksa apakah member dalam status mute?
        isMute = self.settings.getUserStat(message.author, message.guild, "Muted")

        # Periksa apakah user seorang admin server?
        ctx = await self.bot.get_context(message)
        isAdmin = Utils.is_bot_admin(ctx)

        if isMute:
            ignore = True
            delete = True
            checkTime = self.settings.getUserStat(message.author, message.guild, "Cooldown")
            if checkTime:
                checkTime = int(checkTime)
            currentTime = int(time.time())
            
            # Buat DMnya
            if checkTime:
                # Masukan cooldownnya untuk status mute
                checkRead = ReadableTime.getReadableTimeBetween(currentTime, checkTime)
                checkReadEng = ReadableTime.getReadableTimeBetweenEng(currentTime, checkTime)
                res  = "<:indonesia:798977282886467635> **INDONESIA\n**"
                res += "Status kamu saat ini **Mute**.\nKamu harus menunggu *{}* sebelulm kamu dapat mengirim pesan di *{}.*\n\n".format(checkRead, self.suppressed(message.guild, message.guild.name))
                res += "<:English:798978134711599125> **ENGLISH**\n"
                res += "Your status is **Mute**.\nYou must wait *{}* before you can send message in *{}.*".format(checkReadEng, self.suppressed(message.guild, message.guild.name))
            else:
                # Jika tidak ada cooldown yang diterima, masukan mute tanpa batas waktu == 0
                res  = "<:indonesia:798977282886467635> **INDONESIA\n**"
                res += "kamu dalam status **Mute** diserver *{}* dan tidak dapat mengirim pesan hingga admin melepas status mute kamu.\n".format(self.suppressed(message.guild, message.guild.name))
                res += "<:English:798978134711599125> **ENGLISH**\n"
                res += "Your status is **mute** from server *{}*, you can't send message until admin remove your mute status."

            if checkTime and currentTime >= checkTime:
                # Acinonyx telah melewati pemeriksaan waktu
                ignore = False
                delete = False
                res    = None
                self.settings.setUserStat(message.author, message.guild, "Cooldown", None)
                self.settings.setUserStat(message.author, message.guild, "Muted", False)
            
        ignoreList = self.settings.getServerStat(message.guild, "IgnoredUsers")
        if ignoreList:
            for user in ignoreList:
                if not isAdmin and str(message.author.id) == str(user["ID"]):
                    ignore = True

        adminLock = self.settings.getServerStat(message.guild, "AdminLock")
        if not isAdmin and adminLock:
            ignore = True

        if isAdmin:
            ignore = False
            delete = False

        # Get Owner dan OwnerLock
        ownerLock = self.settings.getGlobalStat("OwnerLock",False)
        owner = self.settings.isOwner(message.author)
        # Periksa apakah pengguna command adalah owner? (dan kalau Acinonyx dalam status OwnerLock)
        if (not owner) and ownerLock:
            # Kalau bukan owner abaikan saja
            ignore = True
                
        if not isAdmin and res:
            await message.author.send(res)
        return { 'Ignore' : ignore, 'Delete' : delete}

    
    @commands.command(pass_context=True)
    async def defaultchannel(self, ctx):
        """**INDONESIA**
        Melihat default channel dalam server.
        
        **ENGLISH**
        Check default channel in this server"""
        default = None
        targetChan = ctx.guild.get_channel(ctx.guild.id)
        default = targetChan
        
        #Pastikan cek bahasa dari author
        LangCheck = self.settings.getUserStat(ctx.message.author, ctx.message.guild, "Language")

        targetChanID = self.settings.getServerStat(ctx.guild, "DefaultChannel")
        
        if LangCheck == None:
            # Author belum memilih bahasa
            await self.language_not_set(ctx)
            
        if len(str(targetChanID)):
            # Acinonyx akan memeriksa channelnya dalam database
            tChan = self.bot.get_channel(int(targetChanID))
            if tChan:
                # Acinonyx dapet nih channelnya
                targetChan = tChan
        if targetChan == None:
            # Jika Acinonyx tidak menemukan channel dalam database yang tersimpan
            if default == None:
                if LangCheck == "ID":
                    em = discord.Embed(color = 0XFF8C00, description = ">>> Tampaknya server ini tidak memiliki default channel yang telah diset\n\n"
                                                                       "**Panduan**\n"
                                                                       "*`{}setdefaultchannel [channel]`*".format(ctx.prefix))
                    em.set_author(name = "Default channel",
                                  icon_url = "https://cdn.discordapp.com/attachments/518118753226063887/725569194304733435/photo.jpg")
                    em.set_thumbnail(url = "{}".format(ctx.message.guild.icon_url))
                    em.set_footer(text = "Saat mengetik command, tanda [] tidak usah digunakan\n{}".format(ctx.author),
                                  icon_url = "{}".format(ctx.author.avatar_url))
                
                if LangCheck == "EN":
                    em = discord.Embed(color = 0XFF8C00, description = ">>> There is currently no default channel set\n\n"
                                                                       "**Usage**\n"
                                                                       "*`{}setdefaultchannel [channel]`*".format(ctx.prefix))
                    em.set_author(name = "Default channel",
                                  icon_url = "https://cdn.discordapp.com/attachments/518118753226063887/725569194304733435/photo.jpg")
                    em.set_thumbnail(url = "{}".format(ctx.message.guild.icon_url))
                    em.set_footer(text = "When typing commands, you don't need to use the [] sign\n{}".format(ctx.author),
                                  icon_url = "{}".format(ctx.author.avatar_url))
            
            else:
                if LangCheck == "ID":
                    em = discord.Embed(color = 0XFF8C00, description = ">>> **server {}**\n"
                                                                       "Default chanel server ini {}\n"
                                                                       "**Cara merubah default channel**\n"
                                                                       "Gunakan command `{}setdefaultchannel [mention_channel]`.\n\n"
                                                                       "**Menghapus default channel**\n"
                                                                       "Cukup dengan mengetik `{}setdefaultchannel` tanpa menambahkan `[mention_channel]` akan menghapus default channel yang terdaftar"
                                                                       .format(ctx.message.guild.name,
                                                                               default.mention,
                                                                               ctx.prefix,
                                                                               ctx.prefix
                                                                               ))
                    em.set_author(name = "Default channel list",
                                  icon_url = "https://cdn.discordapp.com/attachments/518118753226063887/725569194304733435/photo.jpg")
                    em.set_thumbnail(url = "{}".format(ctx.message.guild.icon_url))
                    em.set_footer(text = "Saat mengetik command, tanda [] tidak usah digunakan\n{}".format(ctx.author),
                                  icon_url = "{}".format(ctx.author.avatar_url))

                if LangCheck == "EN":
                    em = discord.Embed(color = 0XFF8C00, description = ">>> **server {}**\n"
                                                                       "Default channel in this server is {}\n\n"
                                                                       "**How to change?**\n"
                                                                       "Type *`{}setdefaultchannel [mention_channel]`*.\n\n"
                                                                       "**How to delete?**\n"
                                                                       "Just type *`{}setdefaultchannel`*\n"
                                                                       "without add anything, i will delete default channel"
                                                                       .format(ctx.message.guild.name,
                                                                               default.mention,
                                                                               ctx.prefix,
                                                                               ctx.prefix
                                                                               ))
                    em.set_author(name = "Default channel list", icon_url = "https://cdn.discordapp.com/attachments/518118753226063887/725569194304733435/photo.jpg")
                    em.set_thumbnail(url = "{}".format(ctx.message.guild.icon_url))
                    em.set_footer(text = "When typing commands, you don't need to use the [] sign\n{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
        
        else:
            # Acinonyx mendapatkan channel dari database
            if LangCheck == "ID":
                em = discord.Embed(color = 0XFF8C00, description = ">>> Default channel telah diterapkan ke {}\n\n"
                                                                    "**Cara merubah default channel**\n"
                                                                    "Gunakan command `{}setdefaultchannel [mention_channel]`.\n\n"
                                                                    "**Menghapus default channel**\n"
                                                                    "Cukup dengan mengetik *`{}setdefaultchannel`*\n"
                                                                    "tanpa menambahkan `[mention_channel]` aku akan menghapus default channel"
                                                                    .format(targetChan.mention,
                                                                            ctx.prefix,
                                                                            ctx.prefix))
                em.set_author(name = "Default channel list", icon_url = "https://cdn.discordapp.com/attachments/518118753226063887/725569194304733435/photo.jpg")
                em.set_thumbnail(url = "{}".format(ctx.message.guild.icon_url))
                em.set_footer(text = "Saat mengetik command, tanda [] tidak usah digunakan\n{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                
            if LangCheck == "EN":
                em = discord.Embed(color = 0XFF8C00, description = ">>> The default channel is set to {}\n\n"
                                                                   "**How to change?**\n"
                                                                   "Type *`{}setdefaultchannel [mention_channel]`*.\n\n"
                                                                   "**How to delete?**\n"
                                                                   "Just type *`{}setdefaultchannel`*\n"
                                                                   "without add anything, i will delete default channel"
                                                                   .format(targetChan.mention,
                                                                           ctx.prefix,
                                                                           ctx.prefix
                                                                           ))
                em.set_author(name = "Default channel list", icon_url = "https://cdn.discordapp.com/attachments/518118753226063887/725569194304733435/photo.jpg")
                em.set_thumbnail(url = "{}".format(ctx.message.guild.icon_url))
                em.set_footer(text = "When typing commands, you don't need to use the [] sign\n{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
        
        await ctx.channel.send(embed = em)
        
    
    @commands.command(pass_context=True)
    async def setdefaultchannel(self, ctx, *, channel: discord.TextChannel = None):
        """**INDONESIA**
        Menetapkan default channel untuk bot ini mengirim pesan.

        **ENGLISH**
        Sets a replacement default channel for bot messages
        
        (Admin server only)"""
        LangCheck = self.settings.getUserStat(ctx.message.author, ctx.message.guild, "Language")

        if not await Utils.is_admin_reply(ctx): return

        default = ctx.guild.get_channel(ctx.guild.id)

        if LangCheck == None:
            # Author belum memilih bahasa
            await self.language_not_set(ctx)

        if channel == None:
            self.settings.setServerStat(ctx.message.guild, "DefaultChannel", "")
            if default == None:
                if LangCheck == "ID":
                    msg = "Default channel telah *dihapus*."
                if LangCheck == "EN":
                    msg = "Default channel has been *deleted*"

            else:
                if LangCheck == "ID":
                    msg = "Default channel telah dikembalikan ke: **{}**.".format(default.mention)
                if LangCheck == "EN":
                    msg = "Default channel has been returned to the server\'s original:  **{}**".format(default.mention)
            em = discord.Embed(color = 0XFF8C00, description = msg)
            em.set_footer(text = "{}".format(ctx.author))
            await ctx.message.channel.send(embed = em)
            return

        self.settings.setServerStat(ctx.message.guild, "DefaultChannel", channel.id)

        if LangCheck == "ID":
            msg = "Default channel telah diset ke **{}.**".format(channel.mention)
        if LangCheck == "EN":
            msg = "Default channel has been set to **{}.**".format(channel.mention)
        em = discord.Embed(color = 0XFF8C00, description = msg)
        em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
        await ctx.message.channel.send(embed = em)
        
    
    @setdefaultchannel.error
    async def setdefaultchannel_error(self, error, ctx):
        # kalau default channel error
        msg = "setdefaultchannel Error: ```\n{}\n```".format(error)
        em = discord.Embed(color = 0XFF8C00, description = msg)
        em.set_footer(text = "{}#{}".format(ctx.author.name, ctx.author.discriminator))
        await ctx.channel.send(msg)
    

    # @commands.command(pass_context=True)
    # async def setmadlibschannel(self, ctx, *, channel: discord.TextChannel = None):
    #     """Sets the channel for MadLibs (admin only)."""
        
    #     if not await Utils.is_admin_reply(ctx): return

    #     if channel == None:
    #         self.settings.setServerStat(ctx.message.guild, "MadLibsChannel", "")
    #         msg = 'MadLibs dapat digunakan dalam *any channel* saat ini.'
    #         await ctx.message.channel.send(msg)
    #         return

    #     if type(channel) is str:
    #         try:
    #             role = discord.utils.get(message.guild.channels, name=role)
    #         except:
    #             print("Channel tidak ditemukan")
    #             return

    #     # If we made it this far - then we can add it
    #     self.settings.setServerStat(ctx.message.guild, "MadLibsChannel", channel.id)

    #     msg = 'MadLibs channel telah di set ke: **{}**.'.format(channel.name)
    #     await ctx.message.channel.send(msg)
        
    
    # @setmadlibschannel.error
    # async def setmadlibschannel_error(self, error, ctx):
    #     # do stuff
    #     msg = 'setmadlibschannel Error: {}'.format(error)
    #     await ctx.channel.send(msg)


    @commands.command(pass_context=True)
    async def xpreservelimit(self, ctx, *, limit = None):
        """**INDONESIA**
        Menetapkan batas penyimpanan xp maksimum untuk semua member.
        masukan angka negatif (-1) untuk menghapus batas perolehan xp.

        **ENGLISH**
        sets a limit to the maximum xp reserve a member can get.
        Pass a negative value (-1) for unlimited"""
        # Cek dulu bahasa yang dia pakai
        LangCheck = self.settings.getUserStat(ctx.message.author, ctx.message.guild, "Language")

        if not await Utils.is_admin_reply(ctx): return
        
        if LangCheck == None:
            # Author belum memilih bahasa
            await self.language_not_set(ctx)
        
        if limit == None:
            # Cek XPReserveLimit dalam database server
            server_lim = self.settings.getServerStat(ctx.guild, "XPReserveLimit")
            if server_lim == None:
                # Jika hasil pengecekan berada dalam status "None"
                # Acinonyx akan memberitahu bahwa server ini tidak memiliki batas penyimpanan xp
                if LangCheck == "ID":
                    em = discord.Embed(color = 0XFF8C00,
                                       description = ">>> Server *{}*\n"
                                                     "Saat ini tidak ada batas penyimpanan xp\n\n"
                                                     "**Panduan**\n"
                                                     "*`{}xpreservelimit [jumlah]`*\n\n"
                                                     "**Panduan menghapus limit**\n"
                                                     "*`{}xpreservelimit -[jumlah]`*"
                                                     .format(ctx.guild,
                                                             ctx.prefix,
                                                             ctx.prefix))
                    em.set_author(name = "Xp reserve limit", icon_url = "https://cdn.discordapp.com/attachments/518118753226063887/725569194304733435/photo.jpg")
                    em.set_footer(text = "Saat mengetik command, tanda [] tidak usah digunakan\n{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                    await ctx.send(embed=em)
                    return
                if LangCheck == "EN":
                    em = discord.Embed(color = 0XFF8C00,
                                       description = ">>> Server *{}*\n"
                                                     "There is no xp reserve limit\n\n"
                                                     "**Usage**\n"
                                                     "*`{}xpreservelimit [limit]`*\n\n"
                                                     "**How to delete?**\n"
                                                     "*`{}xpreservelimit -[limit]`*"
                                                     .format(ctx.guild,
                                                             ctx.prefix,
                                                             ctx.prefix))
                    em.set_author(name = "Xp reserve limit", icon_url = "https://cdn.discordapp.com/attachments/518118753226063887/725569194304733435/photo.jpg")
                    em.set_footer(text = "When typing commands, you don't need to use the [] sign\n{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                    await ctx.send(embed=em)
                    return

            else:
                if LangCheck == "ID":
                    em = discord.Embed(color = 0XFF8C00, description = "> Server *{}*\n"
                                                                       "> Saat ini batas penyimpanan xp adalah {:,}\n> \n"
                                                                       "> **Panduan menghapus limit**\n"
                                                                       "> Kamu bisa langsung ketik command sesuai dibawah ini untuk menghapus\n"
                                                                       "> *`{}xpreservelimit -{:,}`*"
                                                                       .format(ctx.guild,
                                                                               server_lim,
                                                                               ctx.prefix,
                                                                               server_lim))
                    em.set_author(name = "Xp reserve limit", icon_url = "https://cdn.discordapp.com/attachments/518118753226063887/725569194304733435/photo.jpg")
                    em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))                
                    await ctx.send(embed=em)
                    return
                if LangCheck == "EN":
                    em = discord.Embed(color = 0XFF8C00, description = "> Server *{}*\n"
                                                                       "> The current xp reserve limit is {:,}\n> \n"
                                                                       "> **How to delete?**\n"
                                                                       "> just type below this\n"
                                                                       "> *`{}xpreservelimit -{:,}`*"
                                                                       .format(ctx.guild,
                                                                               server_lim,
                                                                               ctx.prefix,
                                                                               server_lim))
                    em.set_author(name = "Xp reserve limit", icon_url = "https://cdn.discordapp.com/attachments/518118753226063887/725569194304733435/photo.jpg")
                    em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))                
                    await ctx.send(embed=em)
                    return

        try:
            limit = int(limit)
        except Exception:
            if LangCheck == "ID":
                msg = "┐(￣ヘ￣;)┌\nKamu harus memasukan berupa bilangan angka."
                em = discord.Embed(color = 0XFF8C00, description = msg)
                em.set_footer(text = "{}".format(ctx.author))
                await channel.send(embed = em)
                return
            if LangCheck == "EN":
                msg = "┐(￣ヘ￣;)┌\nYou must enter a number."
                em = discord.Embed(color = 0XFF8C00, description = msg)
                em.set_footer(text = "{}".format(ctx.author))
                await channel.send(embed = em)
                return

        if limit < 0:
            self.settings.setServerStat(ctx.guild, "XPReserveLimit", None)
            if LangCheck == "ID":
                await ctx.send("Batas untuk penyimpanan Xp telah dihilangkan!")
            if LangCheck == "EN":
                await ctx.send("Xp reserve limit removed!")
        else:
            self.settings.setServerStat(ctx.guild, "XPReserveLimit", limit)
            if LangCheck == "ID":
                em = discord.Embed(color = 0XFF8C00,
                                   description = "> Server *{}*\n"
                                                 "> Batas untuk memperoleh xp telah diset ke *{} xp*\n> \n"
                                                 "> **Cara menghapus.**\n"
                                                 "> Kamu bisa langsung ketik command sesuai dibawah ini untuk menghapus\n"
                                                 "> *`{}xpreservelimit -{}`*"
                                                 .format(ctx.guild,
                                                         limit,
                                                         ctx.prefix,
                                                         limit))
                em.set_author(name = "Xp reserve limit", icon_url = "https://cdn.discordapp.com/attachments/518118753226063887/725569194304733435/photo.jpg")
                em.set_footer(text = "{}".format(ctx.author.name), icon_url = "{}".format(ctx.author.avatar_url))
                await ctx.send(embed = em)

            if LangCheck == "EN":
                em = discord.Embed(color = 0XFF8C00,
                                   description = "> Server *{}*\n"
                                                 "> Xp reserve limit set to *{} xp*\n> \n"
                                                 "> **How to delete?**\n"
                                                 "> Just type below this\n"
                                                 "> *`{}xpreservelimit -{}`*"
                                                 .format(ctx.guild,
                                                         limit,
                                                         ctx.prefix,
                                                         limit))
                em.set_author(name = "Xp reserve limit", icon_url = "https://cdn.discordapp.com/attachments/518118753226063887/725569194304733435/photo.jpg")
                em.set_footer(text = "{}".format(ctx.author.name), icon_url = "{}".format(ctx.author.avatar_url))
                await ctx.send(embed = em)

    #@commands.command(pass_context=True)
    #async def onexprole(self, ctx, *, yes_no = None):
    #    """Mengatur satu role yang akan mendapatkan Xp."""

    #    LangCheck = self.settings.getUserStat(ctx.message.author, ctx.message.guild, "Language")
    #    setting_name = "One xp role at a time"
    #    setting_val  = "OnlyOneRole"

    #    if not await Utils.is_admin_reply(ctx): return
    #    current = self.settings.getServerStat(ctx.guild, setting_val)
    #    if yes_no == None:
    #        # Output what we have
    #        if current:
    #            msg = "{}\nSaat ini *dinyalakan.*".format(setting_name)
    #        else:
    #            msg = "{}\nSaat ini *dimatikan.*".format(setting_name)
    #    elif yes_no.lower() in [ "yes", "on", "true", "ya" ]:
    #        yes_no = True
    #        if current == True:
    #            msg = '{}\nSudah *dinyalakan*.'.format(setting_name)
    #        else:
    #            msg = '{}\nSekarang *dinyalakan*.'.format(setting_name)
    #    elif yes_no.lower() in [ "no", "off", "false", "disabled", "disable" ]:
    #        yes_no = False
    #        if current == False:
    #            msg = '{}\nSudah *dimatikan*.'.format(setting_name)
    #        else:
    #            msg = '{}\nSekarang *dimatikan*.'.format(setting_name)
    #    else:
    #        msg = "(￣ー￣;)ゞ\nSettingan yang kamu masukan salah."
    #        yes_no = current
    #    if not yes_no == None and not yes_no == current:
    #        self.settings.setServerStat(ctx.guild, setting_val, yes_no)
    #    em = discord.Embed(color = 0XFF8C00, description = msg)
    #    em.set_footer(text = "{}#{}".format(ctx.author.name, ctx.author.discriminator))
    #    await ctx.send(embed = em)


    @commands.command(pass_context=True)
    async def xplimit(self, ctx, *, limit = None):
        """**INDONESIA**
        Mengatur limit maksimum xp yang dapat di peroleh member.
        Gunakan bilangan negative (-) untuk membuat unlimited.
        
        **ENGLISH**
        Gets and sets a limit to the maximum xp a member can get.
        Pass a negative value for unlimited
        
        (Admin server only)"""

        if not await Utils.is_admin_reply(ctx): return

        LangCheck = self.settings.getUserStat(ctx.message.author, ctx.message.guild, "Language")

        if LangCheck == None:
            # Author belum memilih bahasa
            await self.language_not_set(ctx)

        if limit == None:
            # Periksa XPLimit dalam database Acinonyx
            server_lim = self.settings.getServerStat(ctx.guild, "XPLimit")
            if server_lim == None:
                if LangCheck == "ID":
                    msg = "Tidak ada batasan limit XP."
                if LangCheck == "EN":
                    msg = "There is no xp limit"
                em = discord.Embed(color = 0XFF8C00, description = msg)
                em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                return await ctx.send(embed = em)
            else:
                if LangCheck == "ID":
                    em = discord.Embed(color = 0XFF8C00,
                                       description = "> Server *{}*\n"
                                                     "> Limit maksimum Xp saat ini adalah {:,}\n> \n"
                                                     "> **Panduan menghapus limit xp**\n"
                                                     "> Kamu bisa langsung ketik command sesuai dibawah ini untuk menghapus\n"
                                                     "> `{}xpreservelimit -{}`"
                                                     .format(ctx.guild,
                                                             server_lim,
                                                             ctx.prefix,
                                                             server_lim))
                    em.set_author(name = "Xp Limit", icon_url = "https://cdn.discordapp.com/attachments/518118753226063887/725569194304733435/photo.jpg")
                    em.set_footer(text = "{}".format(ctx.author.name), icon_url = "{}".format(ctx.author.avatar_url))
                    await ctx.send(embed=em)
                    
                if LangCheck == "EN":
                    em = discord.Embed(color = 0XFF8C00,
                                       description = "> Server *{}*\n"
                                                     "> The current xp limit is {:,}\n> \n"
                                                     "> **How to delete?**\n"
                                                     "> Just type it below l, i will remove the current xp limit\n"
                                                     "> `{}xpreservelimit -{}`"
                                                     .format(ctx.guild,
                                                             server_lim,
                                                             ctx.prefix,
                                                             server_lim))
                    em.set_author(name = "Xp Limit", icon_url = "https://cdn.discordapp.com/attachments/518118753226063887/725569194304733435/photo.jpg")
                    em.set_footer(text = "{}".format(ctx.author.name), icon_url = "{}".format(ctx.author.avatar_url))
                    await ctx.send(embed=em)

        try:
            limit = int(limit)
        except Exception:
            if LangCheck == "ID":
                msg = "Harus berupa bilangan angka"
                em = discord.Embed(color = 0XFF8C00, description = msg)
                em.set_footer(text = "{}".format(ctx.author))
                await channel.send(embed = em)
                return 
            if LangCheck == "EN":
                msg = "Limit must be an integer"
                em = discord.Embed(color = 0XFF8C00, description = msg)
                em.set_footer(text = "{}".format(ctx.author))
                await channel.send(embed = em)
                return

        if limit < 0:
            self.settings.setServerStat(ctx.guild, "XPLimit", None)
            if LangCheck == "ID":
                msg = "limit xp dihapus!"
            if LangCheck == "EN":
                msg = "xp limit removed"
            em = discord.Embed(color = 0XFF8C00, description = msg)
            em.set_footer(text = "{}".format(ctx.author))
            await ctx.send(embed = em)
            return
        
        else:
            self.settings.setServerStat(ctx.guild, "XPLimit", limit)
            if LangCheck == "ID":
                em = discord.Embed(color = 0XFF8C00,
                                   description = "> Server *{}*\n"
                                                 "> Limit maksimum Xp telah ditetapkan ke {:,}\n> \n"
                                                 "> **Panduan penghapusan limit**\n"
                                                 "> Kamu bisa langsung ketik command sesuai dibawah ini untuk menghapus\n"
                                                 "> `{}xpreservelimit -{}`"
                                                 .format(ctx.guild,
                                                         server_lim,
                                                         ctx.prefix,
                                                         server_lim))
                em.set_author(name = "Xp Limit", icon_url = "https://cdn.discordapp.com/attachments/518118753226063887/725569194304733435/photo.jpg")
                em.set_footer(text = "{}".format(ctx.author.name), icon_url = "{}".format(ctx.author.avatar_url))
                await ctx.send(embed = em)
            
            if LangCheck == "EN":
                em = discord.Embed(color = 0XFF8C00,
                                   description = "> Server *{}*\n"
                                                 "> Xp limit set to {:,}\n> \n"
                                                 "> **How to delete?**\n"
                                                 "> just type below thi\n"
                                                 "> `{}xpreservelimit -{}`"
                                                 .format(ctx.guild,
                                                         server_lim,
                                                         ctx.prefix,
                                                         server_lim))
                em.set_author(name = "Xp Limit", icon_url = "https://cdn.discordapp.com/attachments/518118753226063887/725569194304733435/photo.jpg")
                em.set_footer(text = "{}".format(ctx.author.name), icon_url = "{}".format(ctx.author.avatar_url))
                await ctx.send(embed = em)

    @commands.command(pass_context=True)
    async def setxp(self, ctx, *, member = None, xpAmount : int = None):
        """**INDONESIA**
        Menetapkan batas Xp untuk member yang dimention.

        **ENGLISH**
        Set's an absolute value for the member's xp reserve.
        (Admin server only)"""
        
        author  = ctx.message.author
        server  = ctx.message.guild
        channel = ctx.message.channel
        LangCheck = self.settings.getUserStat(ctx.message.author, ctx.message.guild, "Language")

        if LangCheck == None:
            # Author belum memilih bahasa
            await self.language_not_set(ctx)

        if LangCheck == "ID":
            em = discord.Embed(color = 0XFF8C00,
                               description = ">>> Set batas limit xp untuk member yang dimention\n\n"
                                             "**Penggunaan**\n"
                                             "`{}setxp [member] [jumlah]`\n"
                                             .format(ctx.prefix))
            em.set_author(name = "Set Xp", icon_url = "https://cdn.discordapp.com/attachments/518118753226063887/725569194304733435/photo.jpg")
            em.set_footer(text = "Saat mengetik command, tanda [] tidak usah digunakan\n{}".format(ctx.author.name),
                          icon_url = "{}".format(ctx.author.avatar_url))

        if LangCheck == "EN":
            em = discord.Embed(color = 0XFF8C00,
                               description = ">>> Set's an absolute value for the member's xp reserve\n"
                                             "**Usage**\n"
                                             "`{}setxp [member] [value]`\n"
                                             .format(ctx.prefix))
            em.set_author(name = "Set Xp", icon_url = "https://cdn.discordapp.com/attachments/518118753226063887/725569194304733435/photo.jpg")
            em.set_footer(text = "When typing commands, you don't need to use the [] sign\n{}".format(ctx.author.name), 
                          icon_url = "{}".format(ctx.author.avatar_url))

        # Periksa terlebih dahulu apakah Acinonyx harus menggunakan mention @here dan @everyone
        if self.settings.getServerStat(server, "SuppressMentions"):
            suppress = True
        else:
            suppress = False
        
        if not await Utils.is_admin_reply(ctx): return

        if member == None:
            await ctx.message.channel.send(embed = em)
            return

        if xpAmount == None:
            # Periksa XP yang ada dalam database Acinonyx
            nameCheck = DisplayName.checkNameForInt(member, server)
            if not nameCheck or nameCheck['Member'] is None:
                nameCheck = DisplayName.checkRoleForInt(member, server)
                if not nameCheck:
                    await ctx.message.channel.send(embed = em)
                    return
            if "Role" in nameCheck:
                mem = nameCheck["Role"]
            else:
                mem = nameCheck["Member"]
            exp = nameCheck["Int"]
            if not mem:
                if LangCheck == "ID":
                    msg = '┐(￣ヘ￣;)┌\nAku tidak dapat menemukan *{}* dalam server.'.format(member)
                if LangCheck == "EN":
                    msg = '┐(￣ヘ￣;)┌\nI couldn\'t find *{}* on the server.'.format(member)
                if suppress:
                    msg = Nullify.clean(msg)
                await ctx.message.channel.send(msg)
                return
            member   = mem
            xpAmount = exp
            
        if xpAmount == None:
            await channel.send(embed = em)
            return

        if type(member) is discord.Member:
            self.settings.setUserStat(member, server, "XP", xpAmount)
        
        else:
            for m in ctx.guild.members:
                if member in m.roles:
                    self.settings.setUserStat(m, server, "XP", xpAmount)
        if LangCheck == "ID":
            msg = 'Limit xp untuk user *{}* telah diset ke *{:,}!*'.format(DisplayName.name(member), xpAmount)
        if LangCheck == "EN":
            msg = '*{}\'s* XPReserve was set to *{:,}!*'.format(DisplayName.name(member), xpAmount)
        
        if suppress:
            msg = Nullify.clean(msg)
        em = discord.Embed(color = 0XFF8C00, description = msg)
        em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
        await channel.send(embed = em)
        await CheckRoles.checkroles(member, channel, self.settings, self.bot)


    @commands.command(pass_context=True)
    async def setxpreserve(self, ctx, *, member = None, xpAmount : int = None):
        """**INDONESIA**
        Menetapkan batas penyimpanan Xp untuk member yang di mention (admin only).

        **ENGLISH**
        Set's an absolute value for the member's xp reserve
        """
        
        author  = ctx.message.author
        server  = ctx.message.guild
        channel = ctx.message.channel
        LangCheck = self.settings.getUserStat(ctx.message.author, ctx.message.guild, "Language")

        if LangCheck == None:
            # Author belum memilih bahasa
            await self.language_not_set(ctx)

        if LangCheck == "ID":
            em = discord.Embed(color = 0XFF8C00,
                               description = "> Set batas limit perolehan xp untuk member yang dimention\n"
                                             "> \n"
                                             "> **Panduan**\n"
                                             "> `{}setxpreserve [mention_member] [jumlah]`\n"
                                             .format(ctx.prefix))
            em.set_author(name = "Set xp Reserve", icon_url = "https://cdn.discordapp.com/attachments/518118753226063887/725569194304733435/photo.jpg")
            em.set_footer(text = "Saat mengetik command, tanda [] tidak usah digunakan\n{}".format(ctx.author.name),
                          icon_url = "{}".format(ctx.author.avatar_url))
        if LangCheck == "EN":
            em = discord.Embed(color = 0XFF8C00,
                               description = "> Set's an absolute value for the member's xp reserve\n"
                                             "> \n"
                                             "> **Usage**\n"
                                             "> `{}setxpreserve [mention_member] [value]`\n"
                                             .format(ctx.prefix))
            em.set_author(name = "Set xp Reserve",
                          icon_url = "https://cdn.discordapp.com/attachments/518118753226063887/725569194304733435/photo.jpg")
            em.set_footer(text = "When typing commands, you don't need to use the [] sign\n{}".format(ctx.author.name),
                          icon_url = "{}".format(ctx.author.avatar_url))

        # Periksa terlebih dahulu apakah Acinonyx harus menggunakan mention @here dan @everyone
        if self.settings.getServerStat(server, "SuppressMentions"):
            suppress = True
        else:
            suppress = False
        
        if not await Utils.is_admin_reply(ctx): return

        if member == None:
            await ctx.message.channel.send(embed = em)
            return
        
        if xpAmount == None:
            nameCheck = DisplayName.checkNameForInt(member, server)
            if not nameCheck or nameCheck['Member'] is None:
                nameCheck = DisplayName.checkRoleForInt(member, server)
                if not nameCheck:
                    await ctx.message.channel.send(embed = em)
                    return
            if "Role" in nameCheck:
                mem = nameCheck["Role"]
            else:
                mem = nameCheck["Member"]
            exp = nameCheck["Int"]
            if not mem:
                if LangCheck == "ID":
                    msg = '┐(￣ヘ￣;)┌\nAku tidak dapat menemukan *{}* dalam server.'.format(member)
                if LangCheck == "EN":
                    msg = '┐(￣ヘ￣;)┌\nI couldn\'t find *{}* on the server.'.format(member)

                if suppress:
                    msg = Nullify.clean(msg)
                em = discord.Embed(color = 0XFF8C00, description = msg)
                em.set_footer(text = "{}".format(ctx.author),
                              icon_url = "{}".format(ctx.author.avatar_url))
                await ctx.message.channel.send(embed = em)
                return
            member   = mem
            xpAmount = exp
            
        if xpAmount == None:
            await channel.send(embed = em)
            return

        if type(member) is discord.Member:
            self.settings.setUserStat(member, server, "XPReserve", xpAmount)
        else:
            for m in ctx.guild.members:
                if member in m.roles:
                    self.settings.setUserStat(m, server, "XPReserve", xpAmount)
        if LangCheck == "ID":
            msg = 'XpReserve untuk user *{}* telah diset ke *{:,}*'.format(DisplayName.name(member), xpAmount)
        if LangCheck == "EN":
            msg = '*{}\'s* XPReserve was set to *{:,}!*'.format(DisplayName.name(member), xpAmount)
        em = discord.Embed(color = 0XFF8C00, description = msg)
        em.set_footer(text = "{}".format(ctx.author))
        await channel.send(embed = em)

    
    @commands.command(pass_context=True)
    async def setdefaultrole(self, ctx, *, role : str = None):
        """**INDONESIA**
        Mengatur default role saat member bergabung dengan server.

        **ENGLISH**
        Set default role when member joined your server.
        (Admin server only)"""
        author  = ctx.message.author
        server  = ctx.message.guild
        channel = ctx.message.channel
        LangCheck = self.settings.getUserStat(ctx.message.author, ctx.message.guild, "Language")

        if LangCheck == None:
            # Author belum memilih bahasa
            await self.language_not_set(ctx)

        # Periksa pesan apakah Acinonyx akan melakukan suppressing mention @here dan @everyone
        if self.settings.getServerStat(server, "SuppressMentions"):
            suppress = True
        else:
            suppress = False

        if not await Utils.is_admin_reply(ctx): return

        if role is None:
            # Nonaktifkan auto-role dan terapkan ke default ""
            self.settings.setServerStat(server, "DefaultRole", "")
            if LangCheck == "ID":
                msg = 'Auto-role management sekarang **dimatikan**.'
                em = discord.Embed(color = 0XFF8C00, description = msg)
                em.set_footer(text = "{}#{}".format(ctx.author.name, ctx.author.discriminator))
                await channel.send(embed = em)
                return
            if LangCheck == "EN":
                msg = 'Auto-role management is **disabled**.'
                em = discord.Embed(color = 0XFF8C00, description = msg)
                em.set_footer(text = "{}#{}".format(ctx.author.name, ctx.author.discriminator))
                await channel.send(embed = em)
                return

        if type(role) is str:
            if role == "everyone":
                role = "@everyone"
            roleName = role
            role = DisplayName.roleForName(roleName, server)
            if not role:
                if LangCheck == "ID":
                    msg = '┐(￣ヘ￣;)┌\nAku tidak dapat menemukan *{}*...'.format(roleName)
                if LangCheck == "EN":
                    msg = "┐(￣ヘ￣;)┌\nI can't find *{}*...".format(roleName)
                # Cek suppress message
                if suppress:
                    msg = Nullify.clean(msg)
                em = discord.Embed(color = 0XFF8C00, description = msg)
                em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                await ctx.message.channel.send(embed = em)
                return

        self.settings.setServerStat(server, "DefaultRole", role.id)
        rolename = role.name
        # Cek suppress message
        if suppress:
            rolename = Nullify.clean(rolename)
        if LangCheck == "ID":
            em = discord.Embed(color = 0XFF8C00,
                               description = ">>> Kamu telah menetapkan default role ke *{}*\n> \n"
                                             "**Cara menghapus**\n"
                                             "Dengan mengetik *`{}setdefaultrole`* tanpa memasukan `[role]` kamu akan menghapus default role".format(rolename, ctx.prefix))
            em.set_author(name = "Set default role", icon_url = "https://cdn.discordapp.com/attachments/518118753226063887/725569194304733435/photo.jpg")
            em.set_footer(text = "Saat mengetik command, tanda [] tidak usah digunakan\n{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
        if LangCheck == "EN":
            em = discord.Embed(color = 0XFF8C00,
                               description = ">>> Default role set to *{}*'\n> \n"
                                             "**How to delete?**\n"
                                             "Just type *`{}setdefaultrole`* without `[role]` i will delete the default role".format(rolename, ctx.prefix))
            em.set_author(name = "Set default role", icon_url = "https://cdn.discordapp.com/attachments/518118753226063887/725569194304733435/photo.jpg")
            em.set_footer(text = "When typing commands, you don't need to use the [] sign\n{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
        await channel.send(embed = em)


    @setdefaultrole.error
    async def setdefaultrole_error(self, error, ctx):
        # Kalo default role error
        msg = 'setdefaultrole Error: ```\n{}\n```'.format(error)
        em = discord.Embed(color = 0XFF8C00, description = msg)
        em.set_footer(text = "{}#{}".format(ctx.author.name, ctx.author.discriminator))
        await ctx.channel.send(embed = em)


    @commands.command(pass_context=True)
    async def addxprole(self, ctx, *, role = None, xp : int = None):
        """**INDONESIA**
        Menambahkan role xp untuk system promotion/demotion.

        **ENGLISH**
        Adds a new role to the xp promotion/demotion system
        (Admin server only)
        """
        
        author  = ctx.message.author
        server  = ctx.message.guild
        channel = ctx.message.channel
        LangCheck = self.settings.getUserStat(ctx.message.author, ctx.message.guild, "Language")

        if LangCheck == None:
            # Author belum memilih bahasa
            await self.language_not_set(ctx)

        if LangCheck == "ID":
            em = discord.Embed(color = 0XFF8C00,
                               description = "> menambahkan role dari list promotion/demotion\n"
                                             "> \n"
                                             "> **Panduan**\n"
                                             "> `{}addxprole [role] [jumlah Xp]`\n"
                                             .format(ctx.prefix))
            em.set_author(name = "Set xp member", icon_url = "https://cdn.discordapp.com/attachments/518118753226063887/725569194304733435/photo.jpg")
            em.set_footer(text = "Saat mengetik command, tanda [] tidak usah digunakan\n{}".format(ctx.author.name),
                          icon_url = "{}".format(ctx.author.avatar_url))
        if LangCheck == "EN":
            em = discord.Embed(color = 0XFF8C00,
                               description = "> Adds a new role to the xp promotion/demotion system\n"
                                             "> \n"
                                             "> **Usage**\n"
                                             "> `{}addxprole [role] [value]`\n"
                                             .format(ctx.prefix))
            em.set_author(name = "Set xp member", icon_url = "https://cdn.discordapp.com/attachments/518118753226063887/725569194304733435/photo.jpg")
            em.set_footer(text = "When typing commands, you don't need to use the [] sign\n{}".format(ctx.author.name),
                          icon_url = "{}".format(ctx.author.avatar_url))

        # Periksa pesan apakah Acinonyx akan melakukan suppressing mention @here dan @everyone
        if self.settings.getServerStat(server, "SuppressMentions"):
            suppress = True
        else:
            suppress = False
        
        if not await Utils.is_admin_reply(ctx): return
        if xp == None:
            # Cek dulu databasenya entah XP tidak di setting atau mungkin ada di section akhir
            if type(role) is str:
                if role == "everyone":
                    role = "@everyone"
                roleCheck = DisplayName.checkRoleForInt(role, server)
                if not roleCheck:
                    await ctx.message.channel.send(embed = em)
                    return
                if not roleCheck["Role"]:
                    if LangCheck == "ID":
                        msg = '┐(￣ヘ￣;)┌\nAku tidak dapat menemukan *{}* dalam server.'.format(role)
                    if LangCheck == "EN":
                        msg = '┐(￣ヘ￣;)┌\nI couldn\'t find *{}* on the server.'.format(role)
                    # Cek suppress messagenya
                    if suppress:
                        msg = Nullify.clean(msg)
                    em = discord.Embed(color = 0XFF8C00, description = msg)
                    em.set_footer(text = "{}".format(ctx.author))
                    await ctx.message.channel.send(embed = em)
                    return
                role = roleCheck["Role"]
                xp   = roleCheck["Int"]

        if xp == None:
            await channel.send(embed = em)
            return
        if not type(xp) is int:
            await channel.send(embed = em)
            return

        # Sekarang Acinonyx akan melihat apakah server tersebut sudah memiliki role dalam database?
        promoArray = self.settings.getServerStat(server, "PromotionArray")
        for aRole in promoArray:
            # Get role yang sesuai dengan id
            if str(aRole['ID']) == str(role.id):
                aRole['XP'] = xp
                if LangCheck == "ID":
                    msg = 'Role **{}** telah diupdate! membutuhkan xp:  *{:,}*'.format(role.name, xp)
                if LangCheck == "EN":
                    msg = 'Role **{}** updated!  Required xp:  *{:,}*'.format(role.name, xp)
                # Cek suppress messagenya
                if suppress:
                    msg = Nullify.clean(msg)
                em = discord.Embed(color = 0XFF8C00, description = msg)
                em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                await channel.send(embed = em)
                return

        # If we made it this far - then we can add it
        promoArray.append({ 'ID' : role.id, 'Name' : role.name, 'XP' : xp })
        self.settings.setServerStat(server, "PromotionArray", promoArray)
        if LangCheck == "ID":
            msg = 'Role **{}** telah ditambahkan kedalam list.\nMembutuhkan xp: *{:,}*'.format(role.name, xp)
        if LangCheck == "EN":
            msg = 'Role **{}** added to list.  Required xp: *{:,}*'.format(role.name, xp)
        # Check for suppress
        if suppress:
            msg = Nullify.clean(msg)
        em = discord.Embed(color = 0XFF8C00, description = msg)
        em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
        await channel.send(embed = em)
        return
        
    @commands.command(pass_context=True)
    async def removexprole(self, ctx, *, role = None):
        """**INDONESIA
        Menghapus dari xp sistem promotion/demotion.

        **ENGLISH**
        Removes a role from the xp promotion/demotion system.
        (Admin server only)"""
        
        author  = ctx.message.author
        server  = ctx.message.guild
        channel = ctx.message.channel
        LangCheck = self.settings.getUserStat(ctx.message.author, ctx.message.guild, "Language")

        if LangCheck == None:
            # Author belum memilih bahasa
            await self.language_not_set(ctx)

        if LangCheck == "ID":
            em = discord.Embed(color = 0XFF8C00,
                               description = ">>> Menghapus role dari list promotion/demotion\n\n"
                                             "**Penggunaan**\n"
                                             "`{}removexprole [role]`\n".format(ctx.prefix))
            em.set_author(name = "Remove xp Role", icon_url = "https://cdn.discordapp.com/attachments/518118753226063887/725569194304733435/photo.jpg")
            em.set_footer(text = "Saat mengetik command, tanda [] tidak usah digunakan\n{}".format(ctx.author),
                          icon_url = "{}".format(ctx.author.avatar_url))
        if LangCheck == "EN":
            em = discord.Embed(color = 0XFF8C00,
                               description = ">>> Removes a role from the xp promotion/demotion system\n\n"
                                             "**Usage**\n"
                                             "`{}removexprole [role]`\n".format(ctx.prefix))
            em.set_author(name = "Remove xp Role", icon_url = "https://cdn.discordapp.com/attachments/518118753226063887/725569194304733435/photo.jpg")
            em.set_footer(text = "When typing commands, you don't need to use the [] sign\n{}".format(ctx.author),
                          icon_url = "{}".format(ctx.author.avatar_url))

        # Periksa pesan apakah Acinonyx akan melakukan suppressing mention @here dan @everyone
        if self.settings.getServerStat(server, "SuppressMentions"):
            suppress = True
        else:
            suppress = False
        
        if not await Utils.is_admin_reply(ctx): return

        if role == None:
            await channel.send(embed = em)
            return

        if type(role) is str:
            if role == "everyone":
                role = "@everyone"
            # Cari nama role terlebih dahulu lalu cari idnya
            promoArray = self.settings.getServerStat(server, "PromotionArray")

            for aRole in promoArray:
                # Ambil role dari database yang sesuai dengan namanya
                if aRole['Name'].lower() == role.lower() or str(aRole["ID"]) == str(role):
                    # Kalau dapet role sesuai yang di minta, hapus aja
                    promoArray.remove(aRole)
                    self.settings.setServerStat(server, "PromotionArray", promoArray)
                    if LangCheck == "ID":
                        msg = "**{}** telah dihapus.".format(aRole['Name'])
                    if LangCheck == "EN":
                        msg = "**{}** removed successfully.".format(aRole['Name'])
                    # Cek suppress message
                    if suppress:
                        msg = Nullify.clean(msg)
                    em = discord.Embed(color = 0XFF8C00, description = msg)
                    em.set_footer(text = "{}".format(ctx.author))
                    await channel.send(embed = em)
                    return
            # Disini Acinonyx tidak dapat menemukan nama role yang diminta
            # Periksa lagi apakah role sudah berganti nama?

            roleCheck = DisplayName.roleForName(role, server)
            if roleCheck:
                # Acinonyx menamukan role yang diminta
                # Pada posisi ini, role tersebut adalah role yang diminta
                promoArray = self.settings.getServerStat(server, "PromotionArray")

                for aRole in promoArray:
                    # Kalau dapet role sesuai yang di minta, hapus aja
                    if str(aRole['ID']) == str(roleCheck.id):
                        promoArray.remove(aRole)
                        self.settings.setServerStat(server, "PromotionArray", promoArray)
                        if LangCheck == "ID":
                            msg = "**{}** telah dihapus.".format(aRole['Name'])
                        if LangCheck == "EN":
                            msg = "**{}** removed successfully.".format(aRole['Name'])
                        # Cek suppress message
                        if suppress:
                            msg = Nullify.clean(msg)
                        em = discord.Embed(color = 0XFF8C00, description = msg)
                        em.set_footer(text = "{}#{}".format(ctx.author.name, ctx.author.discriminator))
                        await channel.send(embed = em)
                        return
                
            # Acinonyx tidak dapat menemukan role yang diminta
            if LangCheck == "ID":
                msg = '┐(￣ヘ￣;)┌\nAku tidak dapat menemukan role *{}* dalam list ku.'.format(role)
            if LangCheck == "EN":
                msg = '┐(￣ヘ￣;)┌\nI can\'t find *{}* in my list.'.format(role)
            # Cek suppress message
            if suppress:
                msg = Nullify.clean(msg)
            em = discord.Embed(color = 0XFF8C00, description = msg)
            em.set_footer(text = "{}".format(ctx.author))
            await channel.send(embed = em)
            return

        promoArray = self.settings.getServerStat(server, "PromotionArray")

        for aRole in promoArray:
            # Ambil role dari database yang sesuai dengan namanya
            if str(aRole['ID']) == str(role.id):
                # Kalau ketemu, hapus aja
                promoArray.remove(aRole)
                self.settings.setServerStat(server, "PromotionArray", promoArray)
                if LangCheck == "ID":
                    msg = "**{}** telah dihapus.".format(aRole['Name'])
                if LangCheck == "EN":
                    msg = "**{}** removed successfully.".format(aRole['Name'])
                # Cek suppress message
                if suppress:
                    msg = Nullify.clean(msg)
                em = discord.Embed(color = 0XFF8C00, description = msg)
                em.set_footer(text = "{}".format(ctx.author))
                await channel.send(embed = em)
                return

        # Acinonyx tidak dapat menemukan role yang diminta
        if LangCheck == "ID":
            msg = "┐(￣ヘ￣;)┌\n*{}* tidak ada dalam list.".format(role.name)
        if LangCheck == "EN":
            msg = "┐(￣ヘ￣;)┌\nI can\'t find *{}* in my list.".format(role.name)
        # Cek suppress message
        if suppress:
            msg = Nullify.clean(msg)
        em = discord.Embed(color = 0XFF8C00, description = msg)
        em.set_footer(text = "{}".format(ctx.author))
        await channel.send(embed = em)

    @commands.command(pass_context=True)
    async def prunexproles(self, ctx):
        """**INDONESIA**
        Menghapus semua role dari system promotion/demotion yang tidak ada dalam server.

        **ENGLISH**
        Removes any roles from the xp promotion/demotion system that are no longer on the server
        (Admin server only)"""

        author  = ctx.message.author
        server  = ctx.message.guild
        channel = ctx.message.channel
        LangCheck = self.settings.getUserStat(ctx.message.author, ctx.message.guild, "Language")

        if LangCheck == None:
            # Author belum memilih bahasa
            await self.language_not_set(ctx)

        if not await Utils.is_admin_reply(ctx): return

        # Get array
        promoArray = self.settings.getServerStat(server, "PromotionArray")
        # Tadinya sih gw mau pakai itemgetter cuma nggk jadi, lebih efisien pakai lambda
        # promoSorted = sorted(promoArray, key=itemgetter('XP', 'Name')) 
        promoSorted = sorted(promoArray, key=lambda x:int(x['XP']))
        
        removed = 0
        for arole in promoSorted:
            # Mencari nama role bersadasarkan nomor ID role
            foundRole = False
            for role in server.roles:
                if str(role.id) == str(arole['ID']):
                    # Ketemu nih
                    foundRole = True
            if not foundRole:
                promoArray.remove(arole)
                removed += 1

        if LangCheck == "ID":
            msg = "Menghapus *{}* role dari list promotion/demotion yang tidak terpakai.".format(removed)
        if LangCheck == "EN":
            msg = "Removed *{}* orphaned roles."
        em = discord.Embed(color = 0XFF8C00, description = msg)
        em.set_footer(text = "{}#{}".format(ctx.author.name, ctx.author.discriminator))
        await ctx.message.channel.send(embed = em)
        

    @commands.command(pass_context=True)
    async def setxprole(self, ctx, *, role : str = None):
        """**INDONESIA**
        Mengatur minimum role ID untuk transfer xp, gamble, atau memberi makan bot.

        **ENGLISH**
        Sets the required role ID to give xp, gamble, or feed the bot
        (Admin server only)"""
        LangCheck = self.settings.getUserStat(ctx.message.author, ctx.message.guild, "Language")

        if LangCheck == None:
            # Author belum memilih bahasa
            await self.language_not_set(ctx)

        # Periksa pesan apakah Acinonyx akan melakukan suppressing mention @here dan @everyone
        if self.settings.getServerStat(ctx.message.guild, "SuppressMentions"):
            suppress = True
        else:
            suppress = False

        if not await Utils.is_admin_reply(ctx): return

        if role == None:
            self.settings.setServerStat(ctx.message.guild, "RequiredXPRole", "")
            if LangCheck == "ID":
                msg = "*Semua member* dapat Transfer xp, gamble, dan memberi makan bot."
            if LangCheck == "EN":
                msg = "Giving xp, gambling, and feeding the bot now available to *everyone*"
            em = discord.Embed(color = 0XFF8C00, description = msg)
            em.set_footer(text = "{}#{}".format(ctx.author.name, ctx.author.discriminator))
            await ctx.message.channel.send(embed = em)
            return

        if type(role) is str:
            if role == "everyone":
                role = "@everyone"
            roleName = role
            role = DisplayName.roleForName(roleName, ctx.message.guild)
            if not role:
                if LangCheck == "ID":
                    msg = "┐(￣ヘ￣;)┌\nAku tidak dapat menemukan role *{}*...".format(roleName)
                if LangCheck == "EN":
                    msg = "┐(￣ヘ￣;)┌\nI couldn\'t find *{}*...".format(roleName)
                # Cek suppress message
                if suppress:
                    msg = Nullify.clean(msg)
                em = discord.Embed(color = 0XFF8C00, description = msg)
                em.set_footer(text = "{}".format(ctx.author))
                await ctx.message.channel.send(embed = em)
                return

        # Kalau semuanya sudah OK, tanpa masalah bisa lanjut kebawah ini
        self.settings.setServerStat(ctx.message.guild, "RequiredXPRole", role.id)
        if LangCheck == "ID":
            msg = "Transfer xp, gamble, atau memberi makan bot telah diset untuk role **{}**.".format(role.name)
        if LangCheck == "EN":
            msg = "Role required to give xp, gamble, or feed the bot set to **{}**.".format(role.name)
        # Check for suppress
        if suppress:
            msg = Nullify.clean(msg)
        em = discord.Embed(color = 0XFF8C00, description = msg)
        em.set_footer(text = "{}#{}".format(ctx.author.name, ctx.author.discriminator))
        await ctx.message.channel.send(embed = em)
        
    
    @setxprole.error
    async def xprole_error(self, error, ctx):
        # xprole error
        msg = 'xprole Error: {}'.format(error)
        em = discord.Embed(color = 0XFF8C00, description = msg)
        em.set_footer(text = "{}#{}".format(ctx.author.name, ctx.author.discriminator))
        await ctx.channel.send(embed = em)

    @commands.command(pass_context=True)
    async def xprole(self, ctx):
        """**INDONESIA**
        Daftar list role untuk transfer Xp, gamble, atau memberi makan bot.

        **ENGLISH**
        Lists the required role to give xp, gamble, or feed the bot"""
        LangCheck = self.settings.getUserStat(ctx.message.author, ctx.message.guild, "Language")

        if LangCheck == None:
            # Author belum memilih bahasa
            await self.language_not_set(ctx)

        # Periksa pesan apakah Acinonyx akan melakukan suppressing mention @here dan @everyone
        if self.settings.getServerStat(ctx.message.guild, "SuppressMentions"):
            suppress = True
        else:
            suppress = False

        role = self.settings.getServerStat(ctx.message.guild, "RequiredXPRole")
        if role == None or role == "":
            if LangCheck == "ID":
                msg = "**Semua member** dapat transfer Xp, gamble, dan memberi makan bot."
            if LangCheck == "EN":
                msg = "**Everyone** can give xp, gamble, and feed the bot."
            em = discord.Embed(color = 0XFF8C00, description = msg)
            em.set_footer(text = "{}".format(ctx.author))
            await ctx.message.channel.send(embed = em)
        else:
            # Role telah diset, berikan namanya
            found = False
            for arole in ctx.message.guild.roles:
                if str(arole.id) == str(role):
                    found = True
                    vowels = "aeiou"
                    if arole.name[:1].lower() in vowels:
                        if LangCheck == "ID":
                            msg = "Kamu membutuhkan role **{}** untuk *transfer xp*, *gamble*, atau *memberi makan* bot.".format(arole.name)
                        if LangCheck == "EN":
                            msg = "You need to be an **{}** to *give xp*, *gamble*, or *feed* the bot.".format(arole.name)
                    else:
                        if LangCheck == "ID":
                            msg = "Kamu membutuhkan role **{}** untuk *transfer xp*, *gamble*, atau *memberi makan* bot.".format(arole.name)
                        if LangCheck == "EN":
                            msg = "You need to be a **{}** to *give xp*, *gamble*, or *feed* the bot.".format(arole.name)
            if not found:
                if LangCheck == "ID":
                    msg = 'Tidak ada role yang cocok dengan ID: `{}`\nPemilik server mungkin telah menghapusnya, cobalah set ulang kembali.'.format(role)
                if LangCheck == "EN":
                    msg = 'There is no role that matches id: `{}`\nconsider updating this setting.'.format(role)
            # Cek suppress message
            if suppress:
                msg = Nullify.clean(msg)
            em = discord.Embed(color = 0XFF8C00, description = msg)
            em.set_footer(text = "{}".format(ctx.author))
            await ctx.message.channel.send(embed = em)
        
    # @commands.command(pass_context=True)
    # async def setstoprole(self, ctx, *, role : str = None):
    #     """Sets the required role ID to stop the music player (admin only)."""
        
    #     # Check if we're suppressing @here and @everyone mentions
    #     if self.settings.getServerStat(ctx.message.guild, "SuppressMentions"):
    #         suppress = True
    #     else:
    #         suppress = False

    #     if not await Utils.is_admin_reply(ctx): return

    #     if role == None:
    #         self.settings.setServerStat(ctx.message.guild, "RequiredStopRole", "")
    #         msg = 'Stopping the music now *admin-only*.'
    #         await ctx.message.channel.send(msg)
    #         return

    #     if type(role) is str:
    #         if role == "everyone":
    #             role = "@everyone"
    #         roleName = role
    #         role = DisplayName.roleForName(roleName, ctx.message.guild)
    #         if not role:
    #             msg = 'I couldn\'t find *{}*...'.format(roleName)
    #             # Check for suppress
    #             if suppress:
    #                 msg = Nullify.clean(msg)
    #             await ctx.message.channel.send(msg)
    #             return

    #     # If we made it this far - then we can add it
    #     self.settings.setServerStat(ctx.message.guild, "RequiredStopRole", role.id)

    #     msg = 'Role required to stop the music player set to **{}**.'.format(role.name)
    #     # Check for suppress
    #     if suppress:
    #         msg = Nullify.clean(msg)
    #     await ctx.message.channel.send(msg)
        
    
    # @setstoprole.error
    # async def stoprole_error(self, error, ctx):
    #     # do stuff
    #     msg = 'setstoprole Error: {}'.format(error)
    #     await ctx.channel.send(msg)

    # @commands.command(pass_context=True)
    # async def stoprole(self, ctx):
    #     """Lists the required role to stop the bot from playing music."""

    #     # Check if we're suppressing @here and @everyone mentions
    #     if self.settings.getServerStat(ctx.message.guild, "SuppressMentions"):
    #         suppress = True
    #     else:
    #         suppress = False

    #     role = self.settings.getServerStat(ctx.message.guild, "RequiredStopRole")
    #     if role == None or role == "":
    #         msg = '**Only Admins** can use stop.'
    #         await ctx.message.channel.send(msg)
    #     else:
    #         # Role is set - let's get its name
    #         found = False
    #         for arole in ctx.message.guild.roles:
    #             if str(arole.id) == str(role):
    #                 found = True
    #                 vowels = "aeiou"
    #                 if arole.name[:1].lower() in vowels:
    #                     msg = 'You need to be an **{}** to use `$stop`.'.format(arole.name)
    #                 else:
    #                     msg = 'You need to be a **{}** to use `$stop`.'.format(arole.name)
                    
    #         if not found:
    #             msg = 'There is no role that matches id: `{}` - consider updating this setting.'.format(role)
    #         # Check for suppress
    #         if suppress:
    #             msg = Nullify.clean(msg)
    #         await ctx.message.channel.send(msg)

        
    # @commands.command(pass_context=True)
    # async def setlinkrole(self, ctx, *, role : str = None):
    #     """Menyetel role yang dibutuhkan untuk menambah/menghapus link list (admin only)."""
        
    #     # Check if we're suppressing @here and @everyone mentions
    #     if self.settings.getServerStat(ctx.message.guild, "SuppressMentions"):
    #         suppress = True
    #     else:
    #         suppress = False

    #     if not await Utils.is_admin_reply(ctx): return

    #     if role == None:
    #         self.settings.setServerStat(ctx.message.guild, "RequiredLinkRole", "")
    #         em = discord.Embed(color=0XFF8C00,
    #                            description="> Penambahan/penghapusan link list sekarang hanya dapat dilakukan oleh *admin server*\n> \n"
    #                                        "> **Panduan penambahan izin link role**\n"
    #                                       "> `{}setlinkrole [role]`\n> \n"
    #                                        "> Berikut adalah izin command yang dapat digunakan oleh link role\n"
    #                                       "> `{}addlink`\n"
    #                                       "> `{}removelink`\n"
    #                                       .format(ctx.prefix,
    #                                               ctx.prefix,
    #                                               ctx.prefix))
    #         em.set_author(name = "Set link role", icon_url = "https://cdn.discordapp.com/attachments/518118753226063887/725569194304733435/photo.jpg")
    #         em.set_footer(text = "Saat mengetik command, tanda [] tidak usah digunakan\nRequest by : {}".format(ctx.author.name), icon_url = "{}".format(ctx.author.avatar_url))
    #         msg = em
    #         await ctx.message.channel.send(embed = msg)
    #         return

    #     if type(role) is str:
    #         if role == "everyone":
    #             role = "@everyone"
    #         roleName = role
    #         role = DisplayName.roleForName(roleName, ctx.message.guild)
    #         if not role:
    #             msg = '┐(￣ヘ￣;)┌\nAku tidak dapat menemukan role *{}*...'.format(roleName)
    #             # Check for suppress
    #             if suppress:
    #                 msg = Nullify.clean(msg)
    #             await ctx.message.channel.send(msg)
    #             return

    #     # If we made it this far - then we can add it
    #     self.settings.setServerStat(ctx.message.guild, "RequiredLinkRole", role.id)

    #     msg = 'Link role telah di tetapkan ke **{}**.'.format(role.name)
    #     # Check for suppress
    #     if suppress:
    #         msg = Nullify.clean(msg)
    #     await ctx.message.channel.send(msg)
        
    
    # @setlinkrole.error
    # async def setlinkrole_error(self, error, ctx):
    #     # do stuff
    #     msg = 'setlinkrole Error: {}'.format(error)
    #     await ctx.channel.send(msg)
        
        
    # @commands.command(pass_context=True)
    # async def sethackrole(self, ctx, *, role : str = None):
    #     """Menyetel role yang dibutuhkan untuk menambahkan/menghapus hack list (admin only)."""
        
    #     # Check if we're suppressing @here and @everyone mentions
    #     if self.settings.getServerStat(ctx.message.guild, "SuppressMentions"):
    #         suppress = True
    #     else:
    #         suppress = False

    #     if not await Utils.is_admin_reply(ctx): return

    #     if role == None:
    #         self.settings.setServerStat(ctx.message.guild, "RequiredHackRole", "")
    #         msg = 'Menambahkan/menghapus hack list hanya dapat dilakukan oleh *admin server*.'
    #         await ctx.message.channel.send(msg)
    #         return

    #     if type(role) is str:
    #         if role == "everyone":
    #             role = "@everyone"
    #         roleName = role
    #         role = DisplayName.roleForName(roleName, ctx.message.guild)
    #         if not role:
    #             msg = '┐(￣ヘ￣;)┌\nAku tidak dapat menemukan role *{}*...'.format(roleName)
    #             # Check for suppress
    #             if suppress:
    #                 msg = Nullify.clean(msg)
    #             await ctx.message.channel.send(msg)
    #             return

    #     # If we made it this far - then we can add it
    #     self.settings.setServerStat(ctx.message.guild, "RequiredHackRole", role.id)

    #     msg = 'Role telah ditetapkan ke **{}**.\nSekarang role tersebut dapat menambahkan/menghapus hack list.'.format(role.name)
    #     # Check for suppress
    #     if suppress:
    #         msg = Nullify.clean(msg)
    #     await ctx.message.channel.send(msg)


    # @sethackrole.error
    # async def hackrole_error(self, error, ctx):
    #     # do stuff
    #     msg = 'sethackrole Error: {}'.format(error)
    #     await ctx.channel.send(msg)


    # @commands.command(pass_context=True)
    # async def settagrole(self, ctx, *, role : str = None):
    #     """Menyetel role ID yang dibutuhkan untuk menambahkan/menghapus tag list (admin only)."""
        
    #     # Check if we're suppressing @here and @everyone mentions
    #     if self.settings.getServerStat(ctx.message.guild, "SuppressMentions"):
    #         suppress = True
    #     else:
    #         suppress = False

    #     if not await Utils.is_admin_reply(ctx): return

    #     if role == None:
    #         self.settings.setServerStat(ctx.message.guild, "RequiredTagRole", "")
    #         msg = 'Menambahkan/menghapus tag list hanya dapat dilakukan oleh *admin-server*.'
    #         await ctx.message.channel.send(msg)
    #         return

    #     if type(role) is str:
    #         if role == "everyone":
    #             role = "@everyone"
    #         roleName = role
    #         role = DisplayName.roleForName(roleName, ctx.message.guild)
    #         if not role:
    #             msg = '┐(￣ヘ￣;)┌\nAku tidak dapat menemukan role *{}*...'.format(roleName)
    #             # Check for suppress
    #             if suppress:
    #                 msg = Nullify.clean(msg)
    #             await ctx.message.channel.send(msg)
    #             return

    #     # If we made it this far - then we can add it
    #     self.settings.setServerStat(ctx.message.guild, "RequiredTagRole", role.id)

    #     msg = 'Role telah ditetapkan ke **{}**.\nSekarang role tersebut dapat menambahkan/menghapus tag list.'.format(role.name)
    #     # Check for suppress
    #     if suppress:
    #         msg = Nullify.clean(msg)
    #     await ctx.message.channel.send(msg)


    # @settagrole.error
    # async def tagrole_error(self, error, ctx):
    #     # do stuff
    #     msg = 'settagrole Error: {}'.format(error)
    #     await ctx.channel.send(msg)
        
        
    @commands.command(pass_context=True)
    async def setrules(self, ctx, *, rules : str = None):
        """**INDONESIA**
        Mengatur rule di server masing-masing.

        **ENGLISH**
        Set the server's rules"""
        LangCheck = self.settings.getUserStat(ctx.message.author, ctx.message.guild, "Language")

        if LangCheck == None:
            # Author belum memilih bahasa
            await self.language_not_set(ctx)

        if not await Utils.is_bot_admin_reply(ctx): return
        
        if rules == None:
            rules = ""
            
        self.settings.setServerStat(ctx.message.guild, "Rules", rules)
        if LangCheck == "ID":
            msg = 'Rule telah ditulis:\n{}'.format(rules)
        if LangCheck == "EN":
            msg = 'Rules now set to:\n{}'.format(rules)
        await ctx.message.channel.send(Utils.suppressed(ctx,msg))
        
        
    @commands.command(pass_context=True)
    async def rawrules(self, ctx):
        """**INDONESIA**
        Menampilkan server rule dalam bentuk markdown.

        **ENGLISH**
        Display the markdown for the server's rules
        (Admin server only)"""
        LangCheck = self.settings.getUserStat(ctx.message.author, ctx.message.guild, "Language")

        if LangCheck == None:
            # Author belum memilih bahasa
            await self.language_not_set(ctx)


        if not await Utils.is_bot_admin_reply(ctx): return
        rules = self.settings.getServerStat(ctx.message.guild, "Rules")
        rules = rules.replace('\\', '\\\\').replace('*', '\\*').replace('`', '\\`').replace('_', '\\_')
        msg = "*{}* Rules (Raw Markdown):\n{}".format(self.suppressed(ctx.guild, ctx.guild.name), rules)
        await ctx.channel.send(msg)
        
        
    @commands.command(pass_context=True)
    async def lock(self, ctx):
        """**INDONESIA**
        Mengunci bot dari member, dan hanya membalas command dari admin server.

        **ENGLISH**
        Toggles whether the bot only responds to admins"""
        LangCheck = self.settings.getUserStat(ctx.message.author, ctx.message.guild, "Language")

        if LangCheck == None:
            # Author belum memilih bahasa
            await self.language_not_set(ctx)

        if not await Utils.is_admin_reply(ctx): return

        isLocked = self.settings.getServerStat(ctx.message.guild, "AdminLock")
        if isLocked:
            if LangCheck == "ID":
                em = discord.Embed(color = 0XFF8C00,
                                   description = "Acinonyx telah di unlock, sekarang aku dapat menerima command dari *semua member*")
                em.set_author(name = "Admin lock off", icon_url = "https://cdn.discordapp.com/attachments/518118753226063887/725569194304733435/photo.jpg")
                em.set_footer(text = "{}".format(ctx.author),
                              icon_url = "{}".format(ctx.author.avatar_url))
            if LangCheck == "EN":
                em = discord.Embed(color = 0XFF8C00,
                                   description = "Acinonyx has unlocked, from now i will reply *everyone* who use the command")
                em.set_author(name = "Admin lock off", icon_url = "https://cdn.discordapp.com/attachments/518118753226063887/725569194304733435/photo.jpg")
                em.set_footer(text = "{}".format(ctx.author),
                              icon_url = "{}".format(ctx.author.avatar_url))
            self.settings.setServerStat(ctx.message.guild, "AdminLock", False)
        else:
            if LangCheck == "ID":
                em = discord.Embed(color = 0XFF8C00,
                                   description = "Acinonyx telah di lock, sekarang aku hanya menerima command dari *admin server*")
                em.set_author(name = "Admin lock on", icon_url = "https://cdn.discordapp.com/attachments/518118753226063887/725569194304733435/photo.jpg")
                em.set_footer(text = "{}".format(ctx.author),
                              icon_url = "{}".format(ctx.author.avatar_url))
            if LangCheck == "EN":
                em = discord.Embed(color = 0XFF8C00,
                                   description = "Acinonyx has been lock, from now i only responds to *admins server*")
                em.set_author(name = "Admin lock on", icon_url = "https://cdn.discordapp.com/attachments/518118753226063887/725569194304733435/photo.jpg")
                em.set_footer(text = "{}".format(ctx.author),
                              icon_url = "{}".format(ctx.author.avatar_url))
            self.settings.setServerStat(ctx.message.guild, "AdminLock", True)
        await ctx.message.channel.send(embed = em)
        
        
    @commands.command(pass_context=True)
    async def addadmin(self, ctx, *, role : str = None):
        """**INDONESIA**
        Menambahkan role baru ke daftar admin bot untuk mengatur bot ini dalam server.

        **ENGLISH**
        Adds a new role to the admin list.
        (Admin server only)"""
        LangCheck = self.settings.getUserStat(ctx.message.author, ctx.message.guild, "Language")

        if LangCheck == None:
            # Author belum memilih bahasa
            await self.language_not_set(ctx)

        if LangCheck == "ID":
            em = discord.Embed(color = 0XFF8C00,
                               description = "> Menambahkan admin ke dalam list bot, role yang dipilih dapat menggunakan command admin untuk mengatur bot ini dalam server\n> \n"
                                             "> **Panduan penggunaan**\n"
                                             "> Ketik `{}addadmin [role]` untuk menambahkan role admin".format(ctx.prefix))
            em.set_footer(text = "Saat mengetik command, tanda [] tidak usah digunakan\n{}".format(ctx.author),
                          icon_url = "{}".format(ctx.author.avatar_url))
        if LangCheck == "EN":
            em = discord.Embed(color = 0XFF8C00,
                               description = "> Adds a new role to the admin list.\n> \n"
                                             "> **Usage**\n"
                                             "> Type `{}addadmin [role]` to add admin role".format(ctx.prefix))
            em.set_footer(text = "When typing commands, you don't need to use the [] sign\n{}".format(ctx.author),
                          icon_url = "{}".format(ctx.author.avatar_url))

        # Periksa pesan apakah Acinonyx akan melakukan suppressing mention @here dan @everyone
        if self.settings.getServerStat(ctx.message.guild, "SuppressMentions"):
            suppress = True
        else:
            suppress = False

        if not await Utils.is_admin_reply(ctx): return

        if role == None:
            await ctx.message.channel.send(embed = em)
            return

        roleName = role
        if type(role) is str:
            if role.lower() == "everyone" or role.lower() == "@everyone":
                role = ctx.guild.default_role
            else:
                role = DisplayName.roleForName(roleName, ctx.guild)
            if not role:
                if LangCheck == "ID":
                    msg = "┐(￣ヘ￣;)┌\nAku tidak dapat menemukan role *{}*...".format(roleName)
                if LangCheck == "EN":
                    msg = "┐(￣ヘ￣;)┌\ni can't find role *{}* in your server...".format(roleName)
                # Check for suppress
                if suppress:
                    msg = Nullify.clean(msg)
                em = discord.Embed(color = 0XFF8C00, description = msg)
                em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                await ctx.message.channel.send(embed = em)
                return

        # Sekarang cek dulu apakah role yang diminta sudah ada dalam database?
        promoArray = self.settings.getServerStat(ctx.message.guild, "AdminArray")

        for aRole in promoArray:
            # Cari role yang diminta berdasarkan id
            if str(aRole['ID']) == str(role.id):
                # Ketemu nih rolenya dalam database
                if LangCheck == "ID":
                    msg = "Role **{}** sudah ada dalam list.".format(role.name)
                if LangCheck == "EN":
                    msg = "**{}** is already in the list.".format(role.name)
                # Cek suppress message
                if suppress:
                    msg = Nullify.clean(msg)
                em = discord.Embed(color = 0XFF8C00, description = msg)
                em.set_footer(text = "{}#{}".format(ctx.author.name, ctx.author.discriminator))
                await ctx.message.channel.send(embed = em)
                return

        # Kalau promoArray diatas tidak ketemu, tambahkan role yang baru kedalam database.
        promoArray.append({ 'ID' : role.id, 'Name' : role.name })
        self.settings.setServerStat(ctx.message.guild, "AdminArray", promoArray)

        if LangCheck == "ID":
            msg = 'Role **{}** telah ditambahkan ke dalam list.'.format(role.name)
        if LangCheck == "EN":
            msg = '**{}** added to list.'.format(role.name)
        # Cek suppress message
        if suppress:
            msg = Nullify.clean(msg)
        em = discord.Embed(color = 0XFF8C00, description = msg)
        em.set_footer(text = "{}#{}".format(ctx.author.name, ctx.author.discriminator))
        await ctx.message.channel.send(embed = em)
        return

    @addadmin.error
    async def addadmin_error(self, error, ctx):
        # addadmin error message
        msg = 'addadmin Error:\n```\n{}\n```'.format(error)
        em = discord.Embed(color = 0XFF8C00, description = msg)
        em.set_footer(text = "{}#{}".format(ctx.author.name, ctx.author.discriminator))
        await ctx.channel.send(embed = em)
        
        
    @commands.command(pass_context=True)
    async def removeadmin(self, ctx, *, role : str = None):
        """**INDONESIA**
        Menghapus role admin dari list.

        **ENGLISH**
        Removes a role from the admin list.
        (Admin server only)"""
        LangCheck = self.settings.getUserStat(ctx.message.author, ctx.message.guild, "Language")

        if LangCheck == None:
            # Author belum memilih bahasa
            await self.language_not_set(ctx)

        if LangCheck == "ID":
            em = discord.Embed(color = 0XFF8C00,
                               description = "> Menghapus admin bot.\n> role yang pilih tidak dapat menggunakan command admin\n> \n"
                                             "> **Panduan**\n"
                                             "> Ketik `{}removeadmin [role]` untuk menghapus role dari list admin bot dalam server\n".format(ctx.prefix))
            em.set_footer(text = "Saat mengetik command, tanda [] tidak usah digunakan\n{}".format(ctx.author.name),
                          icon_url = "{}".format(ctx.author.avatar_url))
        if LangCheck == "EN":
            em = discord.Embed(color = 0XFF8C00,
                               description = "> Removes a role from the admin list.\n"
                                             "> **Usage**\n"
                                             "> Type `{}removeadmin [role]` to remove admin role from my list\n".format(ctx.prefix))
            em.set_footer(text = "When typing commands, you don't need to use the [] sign\n{}".format(ctx.author.name),
                          icon_url = "{}".format(ctx.author.avatar_url))

        # Periksa pesan apakah Acinonyx akan melakukan suppressing mention @here dan @everyone
        if self.settings.getServerStat(ctx.message.guild, "SuppressMentions"):
            suppress = True
        else:
            suppress = False

        if not await Utils.is_admin_reply(ctx): return

        if role == None:
            await ctx.message.channel.send(embed = usage)
            return

        roleName = role
        if type(role) is str:
            if role.lower() == "everyone" or role.lower() == "@everyone":
                role = ctx.guild.default_role
            else:
                role = DisplayName.roleForName(role, ctx.guild)

        # Sekarang cek dulu apakah role yang diminta sudah ada dalam database?
        promoArray = self.settings.getServerStat(ctx.message.guild, "AdminArray")

        for aRole in promoArray:
            # Cek nama rolenya
            if aRole['Name'].lower() == roleName.lower():
                # Kalau ketemu, hapus aja
                promoArray.remove(aRole)
                self.settings.setServerStat(ctx.message.guild, "AdminArray", promoArray)
                if LangCheck == "ID":
                    msg = 'Role **{}** berhasil dihapus dari list.'.format(aRole['Name'])
                if LangCheck == "EN":
                    msg = '**{}** removed successfully.'.format(aRole['Name'])
                # Cek suppress message
                if suppress:
                    msg = Nullify.clean(msg)
                em = discord.Embed(color = 0XFF8C00, description = msg)
                em.set_footer(text = "{}".format(ctx.author))
                await ctx.message.channel.send(embed = em)
                return

            # Cari rolenya berdasarkan nomor ID role
            if role and (str(aRole['ID']) == str(role.id)):
                # Kalau ketemu hapus aja
                promoArray.remove(aRole)
                self.settings.setServerStat(ctx.message.guild, "AdminArray", promoArray)
                if LangCheck == "ID":
                    msg = 'Role **{}** berhasil dihapus dari list'.format(role.name)
                if LangCheck == "EN":
                    msg = '**{}** removed successfully.'.format(role.name)
                # Cek suppress message
                if suppress:
                    msg = Nullify.clean(msg)
                em = discord.Embed(color = 0XFF8C00, description = msg)
                em.set_footer(text = "{}#{}".format(ctx.author.name, ctx.author.discriminator))
                await ctx.message.channel.send(embed = em)
                return

        # Kalau promoArray diatas tidak ketemu, tambahkan role yang baru kedalam database.
        if LangCheck == "ID":
            msg = "┐(￣ヘ￣;)┌\nRole **{}** Tidak ada dalam list.".format(role.name)
        if LangCheck == "EN":
            msg = "┐(￣ヘ￣;)┌\n**{}** not found in list.".format(role.name)
        # Cek suppress message
        if suppress:
            msg = Nullify.clean(msg)
        em = discord.Embed(color = 0XFF8C00, description = msg)
        em.set_footer(text = "{}".format(ctx.author))
        await ctx.message.channel.send(embed = em)

    @removeadmin.error
    async def removeadmin_error(self, error, ctx):
        # removeadmin error
        msg = 'removeadmin Error: {}'.format(error)
        em = discord.Embed(color = 0XFF8C00, description = msg)
        em.set_footer(text = "{}#{}".format(ctx.author.name, ctx.author.discriminator))
        await ctx.channel.send(embed = em)


    # @commands.command(pass_context=True)
    # async def removemotd(self, ctx, *, chan = None):
    #     """Menghapus channel topic dari channel yang dipilih (admin server-only)
    #     Command ini sedang dalam perbaikan!!!."""
        
    #     channel = ctx.message.channel
    #     author  = ctx.message.author
    #     server  = ctx.message.guild

    #     em = discord.Embed(color = 0XFF8C00, description = "> Menghapus channel topic dari channel yang dipilih\n> \n"
    #                                                        "> **Panduan Penggunaan**\n"
    #                                                        "> `{}removemotd [channel]`\n".format(prefix))
    #     em.set_author(name = "Remove channel topic")
    #     em.set_thumbnail(url = "{}".format(ctx.message.guild.icon_url), icon_url = "https://cdn.discordapp.com/attachments/518118753226063887/725569194304733435/photo.jpg")
    #     em.set_footer(text = "Saat mengetik command, tanda [] tidak usah digunakan\nRequest by : {}".format(ctx.author.name), icon_url = "{}".format(ctx.author.avatar_url))
    #     usage = em

    #     # Check if we're suppressing @here and @everyone mentions
    #     if self.settings.getServerStat(ctx.message.guild, "SuppressMentions"):
    #         suppress = True
    #     else:
    #         suppress = False
        
    #     if not await Utils.is_admin_reply(ctx): return
    #     if chan == None:
    #         chan = channel
    #     if type(chan) is str:
    #         try:
    #             chan = discord.utils.get(server.channels, name=chan)
    #         except:
    #             print("Channel tidak ditemukan")
    #             return
    #     # At this point - we should have the necessary stuff
    #     motdArray = self.settings.getServerStat(server, "ChannelMOTD")
    #     for a in motdArray:
    #         # Get the channel that corresponds to the id
    #         if str(a['ID']) == str(chan.id):
    #             # We found it - throw an error message and return
    #             motdArray.remove(a)
    #             self.settings.setServerStat(server, "ChannelMOTD", motdArray)
                
    #             msg = 'Semua message hari ini dari channel *{}* telah dihapus.'.format(channel.name)
    #             em = discord.Embed(color = 0XFF8C00, description = msg)
    #             em.set_footer(text = "{}#{}".format(ctx.author.name, ctx.author.discriminator))
    #             await channel.send(embed = em)
    #             await channel.edit(topic=None)
    #             await self.updateMOTD()
    #             return      
    #     msg = '┐(￣ヘ￣;)┌\nAku tidak dapat menemukan channel *{}*.'.format(chan.name)
    #     # Check for suppress
    #     if suppress:
    #         msg = Nullify.clean(msg)
    #     em = discord.Embed(color = 0XFF8C00, description = msg)
    #     em.set_footer(text = "{}#{}".format(ctx.author.name, ctx.author.discriminator))
    #     await channel.send(embed = em) 
        
    # @removemotd.error
    # async def removemotd_error(self, error, ctx):
    #     # do stuff
    #     msg = 'removemotd Error: {}'.format(error)
    #     em = discord.Embed(color = 0XFF8C00, description = msg)
    #     em.set_footer(text = "{}#{}".format(ctx.author.name, ctx.author.discriminator))
    #     await ctx.channel.send(embed = em)
                

    @commands.command(pass_context=True)
    async def broadcast(self, ctx, *, message : str = None):
        """Broadcasts pesan ke seluruh server yang terhubung dengan bot ini. (Owner bot-only)"""

        channel = ctx.message.channel
        author  = ctx.message.author

        if message == None:
            await channel.send(usage)
            return

        # Only allow owner
        isOwner = self.settings.isOwner(ctx.author)
        if isOwner == None:
            msg = 'Belum ada owner'
            await ctx.channel.send(msg)
            return
        elif isOwner == False:
            msgText = ["Siapa yaa?\nKamu bukan owner ku",
                       "Kamu bukan owner ku!!",
                       "Hus hus, jangan main main sama command ini",
                       "Command ini bahaya loh dek, jangan main main!"]
            msg = random.choice(msgText)
            em = discord.Embed(color = 0XFF8C00, description = msg)
            em.set_footer(text = "{}#{}".format(ctx.author.name, ctx.author.discriminator))
            await ctx.channel.send(embed = em)
            return
        
        for server in self.bot.guilds:
            # Get the default channel
            targetChan = server.get_channel(server.id)
            targetChanID = self.settings.getServerStat(server, "DefaultChannel")
            if len(str(targetChanID)):
                # We *should* have a channel
                tChan = self.bot.get_channel(int(targetChanID))
                if tChan:
                    # We *do* have one
                    targetChan = tChan
            try:
                await targetChan.send(message)
            except Exception:
                pass

        
    # @commands.command(pass_context=True)
    # async def setmotd(self, ctx, message : str = None, chan : discord.TextChannel = None):
    #     """Menulis channel topic dari channel yang dipilih."""
        
    #     channel = ctx.message.channel
    #     author  = ctx.message.author
    #     server  = ctx.message.guild

    #     em = discord.Embed(color = 0XFF8C00, description = "> Menghapus channel topic dari channel yang dipilih\n> \n"
    #                                                        "> **Panduan Penggunaan**\n"
    #                                                        "> `{}removemotd \"[message]\" [channel]`\n"
    #                                                        "> Pastikan kamu menulis message dengan tanda(\")".format(prefix))
    #     em.set_author(name = "Remove message of the day")
    #     em.set_thumbnail(url = "{}".format(ctx.message.guild.icon_url), icon_url = "https://cdn.discordapp.com/attachments/518118753226063887/725569194304733435/photo.jpg")
    #     em.set_footer(text = "Saat mengetik command, tanda [] tidak usah digunakan\nRequest by : {}".format(ctx.author.name), icon_url = "{}".format(ctx.author.avatar_url))
    #     usage = em
        
    #     if not await Utils.is_admin_reply(ctx): return
    #     if not message:
    #         await channel.send(embed = usage)
    #         return  
    #     if not chan:
    #         chan = channel
    #     if type(chan) is str:
    #         try:
    #             chan = discord.utils.get(server.channels, name=chan)
    #         except:
    #             print("┐(￣ヘ￣;)┌\nchannel yang kamu tuju tidak ditemukan")
    #             return

    #     msg = 'MOTD for *{}* added.'.format(chan.name)
    #     await channel.send(msg)
    #     await chan.edit(topic=message)

        
    # @setmotd.error
    # async def setmotd_error(self, error, ctx):
    #     # do stuff
    #     msg = 'setmotd Error: {}'.format(error)
    #     await ctx.channel.send(msg)


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
