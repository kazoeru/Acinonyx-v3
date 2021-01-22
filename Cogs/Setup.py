import asyncio
import discord
from   discord.ext import commands
from   Cogs import Settings
from   Cogs import DisplayName
from   Cogs import Nullify

def setup(bot):
    # Add the bot and deps
    settings = bot.get_cog("Settings")
    bot.add_cog(Setup(bot, settings))

# This is the Uptime module. It keeps track of how long the bot's been up

class Setup(commands.Cog):

    # Init with the bot reference, and a reference to the settings var
    def __init__(self, bot, settings):
        self.bot = bot
        self.settings = settings
        global Utils, DisplayName
        Utils = self.bot.get_cog("Utils")
        DisplayName = self.bot.get_cog("DisplayName")

    def suppressed(self, guild, msg):
        # Check if we're suppressing @here and @everyone mentions
        if self.settings.getServerStat(guild, "SuppressMentions"):
            return Nullify.clean(msg)
        else:
            return msg

    @commands.command(pass_context=True)
    async def setup(self, ctx):
        """Menjalankan setup bot ini dalam server untuk pertama kali (admin-only)."""

        channel = ctx.message.channel
        author  = ctx.message.author
        server  = ctx.message.guild

        if type(channel) == discord.DMChannel:
            msg = '┐(￣ヘ￣;)┌\nKamu harus menggunakan command ini dalam chat server mu.'
            em  = discord.Embed(color = 0XFF8C00, description = msg)
            em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
            await author.send(embed = em)
            return

        '''if not author is server.owner:
            msg = 'The server *owner* needs to set me up.'
            await self.bot.send_message(channel, msg)
            return'''

        # Allow admins to run Setup
        isAdmin = ctx.message.author.permissions_in(ctx.message.channel).administrator
        if not isAdmin:
            checkAdmin = self.settings.getServerStat(ctx.message.guild, "AdminArray")
            for role in ctx.message.author.roles:
                for aRole in checkAdmin:
                    # Get the role that corresponds to the id
                    if str(aRole['ID']) == str(role.id):
                        isAdmin = True
        if not isAdmin:
            msg = '┐(￣ヘ￣;)┌\nKamu tidak memiliki hak untuk menggunakan command ini.'
            em  = discord.Embed(color = 0XFF8C00, description = msg)
            em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
            await ctx.channel.send(embed = em)
            return


        # If we're here, begin the setup

        #############################
        # Role Management:
        #############################
        # 1. Auto role? Yes/no
        #  a. If yes - get role ID (let's move away from position)
        # 2. Use XP? Yes/no
        #  a. If yes:
        #    * how much reserve per hour
        #    * how much xp/reserve to start
        await self.startSetup(ctx)

    # Check for y, n, or skip
    def check(self, msg):
        if not type(msg.channel) == discord.DMChannel:
            return False
        msgStr = msg.content.lower()
        if msgStr.startswith('y'):
            return True
        if msgStr.startswith('n'):
            return True
        if msgStr == 'skip':
            return True
        return False

    def checkRole(self, msg):
        if not type(msg.channel) == discord.DMChannel:
            return False
        return True

    async def startSetup(self, ctx):
        channel = ctx.message.channel
        author  = ctx.message.author
        server  = ctx.message.guild

        em = discord.Embed(color = 0XFF8C00,
                           description = "Hallo nama ku Acinonyx!\n"
                                         "Yuuk kita jalankan setup untuk server mu.\n\n"
                                         "aku akan menyanyakan beberapa pertanyaan dan kamu dapat menjawabnya\n"
                                         "atau kamu bisa menjawab `skip` untuk menggunakan settingan default ku.\n"
                                         "(atau menggunakan setting sebelumnya jika kamu sudah pernah melakukan setting dengan ku).")
        em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
        await author.send(embed=em)
        await self.autoRole(ctx)

    # Set up the auto-role system
    async def autoRole(self, ctx):
        channel = ctx.message.channel
        author  = ctx.message.author
        server  = ctx.message.guild

        defRole = self.settings.getServerStat(server, "DefaultRole")
        verify = int(self.settings.getServerStat(server, "VerificationTime"))

        msg = '**__Auto-Role Management__**:\nMaukah kamu jika aku mengatur untuk auro-role untuk member yang baru saja bergabung?\n(y/n/skip)'
        if defRole:
            auto = 'Auto role telah di setting ke: **{}**.'.format(DisplayName.roleForID(defRole, server))
        else:
            auto = '*dimatikan*.'

        if verify == 0:
            verifyString = 'Tidak ada delay untuk apply.'
        else:
            verifyString = '{} menit delay sebelum apply.'.format(verify)

        msg = '{}\n\n*Pengaturan saat ini adalah* ***{}***\n{}'.format(msg, auto, verifyString)
        em  = discord.Embed(color = 0XFF8C00, description = msg)
        em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
        await author.send(embed = em)
            

        gotIt = False
        while not gotIt:
            def littleCheck(m):
                return author.id == m.author.id and self.check(m)
            try:
                talk = await self.bot.wait_for('message', check=littleCheck, timeout=60)
            except Exception:
                talk = None
                
            if not talk:
                msg = "┐(￣ヘ￣;)┌\n*{}*, Aku kehabisan waktu...\nKetik `{}setup` dalam chat server mu untuk memulai setup kembali.".format(DisplayName.name(author), ctx.prefix)
                em  = discord.Embed(color = 0XFF8C00, description = msg)
                em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                await author.send(embed = em)
                return
            else:
                # We got something
                if talk.content.lower().startswith('y'):
                    await self.autoRoleName(ctx)
                elif talk.content.lower().startswith('n'):
                    self.settings.setServerStat(server, "DefaultRole", None)
                    msg = 'Auto-role *dimatikan.*'
                    em  = discord.Embed(color = 0XFF8C00, description = msg)
                    em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                    await author.send(embed = em)
                    await self.xpSystem(ctx)
                else:
                    # Skipping
                    msg = 'Auto-role tidak ada yang berubah: {}'.format(auto)
                    em  = discord.Embed(color = 0XFF8C00, description = msg)
                    em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                    await author.send(embed = em)
                    await self.xpSystem(ctx)
                gotIt = True

    # Get our default role
    async def autoRoleName(self, ctx):
        channel = ctx.message.channel
        author  = ctx.message.author
        server  = ctx.message.guild

        msg = 'Silahkan masukan nama role untuk mengatur auto-assign:'
        em  = discord.Embed(color = 0XFF8C00, description = msg)
        em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
        await author.send(embed = em)
        gotIt = False
        while not gotIt:
            def littleCheck(m):
                return author.id == m.author.id and self.checkRole(m)
            try:
                talk = await self.bot.wait_for('message', check=littleCheck, timeout=60)
            except Exception:
                talk = None
            if not talk:
                msg = "┐(￣ヘ￣;)┌\n*{}*, Aku kehabisan waktu...\nKetik `{}setup` dalam chat server mu untuk memulai setup kembali..".format(DisplayName.name(author), ctx.prefix)
                em  = discord.Embed(color = 0XFF8C00, description = msg)
                em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                await author.send(embed = em)
                return
            else:
                # We got a response - check if it's a real role
                role = DisplayName.roleForName(talk.content, server)
                if not role:
                    msg = "┐(￣ヘ￣;)┌\nSepertinya aku tidak menemukan role dengan nama **{}** dalam server mu - silahkan coba lagi.".format(talk.content)
                    em  = discord.Embed(color = 0XFF8C00, description = msg)
                    em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                    await author.send(embed = em)
                    continue
                else:
                    # Got a role!
                    msg = "Auto-role telah di set ke **{}**!".format(role.name)
                    em  = discord.Embed(color = 0XFF8C00, description = msg)
                    em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                    await author.send(embed = em)
                    self.settings.setServerStat(server, "DefaultRole", role.id)
                    gotIt = True
        # Let's find out how long to wait for auto role to apply
        verify = int(self.settings.getServerStat(server, "VerificationTime"))
        msg = 'Jika kamu memiliki high security server - atau hanya menginginkan delay sebelum memberikan default role, Aku dapat melakukannya.\nBerapa lama waktu yang dibutuhkan untuk delay sebelum memberikan role kepada member yang baru join? (dalam hitungan menit)\n\n*Pengaturan delay saat ini adalah* ***{} Menit***.'.format(verify)
        em  = discord.Embed(color = 0XFF8C00, description = msg)
        em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
        await author.send(embed = em)
        gotIt = False
        while not gotIt:
            def littleCheck(m):
                return author.id == m.author.id and self.checkRole(m)
            try:
                talk = await self.bot.wait_for('message', check=littleCheck, timeout=60)
            except Exception:
                talk = None
            if not talk:
                msg = "┐(￣ヘ￣;)┌\n*{}*, Aku kehabisan waktu...\nKetik `{}setup` dalam chat server mu untuk memulai setup kembali.".format(DisplayName.name(author), ctx.prefix)
                em  = discord.Embed(color = 0XFF8C00, description = msg)
                em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                await author.send(embed = em)
                return
            else:
                # We got something
                if talk.content.lower() == "skip":
                    await author.send('Waktu delay Auto-role masih sama *{} menit*.'.format(threshold))
                else:
                    try:
                        talkInt = int(talk.content)
                        msg = 'Waktu delay untuk Auto-role sekarang menjadi *{} menit!*'.format(talkInt)
                        em  = discord.Embed(color = 0XFF8C00, description = msg)
                        em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                        await author.send(embed = em)
                        self.settings.setServerStat(server, "VerificationTime", talkInt)
                    except ValueError:
                        msg = 'Waktu delay Auto-role dimasukan dalam bentuk angka - Silahkan coba lagi.'
                        em  = discord.Embed(color = 0XFF8C00, description = msg)
                        em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                        await author.send(embed = em)
                        continue
                gotIt = True
        # Onward
        await self.xpSystem(ctx)

    async def xpSystem(self, ctx):
        channel = ctx.message.channel
        author  = ctx.message.author
        server  = ctx.message.guild

        defXP = self.settings.getServerStat(server, "DefaultXP")
        if defXP == None:
            defXP = 0
        defXPR = self.settings.getServerStat(server, "DefaultXPReserve")
        if defXPR == None:
            defXPR = 10
        hourXP = self.settings.getServerStat(server, "HourlyXP")
        hourXPReal = self.settings.getServerStat(server, "HourlyXPReal")
        messageXP  = self.settings.getServerStat(server, "XPPerMessage")
        messageXPR = self.settings.getServerStat(server, "XPRPerMessage")
        reqOnline = self.settings.getServerStat(server, "RequireOnline")
        reqXP = self.settings.getServerStat(server, "RequiredXPRole")
        suppProm = self.settings.getServerStat(server, "SuppressPromotions")
        suppDem = self.settings.getServerStat(server, "SuppressDemotions")
        if reqXP == None or not len(str(reqXP)):
            reqXP = "Everyone"
        else:
            reqXP = DisplayName.roleForID(reqXP, server)
        adminUnlimited = self.settings.getServerStat(server, "AdminUnlimited")
        xpProm = self.settings.getServerStat(server, "XPPromote")
        xpDem = self.settings.getServerStat(server, "XPDemote")

        msg = '**__XP Management System__**\nAku dapat membantu dengan auto-manage role untuk promote/demote berdasarkan xp yang didapat.\n\nApakah kamu mau menjalankan setup ini?\n(y/n)'
        msg = '{}\n\n__Pengaturan saat ini:__\n\nDefault xp saat bergabung: *{}*\nXp yang dapat disimpan oleh member: *{}*\nPendapatan XP setiap Jam: *{}*\nBatas pendapatan XP setiap jam: *{}*\nPendapatan XP setiap jam pada saat user sedang online: *{}*\nPendapatan XP setiap pesan yang dikirim: *{}*\nBatas limit XP untuk setiap pesan yang dikirim: *{}*\nRole yang dibutuhkan untuk menggunakan XP system: **{}**\nUnlimited XP untuk admin: *{}*\nKenaikan XP Role untuk user berdasarkan XP: *{}*\nPesan kenaikan Role akan dikirim: *{}*\nPenurunan XP Role untuk user berdasarkan XP: *{}*\nPesan penurunan role xp akan dikirim: *{}*'.format(msg, defXP, defXPR, hourXPReal, hourXP, reqOnline, messageXP, messageXPR, reqXP, adminUnlimited, xpProm, suppProm, xpDem, suppDem)
        em  = discord.Embed(color = 0XFF8C00, description = msg)
        em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
        await author.send(embed = em)

        gotIt = False
        while not gotIt:
            def littleCheck(m):
                return author.id == m.author.id and self.check(m)
            try:
                talk = await self.bot.wait_for('message', check=littleCheck, timeout=60)
            except Exception:
                talk = None
            if not talk:
                msg = "┐(￣ヘ￣;)┌\n*{}*, Aku kehabisan waktu...\nKetik `{}setup` dalam chat server mu untuk memulai setup kembali.".format(DisplayName.name(author), ctx.prefix)
                em  = discord.Embed(color = 0XFF8C00, description = msg)
                em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                await author.send(embed = em)
                return
            else:
                # We got something
                if talk.content.lower().startswith('y'):
                    # await self.autoRoleName(ctx)
                    await self.setupXP(ctx)
                elif talk.content.lower().startswith('n'):
                    await self.picThresh(ctx)
                else:
                    # Skipping
                    await self.picThresh(ctx)
                gotIt = True
        # Onward

    async def setupXP(self, ctx):
        channel = ctx.message.channel
        author  = ctx.message.author
        server  = ctx.message.guild

        ##########################################################################################################################
        # Default XP
        defXP = self.settings.getServerStat(server, "DefaultXP")
        if defXP == None:
            defXP = 0
        msg = 'Dibutuhkan berapa banyak xp untuk setiap user dapat bergabung?\n*Pengaturan saat ini adalah* ***{} Xp***.'.format(defXP)
        em  = discord.Embed(color = 0XFF8C00, description = msg)
        em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
        await author.send(embed = em)
        gotIt = False
        while not gotIt:
            def littleCheck(m):
                return author.id == m.author.id and self.checkRole(m)
            try:
                talk = await self.bot.wait_for('message', check=littleCheck, timeout=60)
            except Exception:
                talk = None
            if not talk:
                msg = "┐(￣ヘ￣;)┌\n*{}*, Aku kehabisan waktu...\nKetik `{}setup` dalam chat server mu untuk memulai setup kembali.".format(DisplayName.name(author), ctx.prefix)
                em  = discord.Embed(color = 0XFF8C00, description = msg)
                em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                await author.send(embed = em)
                return
            else:
                # We got something
                if talk.content.lower() == "skip":
                    msg = 'Default xp masih tetap sama, yaitu *{}*.'.format(defXP)
                    em  = discord.Embed(color = 0XFF8C00, description = msg)
                    em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                    await author.send(embed = em)
                    self.settings.setServerStat(server, "DefaultXP", defXP)
                else:
                    try:
                        talkInt = int(talk.content)
                        msg = 'Default xp sekarang *{}!*'.format(talkInt)
                        em  = discord.Embed(color = 0XFF8C00, description = msg)
                        em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                        await author.send(embed = em)
                        self.settings.setServerStat(server, "DefaultXP", talkInt)
                    except ValueError:
                        # await self.autoRoleName(ctx)
                        msg = '┐(￣ヘ￣;)┌\nDefault xp dimasukan dalam bentuk angka - silahkan coba lagi.'
                        em  = discord.Embed(color = 0XFF8C00, description = msg)
                        em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                        await author.send(embed = em)
                        continue
                gotIt = True
        
        ##########################################################################################################################
        # Default XP Reserve
        defXPR = self.settings.getServerStat(server, "DefaultXPReserve")
        if defXPR == None:
            defXPR = 10
        msg = 'Berapa banyak xp yang dapat di simpan user? (setiap user dapat transfer xp, gamble, atau memberi makan bot)\n\n*Pengaturan saat ini adalah* ***{} Xp***.'.format(defXPR)
        em  = discord.Embed(color = 0XFF8C00, description = msg)
        em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
        await author.send(embed = em)
        gotIt = False
        while not gotIt:
            def littleCheck(m):
                return author.id == m.author.id and self.checkRole(m)
            try:
                talk = await self.bot.wait_for('message', check=littleCheck, timeout=60)
            except Exception:
                talk = None
            if not talk:
                msg = "┐(￣ヘ￣;)┌\n*{}*, Aku kehabisan waktu...\nKetik `{}setup` dalam chat server mu untuk memulai setup kembali.".format(DisplayName.name(author), ctx.prefix)
                em  = discord.Embed(color = 0XFF8C00, description = msg)
                em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                await author.send(embed = em)
                return
            else:
                # We got something
                if talk.content.lower() == "skip":
                    msg = 'Default xp untuk simpanan user masih tetap sama, yaitu *{}*.'.format(defXPR)
                    em  = discord.Embed(color = 0XFF8C00, description = msg)
                    em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                    await author.send(embed = em)
                    self.settings.setServerStat(server, "DefaultXPReserve", defXPR)
                else:
                    try:
                        talkInt = int(talk.content)
                        msg = 'Default xp untuk simpanan user adalah *{}!*'.format(talkInt)
                        em  = discord.Embed(color = 0XFF8C00, description = msg)
                        em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                        await author.send(embed = em)
                        self.settings.setServerStat(server, "DefaultXPReserve", talkInt)
                    except ValueError:
                        # await self.autoRoleName(ctx)
                        msg = '┐(￣ヘ￣;)┌\nDefault xp untuk simpanan user dimasukan dalam bentuk angka - silahkan coba lagi.'
                        em  = discord.Embed(color = 0XFF8C00, description = msg)
                        em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                        await author.send(embed = em)
                        continue
                gotIt = True
                
        ##########################################################################################################################
        # Hourly XP
        hourXPReal = self.settings.getServerStat(server, "HourlyXPReal")
        if hourXPReal == None:
            hourXPReal = 0
        msg = 'Berapa banyak xp (xp yang menentukan user role) yang akan didapatkan user setiap jam?\n*Pengaturan saat ini* ***{} Xp***.'.format(hourXPReal)
        em  = discord.Embed(color = 0XFF8C00, description = msg)
        em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
        await author.send(embed = em)
        gotIt = False
        while not gotIt:
            def littleCheck(m):
                return author.id == m.author.id and self.checkRole(m)
            try:
                talk = await self.bot.wait_for('message', check=littleCheck, timeout=60)
            except Exception:
                talk = None
            if not talk:
                msg = "┐(￣ヘ￣;)┌\n*{}*, Aku kehabisan waktu...\nKetik `{}setup` dalam chat server mu untuk memulai setup kembali.".format(DisplayName.name(author), ctx.prefix)
                em  = discord.Embed(color = 0XFF8C00, description = msg)
                em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                await author.send(embed = em)
                return
            else:
                # We got something
                if talk.content.lower() == "skip":
                    msg = 'Pendapatan xp setiap jam masih sama, yaitu *{}*.'.format(hourXPReal)
                    em  = discord.Embed(color = 0XFF8C00, description = msg)
                    em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                    await author.send(embed = em)
                    self.settings.setServerStat(server, "HourlyXPReal", hourXPReal)
                else:
                    try:
                        talkInt = int(talk.content)
                        msg = 'Pendapatan xp setiap jam sekarang *{}!*'.format(talkInt)
                        em  = discord.Embed(color = 0XFF8C00, description = msg)
                        em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                        await author.send(embed = em)
                        self.settings.setServerStat(server, "HourlyXPReal", talkInt)
                    except ValueError:
                        # await self.autoRoleName(ctx)
                        msg = '┐(￣ヘ￣;)┌\nPendapatan xp setiap jam dimasukan dalam bentuk angka - silahkan coba lagi.'
                        em  = discord.Embed(color = 0XFF8C00, description = msg)
                        em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                        await author.send(embed = em)
                        continue
                gotIt = True
        
        ##########################################################################################################################
        # Hourly XP Reserve
        hourXP = self.settings.getServerStat(server, "HourlyXP")
        if hourXP == None:
            hourXP = 3
        msg = 'Berapa banyak limit untuk pendapatan xp setiap jam yang dapat di simpan user? (setiap user dapat transfer xp, gamble, atau memberi makan bot)\n\n*Pengaturan saat ini adalah* ***{} Xp***.'.format(hourXP)
        em  = discord.Embed(color = 0XFF8C00, description = msg)
        em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
        await author.send(embed = em)
        gotIt = False
        while not gotIt:
            def littleCheck(m):
                return author.id == m.author.id and self.checkRole(m)
            try:
                talk = await self.bot.wait_for('message', check=littleCheck, timeout=60)
            except Exception:
                talk = None
            if not talk:
                msg = "┐(￣ヘ￣;)┌\n*{}*, Aku kehabisan waktu...\nKetik `{}setup` dalam chat server mu untuk memulai setup kembali.".format(DisplayName.name(author), ctx.prefix)
                em  = discord.Embed(color = 0XFF8C00, description = msg)
                em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                await author.send(embed = em)
                return
            else:
                # We got something
                if talk.content.lower() == "skip":
                    msg = 'Limit pendapatan xp setiap jam yang dapat disimpan user masih tetap *{} Xp*.'.format(hourXP)
                    em  = discord.Embed(color = 0XFF8C00, description = msg)
                    em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                    await author.send(embed = em)
                    self.settings.setServerStat(server, "HourlyXP", hourXP)
                else:
                    try:
                        talkInt = int(talk.content)
                        msg = 'Limit pendapatan xp setiap jam yang dapat disimpan user adalah *{}!*'.format(talkInt)
                        em  = discord.Embed(color = 0XFF8C00, description = msg)
                        em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                        await author.send(embed = em)
                        self.settings.setServerStat(server, "HourlyXP", talkInt)
                    except ValueError:
                        # await self.autoRoleName(ctx)
                        msg = '┐(￣ヘ￣;)┌\nPendapatan xp setiap jam yang dapat disimpan user harus dimasukan dalam bentuk angka - silahkan coba lagi.'
                        em  = discord.Embed(color = 0XFF8C00, description = msg)
                        em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                        await author.send(embed = em)
                        continue
                gotIt = True

        ##########################################################################################################################
        # Required Online
        reqOnline = self.settings.getServerStat(server, "RequireOnline")
        msg = 'Apakah kamu ingin aku mengharuskan user berada pada status *online* untuk mendapatkan xp setiap jam? (y/n)\n*Pengaturan saat ini* ***{}***.'.format(reqOnline)
        em  = discord.Embed(color = 0XFF8C00, description = msg)
        em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
        await author.send(embed = em)
        gotIt = False
        while not gotIt:
            def littleCheck(m):
                return author.id == m.author.id and self.check(m)
            try:
                talk = await self.bot.wait_for('message', check=littleCheck, timeout=60)
            except Exception:
                talk = None
            if not talk:
                msg = "┐(￣ヘ￣;)┌\n*{}*, Aku kehabisan waktu...\nKetik `{}setup` dalam chat server mu untuk memulai setup kembali.".format(DisplayName.name(author), ctx.prefix)
                em  = discord.Embed(color = 0XFF8C00, description = msg)
                em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                await author.send(embed = em)
                return
            else:
                # We got something
                if talk.content.lower().startswith('y'):
                    self.settings.setServerStat(server, "RequireOnline", True)
                    msg = 'Status online saat ini *Yes.*'
                    em  = discord.Embed(color = 0XFF8C00, description = msg)
                    em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                    await author.send(embed = em)
                
                elif talk.content.lower().startswith('n'):
                    msg = 'Status online telah di setting ke *No.*'
                    em  = discord.Embed(color = 0XFF8C00, description = msg)
                    em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                    self.settings.setServerStat(server, "RequireOnline", False)
                    await author.send(embed = em)
                
                else:
                    # Skipping
                    msg = 'Status online akan tetap *{}*'.format(reqOnline)
                    em  = discord.Embed(color = 0XFF8C00, description = msg)
                    em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                    await author.send(embed = em)
                gotIt = True
                
        ##########################################################################################################################
        # XP Per Message
        messageXP = self.settings.getServerStat(server, "XPPerMessage")
        if messageXP == None:
            messageXP = 0
        msg = 'Berapa banyak xp (xp yang menentukan user role) yang akan didapatkan setiap user saat mereka mengirim pesan dalam server mu?\n\nPengaturan saat ini adalah* ***{} Xp***.'.format(messageXP)
        em  = discord.Embed(color = 0XFF8C00, description = msg)
        em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
        await author.send(embed = em)
        gotIt = False
        while not gotIt:
            def littleCheck(m):
                return author.id == m.author.id and self.checkRole(m)
            try:
                talk = await self.bot.wait_for('message', check=littleCheck, timeout=60)
            except Exception:
                talk = None
            if not talk:
                msg = "┐(￣ヘ￣;)┌\n*{}*, Aku kehabisan waktu...\nKetik `{}setup` dalam chat server mu untuk memulai setup kembali.".format(DisplayName.name(author), ctx.prefix)
                em  = discord.Embed(color = 0XFF8C00, description = msg)
                em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                await author.send(embed = em)
                return
            else:
                # We got something
                if talk.content.lower() == "skip":
                    msg = 'Pendapatan xp untuk setiap user saat mengirim pesan masih tetap sama *{} Xp*.'.format(messageXP)
                    em  = discord.Embed(color = 0XFF8C00, description = msg)
                    em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                    await author.send(embed = em)
                    self.settings.setServerStat(server, "XPPerMessage", messageXP)
                else:
                    try:
                        talkInt = int(talk.content)
                        msg = 'Pendapatan xp untuk setiap user saat mengirim pesan saat ini adalah *{} Xp!*'.format(talkInt)
                        em  = discord.Embed(color = 0XFF8C00, description = msg)
                        em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                        await author.send(embed = em)
                        self.settings.setServerStat(server, "XPPerMessage", talkInt)
                    except ValueError:
                        # await self.autoRoleName(ctx)
                        msg = '┐(￣ヘ￣;)┌\nPendapatan xp untuk setiap mengirim pesan dimasukan dalam bentuk angka - silahkan coba lagi.'
                        em  = discord.Embed(color = 0XFF8C00, description = msg)
                        em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                        await author.send(embed = em)
                        continue
                gotIt = True
                
        ##########################################################################################################################
        # XP Reserve Per Message
        messageXPR = self.settings.getServerStat(server, "XPRPerMessage")
        if messageXPR == None:
            messageXPR = 0
        msg = 'Berapa limit xp yang dapat diperoleh user setiap mereka mengirim pesan? (setiap xp user dapat transfer xp, gamble, atau memberi makan bot)\n\n*Pengaturan saat ini adalah* ***{} Xp***.'.format(messageXPR)
        em  = discord.Embed(color = 0XFF8C00, description = msg)
        em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
        await author.send(embed = em)
        gotIt = False
        while not gotIt:
            def littleCheck(m):
                return author.id == m.author.id and self.checkRole(m)
            try:
                talk = await self.bot.wait_for('message', check=littleCheck, timeout=60)
            except Exception:
                talk = None
            if not talk:
                msg = "┐(￣ヘ￣;)┌\n*{}*, Aku kehabisan waktu...\nKetik `{}setup` dalam chat server mu untuk memulai setup kembali.".format(DisplayName.name(author), ctx.prefix)
                em  = discord.Embed(color = 0XFF8C00, description = msg)
                em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                await author.send(embed = em)
                return
            else:
                # We got something
                if talk.content.lower() == "skip":
                    msg = 'Limit pendapatan xp user setiap mengirim pesan masih tetap sama *{} Xp*.'.format(messageXPR)
                    em  = discord.Embed(color = 0XFF8C00, description = msg)
                    em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                    await author.send(embed = em)
                    self.settings.setServerStat(server, "XPRPerMessage", messageXPR)
                else:
                    try:
                        talkInt = int(talk.content)
                        msg = 'Limit pendapatan xp user setiap mengirim pesan saat ini adalah *{}!*'.format(talkInt)
                        em  = discord.Embed(color = 0XFF8C00, description = msg)
                        em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                        await author.send(embed = em)
                        self.settings.setServerStat(server, "XPRPerMessage", talkInt)
                    except ValueError:
                        # await self.autoRoleName(ctx)
                        msg = '┐(￣ヘ￣;)┌\nLimit pendapatan xp user harus dimasukan dalam bentuk angka - Silahkan coba lagi.'
                        em  = discord.Embed(color = 0XFF8C00, description = msg)
                        em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                        await author.send(embed = em)
                        continue
                gotIt = True
        
        ##########################################################################################################################
        # Required Role for XP
        reqXP = self.settings.getServerStat(server, "RequiredXPRole")
        if reqXP == None or not len(str(reqXP)):
            reqXP = "Everyone"
        else:
            reqXP = DisplayName.roleForID(reqXP, server)
        msg = 'Role minimum yang dibutuhkan untuk setiap user menggunakan xp system? (ketik `everyone` untuk memberikan akses ke semua member)\n\nSaat ini adalah **{}**.'.format(reqXP)
        em  = discord.Embed(color = 0XFF8C00, description = msg)
        em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
        await author.send(embed = em)
        gotIt = False
        while not gotIt:
            def littleCheck(m):
                return author.id == m.author.id and self.checkRole(m)
            try:
                talk = await self.bot.wait_for('message', check=littleCheck, timeout=60)
            except Exception:
                talk = None
            if not talk:
                msg = "┐(￣ヘ￣;)┌\n*{}*, Aku kehabisan waktu...\nKetik `{}setup` dalam chat server mu untuk memulai setup kembali.".format(DisplayName.name(author), ctx.prefix)
                em  = discord.Embed(color = 0XFF8C00, description = msg)
                em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                await author.send(embed = em)
                return
            else:
                # We got something
                if talk.content.lower() == "skip":
                    msg = 'XP role minimum saat ini adalah **{}**.'.format(reqXP)
                    em  = discord.Embed(color = 0XFF8C00, description = msg)
                    em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                    await author.send(embed = em)
                elif talk.content.lower() == "everyone":
                    self.settings.setServerStat(server, "RequiredXPRole", None)
                    msg = 'XP role minimum saat ini adalah **Everyone**.'
                    em  = discord.Embed(color = 0XFF8C00, description = msg)
                    em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                    await author.send(embed = em)
                else:
                    role = DisplayName.roleForName(talk.content, server)
                    if not role:
                        msg = "┐(￣ヘ￣;)┌\nSepertinya aku tidapat menemukan role **{}** dalam server mu - Silahkan coba lagi.".format(talk.content)
                        em  = discord.Embed(color = 0XFF8C00, description = msg)
                        em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                        await author.send(embed = em)
                        continue
                    else:
                        self.settings.setServerStat(server, "RequiredXPRole", role.id)
                        msg = '┐(￣ヘ￣;)┌Minimum xp role set to **{}**.'.format(role.name)
                        em  = discord.Embed(color = 0XFF8C00, description = msg)
                        em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                        await author.send(embed = em)
                gotIt = True

        ##########################################################################################################################
        # Admin Unlimited
        adminUnlimited = self.settings.getServerStat(server, "AdminUnlimited")
        msg = 'Apakah kamu menginginkan Admin memiliki limit xp yang tidak terbatas? (y/n)\n\nSaat ini adalah *{}*.'.format(adminUnlimited)
        em  = discord.Embed(color = 0XFF8C00, description = msg)
        em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
        await author.send(embed = em)
        gotIt = False
        while not gotIt:
            def littleCheck(m):
                return author.id == m.author.id and self.check(m)
            try:
                talk = await self.bot.wait_for('message', check=littleCheck, timeout=60)
            except Exception:
                talk = None
            if not talk:
                msg = "┐(￣ヘ￣;)┌\n*{}*, Aku kehabisan waktu...\nKetik `{}setup` dalam chat server mu untuk memulai setup kembali.".format(DisplayName.name(author), ctx.prefix)
                em  = discord.Embed(color = 0XFF8C00, description = msg)
                em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                await author.send(embed = em)
                return
            else:
                # We got something
                if talk.content.lower().startswith('y'):
                    self.settings.setServerStat(server, "AdminUnlimited", True)
                    msg = 'Tidak ada batasan limit untuk admin saat ini *Yes.*'
                    em  = discord.Embed(color = 0XFF8C00, description = msg)
                    em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                    await author.send(embed = em)
                elif talk.content.lower().startswith('n'):
                    self.settings.setServerStat(server, "AdminUnlimited", False)
                    msg = 'Tidak ada batasan limit untuk admin saat ini *No.*'
                    em  = discord.Embed(color = 0XFF8C00, description = msg)
                    em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                    await author.send(embed = em)
                else:
                    # Skipping
                    msg = 'Tidak ada batasan limit untuk admin saat ini masih tetap sama *{}*'.format(adminUnlimited)
                    em  = discord.Embed(color = 0XFF8C00, description = msg)
                    em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                    await author.send(embed = em)
                gotIt = True

        ##########################################################################################################################
        # Auto Promote
        xpProm = self.settings.getServerStat(server, "XPPromote")
        msg = 'Apakah kamu menginginkan ku untuk menaikan user xp role secara otomatis berdasarkan xp? (y/n)\n\nKamu dapat menentukan role mana yang dapat dipromote - dan persyaratan xp mereka.\n\n*Pengaturan saat ini adalah* ***{}***.'.format(xpProm)
        em  = discord.Embed(color = 0XFF8C00, description = msg)
        em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
        await author.send(embed = em)
        gotIt = False
        while not gotIt:
            def littleCheck(m):
                return author.id == m.author.id and self.check(m)
            try:
                talk = await self.bot.wait_for('message', check=littleCheck, timeout=60)
            except Exception:
                talk = None
            if not talk:
                msg = "┐(￣ヘ￣;)┌\n*{}*, Aku kehabisan waktu...\nKetik `{}setup` dalam chat server mu untuk memulai setup kembali.".format(DisplayName.name(author), ctx.prefix)
                em  = discord.Embed(color = 0XFF8C00, description = msg)
                em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                await author.send(embed = em)
                return
            else:
                # We got something
                if talk.content.lower().startswith('y'):
                    self.settings.setServerStat(server, "XPPromote", True)
                    msg = 'XP promote saat ini telah di set ke *Yes.*'
                    em  = discord.Embed(color = 0XFF8C00, description = msg)
                    em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                    await author.send(embed = em)
                elif talk.content.lower().startswith('n'):
                    self.settings.setServerStat(server, "XPPromote", False)
                    msg = 'XP promote saat ini telah di set ke *No.*'
                    em  = discord.Embed(color = 0XFF8C00, description = msg)
                    em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                    await author.send(embed = em)
                else:
                    # Skipping
                    msg = 'XP promote saat ini masih tetap sama *{}*'.format(xpProm)
                    em  = discord.Embed(color = 0XFF8C00, description = msg)
                    em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                    await author.send(embed = em)
                gotIt = True
                
        ##########################################################################################################################
        # Suppress Promote Message?
        suppProm = self.settings.getServerStat(server, "SuppressPromotions")
        msg = 'Apakah kamu ingin aku untuk tidak mengirimkan pesan ketika user mendapatkan kenaikan XpRole? (y/n)\n\n*Pengaturan saat ini adalah* ***{}***.'.format(suppProm)
        em  = discord.Embed(color = 0XFF8C00, description = msg)
        em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
        await author.send(embed = em)
        gotIt = False
        while not gotIt:
            def littleCheck(m):
                return author.id == m.author.id and self.check(m)
            try:
                talk = await self.bot.wait_for('message', check=littleCheck, timeout=60)
            except Exception:
                talk = None
            if not talk:
                msg = "┐(￣ヘ￣;)┌\n*{}*, Aku kehabisan waktu...\nKetik `{}setup` dalam chat server mu untuk memulai setup kembali.".format(DisplayName.name(author), ctx.prefix)
                em  = discord.Embed(color = 0XFF8C00, description = msg)
                em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                await author.send(embed = em)
                return
            else:
                # We got something
                if talk.content.lower().startswith('y'):
                    self.settings.setServerStat(server, "SuppressPromotions", True)
                    msg = 'Aku tidak akan mengimkan pesan promote'
                    em  = discord.Embed(color = 0XFF8C00, description = msg)
                    em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                    await author.send(embed = em)
                elif talk.content.lower().startswith('n'):
                    self.settings.setServerStat(server, "SuppressPromotions", False)
                    msg = 'Aku akan mengimkan pesan saat ada user yang mendapatkan kenaikan XpRole.'
                    em  = discord.Embed(color = 0XFF8C00, description = msg)
                    em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                    await author.send(embed = em)
                else:
                    # Skipping
                    msg = 'Pesan kenaikan XpRole masih tetap sama *{}*'.format(suppProm)
                    em  = discord.Embed(color = 0XFF8C00, description = msg)
                    em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                    await author.send(embed = em)
                gotIt = True

        ##########################################################################################################################
        # Auto Demote
        xpDem = self.settings.getServerStat(server, "XPDemote")
        msg = 'Apakah kamu menginginkan aku menurunkan user role secara otomatis berdasarkan xp? (y/n)\n\nKamu dapat menentukan role mana yang dapat didemote - dan persyaratan xp mereka.\n\n*Pengaturan saat ini* ***{}***.'.format(xpDem)
        em  = discord.Embed(color = 0XFF8C00, description = msg)
        em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
        await author.send(embed = em)
        gotIt = False
        while not gotIt:
            def littleCheck(m):
                return author.id == m.author.id and self.check(m)
            try:
                talk = await self.bot.wait_for('message', check=littleCheck, timeout=60)
            except Exception:
                talk = None
            if not talk:
                msg = "┐(￣ヘ￣;)┌\n*{}*, Aku kehabisan waktu...\nKetik `{}setup` dalam chat server mu untuk memulai setup kembali.".format(DisplayName.name(author), ctx.prefix)
                em  = discord.Embed(color = 0XFF8C00, description = msg)
                em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                await author.send(embed = em)
                return
            else:
                # We got something
                if talk.content.lower().startswith('y'):
                    self.settings.setServerStat(server, "XPDemote", True)
                    msg = 'XP demote telah di set ke *Yes.*'
                    em  = discord.Embed(color = 0XFF8C00, description = msg)
                    em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                    await author.send(embed = em)
                elif talk.content.lower().startswith('n'):
                    self.settings.setServerStat(server, "XPDemote", False)
                    msg = 'XP demote telah di set ke *No.*'
                    em  = discord.Embed(color = 0XFF8C00, description = msg)
                    em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                    await author.send(embed = em)
                else:
                    # Skipping
                    msg = 'XP demote masih tetap sama *{}*'.format(xpDem)
                    em  = discord.Embed(color = 0XFF8C00, description = msg)
                    em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                    await author.send(embed = em)
                gotIt = True
                
        ##########################################################################################################################
        # Suppress Demote Message?
        suppDem = self.settings.getServerStat(server, "SuppressDemotions")
        msg = 'Apakah kamu menginginkan ku untuk tidak mengirim pesan saat user diturunkan rolenya? (y/n)\n\nSaat ini adalah *{}*.'.format(suppDem)
        em  = discord.Embed(color = 0XFF8C00, description = msg)
        em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
        await author.send(embed = em)
        gotIt = False
        while not gotIt:
            def littleCheck(m):
                return author.id == m.author.id and self.check(m)
            try:
                talk = await self.bot.wait_for('message', check=littleCheck, timeout=60)
            except Exception:
                talk = None
            if not talk:
                msg = "┐(￣ヘ￣;)┌\n*{}*, Aku kehabisan waktu...\nKetik `{}setup` dalam chat server mu untuk memulai setup kembali.".format(DisplayName.name(author), ctx.prefix)
                em  = discord.Embed(color = 0XFF8C00, description = msg)
                em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                await author.send(embed = em)
                return
            else:
                # We got something
                if talk.content.lower().startswith('y'):
                    self.settings.setServerStat(server, "SuppressDemotions", True)
                    msg = 'Aku tidak akan mengirimkan pesan saat user diturunkan role xpnya.'
                    em  = discord.Embed(color = 0XFF8C00, description = msg)
                    em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                    await author.send(embed = em)
                elif talk.content.lower().startswith('n'):
                    self.settings.setServerStat(server, "SuppressDemotions", False)
                    msg = 'Aku akan mengirimkan pesan saat user diturunkan role xpnya.'
                    em  = discord.Embed(color = 0XFF8C00, description = msg)
                    em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                    await author.send(embed = em)
                else:
                    # Skipping
                    msg = 'Pesan penurunan xp role masih sama *{}*'.format(suppDem)
                    em  = discord.Embed(color = 0XFF8C00, description = msg)
                    em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                    await author.send(embed = em)
                gotIt = True

        ##########################################################################################################################
        # XP Roles
        # Recheck xpProm and xpDem
        xpProm = self.settings.getServerStat(server, "XPPromote")
        xpDem = self.settings.getServerStat(server, "XPDemote")
        if xpProm or xpDem:
            msg = 'Untuk mengatur kenaikan/penurunan xp role - Kamu dapat mengetik `{}addxprole [role] [xp_yang_dibutuhkan]` untuk menambah role baru dalam server mu.\nDan `{}removexprole [role]` untuk menghapus role xp.\nCommand ini digunakan dalam server mu.'.format(ctx.prefix, ctx.prefix)
            em  = discord.Embed(color = 0XFF8C00, description = msg)
            em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
            await author.send(embed = em)

        await self.picThresh(ctx)


    async def picThresh(self, ctx):
        channel = ctx.message.channel
        author  = ctx.message.author
        server  = ctx.message.guild

        threshold = self.settings.getServerStat(server, "PictureThreshold")

        msg = 'Sebagai tindakan Anti-spam, Aku memiliki system cooldown untuk setiap gambar yang dapat saya tampilkan.\n Kamu menginginkan delay cooldown ini berapa lama? (dalam hitungan detik)?\n\n*Pengaturan saat ini adalah* ***{}***.'.format(threshold)
        em  = discord.Embed(color = 0XFF8C00, description = msg)
        em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
        await author.send(embed = em)
        gotIt = False
        while not gotIt:
            def littleCheck(m):
                return author.id == m.author.id and self.checkRole(m)
            try:
                talk = await self.bot.wait_for('message', check=littleCheck, timeout=60)
            except Exception:
                talk = None
            if not talk:
                msg = "┐(￣ヘ￣;)┌\n*{}*, Aku kehabisan waktu...\nKetik `{}setup` dalam chat server mu untuk memulai setup kembali.".format(DisplayName.name(author), ctx.prefix)
                em  = discord.Embed(color = 0XFF8C00, description = msg)
                em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                await author.send(embed = em)
                return
            else:
                # We got something
                if talk.content.lower() == "skip":
                    msg = 'Cooldown Anti-spam gambar masih tetap sama *{}*.'.format(threshold)
                    em  = discord.Embed(color = 0XFF8C00, description = msg)
                    em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                    await author.send(embed = em)
                else:
                    try:
                        talkInt = int(talk.content)
                        msg = 'Cooldown Anti-spam gambar masih saat ini adalah *{}!*'.format(talkInt)
                        em  = discord.Embed(color = 0XFF8C00, description = msg)
                        em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                        await author.send(embed = em)
                        self.settings.setServerStat(server, "PictureThreshold", talkInt)
                    except ValueError:
                        # await self.autoRoleName(ctx)
                        msg = 'Cooldown Anti-spam gambar dimasukan dalam bentuk angka - Silahkan coba lagi.'
                        em  = discord.Embed(color = 0XFF8C00, description = msg)
                        em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                        await author.send(embed = em)
                        continue
                gotIt = True
        await self.hungerLock(ctx)

    async def hungerLock(self, ctx):
        channel = ctx.message.channel
        author  = ctx.message.author
        server  = ctx.message.guild

        hLock = self.settings.getServerStat(server, "HungerLock")
        msg = 'Apakah kamu menginginkan ku mengabaikan user saat aku kelaparan? (Aku *Selalu* Mengikuti apa kata admin) (y/n)\n\nSaat ini adalah *{}*.'.format(hLock)
        em  = discord.Embed(color = 0XFF8C00, description = msg)
        em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
        await author.send(embed = em)
        gotIt = False
        while not gotIt:
            def littleCheck(m):
                return author.id == m.author.id and self.check(m)
            try:
                talk = await self.bot.wait_for('message', check=littleCheck, timeout=60)
            except Exception:
                talk = None
            if not talk:
                msg = "┐(￣ヘ￣;)┌\n*{}*, Aku kehabisan waktu...\nKetik `{}setup` dalam chat server mu untuk memulai setup kembali.".format(DisplayName.name(author), ctx.prefix)
                em  = discord.Embed(color = 0XFF8C00, description = msg)
                em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                await author.send(embed = em)
                return
            else:
                # We got something
                if talk.content.lower().startswith('y'):
                    self.settings.setServerStat(server, "HungerLock", True)
                    msg = 'Pengingat tingkat kelaparan bot telah di set ke *Yes.*'
                    em  = discord.Embed(color = 0XFF8C00, description = msg)
                    em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                    await author.send(embed = em)
                elif talk.content.lower().startswith('n'):
                    self.settings.setServerStat(server, "HungerLock", False)
                    msg = 'Pengingat tingkat kelaparan bot telah di set ke *No.*'
                    em  = discord.Embed(color = 0XFF8C00, description = msg)
                    em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                    await author.send(embed = em)
                else:
                    # Skipping
                    msg = 'Pengingat tingkat kelaparan bot masih tetap sama *{}*'.format(hLock)
                    em  = discord.Embed(color = 0XFF8C00, description = msg)
                    em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                    await author.send(emebd = em)
                gotIt = True
        await self.suppress(ctx)


    # async def defVolume(self, ctx):
    #     channel = ctx.message.channel
    #     author  = ctx.message.author
    #     server  = ctx.message.guild

    #     dVol = float(self.settings.getServerStat(server, "DefaultVolume"))
    #     if dVol == None:
    #         dVol = 0.6
    #     msg = 'What would you like the default volume of the music player to be? (values can be 1-100)\n\nCurrent is *{}*.'.format(int(dVol*100))
    #     await author.send(msg)
    #     gotIt = False
    #     while not gotIt:
    #         def littleCheck(m):
    #             return author.id == m.author.id and self.checkRole(m)
    #         try:
    #             talk = await self.bot.wait_for('message', check=littleCheck, timeout=60)
    #         except Exception:
    #             talk = None
    #         if not talk:
    #             msg = "┐(￣ヘ￣;)┌\n*{}*, Aku kehabisan waktu...\nKetik `{}setup` dalam chat server mu untuk memulai setup kembali.".format(DisplayName.name(author), ctx.prefix)
    #             await author.send(msg)
    #             return
    #         else:
    #             if talk.content.lower() == "skip":
    #                 await author.send('Default volume will remain *{}*.'.format(int(dVol*100)))
    #             else:
    #                 try:
    #                     talkInt = int(talk.content)
    #                     if talkInt > 100:
    #                         talkInt = 100
    #                     if talkInt < 1:
    #                         talkInt = 1
    #                     await author.send('Default volume is now *{}!*'.format(talkInt))
    #                     self.settings.setServerStat(server, "DefaultVolume", (talkInt/100))
    #                 except ValueError:
    #                     # await self.autoRoleName(ctx)
    #                     await author.send('Default volume needs to be a whole number - try again.')
    #                     continue
    #             gotIt = True

    #     await self.suppress(ctx)


    async def suppress(self, ctx):
        channel = ctx.message.channel
        author  = ctx.message.author
        server  = ctx.message.guild

        hLock = self.settings.getServerStat(server, "SuppressMentions")
        msg = 'Apakah kamu menginginkan ku untuk melakukan mention @everyone dan @here dalam output command ku? (y/n)\n\n*Pengaturan saat ini adalah* ***{}***.'.format(hLock)
        em  = discord.Embed(color = 0XFF8C00, description = msg)
        em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
        await author.send(embed = em)
        gotIt = False
        while not gotIt:
            def littleCheck(m):
                return author.id == m.author.id and self.check(m)
            try:
                talk = await self.bot.wait_for('message', check=littleCheck, timeout=60)
            except Exception:
                talk = None
            if not talk:
                msg = "┐(￣ヘ￣;)┌\n*{}*, Aku kehabisan waktu...\nKetik `{}setup` dalam chat server mu untuk memulai setup kembali.".format(DisplayName.name(author), ctx.prefix)
                em  = discord.Embed(color = 0XFF8C00, description = msg)
                em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                await author.send(embed = em)
                return
            else:
                # We got something
                if talk.content.lower().startswith('y'):
                    self.settings.setServerStat(server, "SuppressMentions", True)
                    msg = 'Aku *akan* mention menggunakan @​everyone dan @​here.'
                    em  = discord.Embed(color = 0XFF8C00, description = msg)
                    em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                    await author.send(embed = em)
                elif talk.content.lower().startswith('n'):
                    self.settings.setServerStat(server, "SuppressMentions", False)
                    msg = 'Aku *tidak akan* mention menggunakan @​everyone dan @​here mentions.'
                    em  = discord.Embed(color = 0XFF8C00, description = msg)
                    em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                    await author.send(embed = em)
                else:
                    # Skipping
                    msg = 'Mention @​everyone dan @​here masih tetap sama *{}*'.format(hLock)
                    em  = discord.Embed(color = 0XFF8C00, description = msg)
                    em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
                    await author.send(embed = em)
                gotIt = True
        await self.setupComplete(ctx)

    async def setupComplete(self, ctx):
        channel = ctx.message.channel
        author  = ctx.message.author
        server  = ctx.message.guild

        msg = '__Setup Status untuk *{}*:__\n\n**COMPLETE**\n\nTerima kasih, *{}*, untuk meluangkan waktu mu untuk ku, dan menyiapkan berbagai hal untuk server mu.\nJika kamu tertarik untuk menjelajahi fitur ku yang lainnya, Jangan ragu untuk melihat semuanya dengan `{}help`.\n\nDan juga, Aku akan berusaha menjadi admin yang terbaik untuk server mu.\n\nTerima Kasih!'.format(self.suppressed(server, server.name), DisplayName.name(author), ctx.prefix)
        em  = discord.Embed(color = 0XFF8C00, description = msg)
        em.set_footer(text = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar_url))
        await author.send(embed = em)

# Calling a bot command:  await self.setup.callback(self, ctx)
