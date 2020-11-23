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
        """Runs first-time setup (server owner only)."""

        channel = ctx.message.channel
        author  = ctx.message.author
        server  = ctx.message.guild

        if type(channel) == discord.DMChannel:
            msg = '┐(￣ヘ￣;)┌\nKamu haru menggunakan command ini dalam chat server mu.'
            await author.send(msg)
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
            await ctx.channel.send('┐(￣ヘ￣;)┌\nKamu tidak memiliki hak untuk menggunakan command ini.')
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
                           description = "> Hallo nama ku Acinonyx!\n"
                                         "> Yuuk kita jalankan setup untuk server mu.\n\n"
                                         "> aku akan menyanyakan beberapa pertanyaan dan kamu dapat menjawabnya\n"
                                         "> atau kamu bisa menjawab `skip` untuk menggunakan settingan default ku\n"
                                         "> (atau menggunakan setting sebelumnya jika kamu sudah pernah melakukan setting dengan ku)")
        em.set_author(name = "Welcome Acinonyx Setup", url = "https://acinonyxesports.com", icon_url = "https://cdn.discordapp.com/attachments/518118753226063887/725569194304733435/photo.jpg")
        em.set_footer(text = "Request by : {}".format(ctx.author.name), icon_url = "{}".format(ctx.author.avatar_url))
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

        msg = '{}\n\nSaat ini adalah {}\n{}'.format(msg, auto, verifyString)
        
        await author.send(msg)
            

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
                await author.send(msg)
                return
            else:
                # We got something
                if talk.content.lower().startswith('y'):
                    await self.autoRoleName(ctx)
                elif talk.content.lower().startswith('n'):
                    self.settings.setServerStat(server, "DefaultRole", None)
                    await author.send('Auto-role *dimatikan.*')
                    await self.xpSystem(ctx)
                else:
                    # Skipping
                    await author.send('Auto-role tidak ada yang berubah: {}'.format(auto))
                    await self.xpSystem(ctx)
                gotIt = True

    # Get our default role
    async def autoRoleName(self, ctx):
        channel = ctx.message.channel
        author  = ctx.message.author
        server  = ctx.message.guild

        msg = 'Silahkan masukan nama role untuk mengatur auto-assign:'
        await author.send(msg)
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
                await author.send(msg)
                return
            else:
                # We got a response - check if it's a real role
                role = DisplayName.roleForName(talk.content, server)
                if not role:
                    msg = "┐(￣ヘ￣;)┌\nSepertinya aku tidak menemukan role dengan nama **{}** dalam server mu - silahkan coba lagi.".format(talk.content)
                    await author.send(msg)
                    continue
                else:
                    # Got a role!
                    msg = "Auto-role telah di set ke **{}**!".format(role.name)
                    await author.send(msg)
                    self.settings.setServerStat(server, "DefaultRole", role.id)
                    gotIt = True
        # Let's find out how long to wait for auto role to apply
        verify = int(self.settings.getServerStat(server, "VerificationTime"))
        msg = 'Jika kamu memiliki high security server - atau hanya menginginkan delay sebelum memberikan default role, Aku dapat melakukannya.\nBerapa lama waktu yang dibutuhkan untuk delay sebelum memberikan role kepada member yang baru join? (dalam hitungan menit)\n\nDelay saat ini adalah *{}*.'.format(verify)
        await author.send(msg)
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
                await author.send(msg)
                return
            else:
                # We got something
                if talk.content.lower() == "skip":
                    await author.send('Waktu delay Auto-role masih sama *{} menit*.'.format(threshold))
                else:
                    try:
                        talkInt = int(talk.content)
                        await author.send('Waktu delay untuk Auto-role sekarang menjadi *{} menit!*'.format(talkInt))
                        self.settings.setServerStat(server, "VerificationTime", talkInt)
                    except ValueError:
                        await author.send('Waktu delay Auto-role dimasukan dalam bentuk angka - Silahkan coba lagi.')
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
        msg = '{}\n\n__Current settings:__\n\nDefault xp saat bergabung: *{}*\nDefault xp yang disimpan saat bergabung: *{}*\nPendapatan XP setiap Jam: *{}*\nLimit XP setiap jam: *{}*\nPendapatan XP setiap jam yang mengharuskan user untuk online: *{}*\nPendapatan XP setiap pesan: *{}*\nPendapatan XP setiap jam: *{}*\nRole yang dibutuhkan untuk menggunakan XP system: **{}**\nUnlimited XP untuk admin: *{}*\nKenaikan role xp untuk user berdasarkan XP: *{}*\nPesan kenaikan role xp untuk user: *{}*\nPemurunan role xp untuk user berdasarkan XP: *{}*\nPesan penurunan role xp untuk user: *{}*'.format(msg, defXP, defXPR, hourXPReal, hourXP, reqOnline, messageXP, messageXPR, reqXP, adminUnlimited, xpProm, suppProm, xpDem, suppDem)
        await author.send(msg)

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
                await author.send(msg)
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
        msg = 'Dibutuhkan berapa banyak untuk setiap user dapat bergabung?\nSaat ini adalah *{}*.'.format(defXP)
        await author.send(msg)
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
                await author.send(msg)
                return
            else:
                # We got something
                if talk.content.lower() == "skip":
                    await author.send('Default xp masih tetap sama, yaitu *{}*.'.format(defXP))
                    self.settings.setServerStat(server, "DefaultXP", defXP)
                else:
                    try:
                        talkInt = int(talk.content)
                        await author.send('Default xp sekarang *{}!*'.format(talkInt))
                        self.settings.setServerStat(server, "DefaultXP", talkInt)
                    except ValueError:
                        # await self.autoRoleName(ctx)
                        await author.send('┐(￣ヘ￣;)┌\nDefault xp dimasukan dalam bentuk angka - silahkan coba lagi.')
                        continue
                gotIt = True
        
        ##########################################################################################################################
        # Default XP Reserve
        defXPR = self.settings.getServerStat(server, "DefaultXPReserve")
        if defXPR == None:
            defXPR = 10
        msg = 'Berapa banyak xp yang dapat di simpan user? (setiap user dapat transfer xp, gamble, atau memberi makan bot)\n\nSaat ini adalah *{}*.'.format(defXPR)
        await author.send(msg)
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
                await author.send(msg)
                return
            else:
                # We got something
                if talk.content.lower() == "skip":
                    await author.send('Default xp untuk simpanan user masih tetap sama, yaitu *{}*.'.format(defXPR))
                    self.settings.setServerStat(server, "DefaultXPReserve", defXPR)
                else:
                    try:
                        talkInt = int(talk.content)
                        await author.send('Default xp untuk simpanan user adalah *{}!*'.format(talkInt))
                        self.settings.setServerStat(server, "DefaultXPReserve", talkInt)
                    except ValueError:
                        # await self.autoRoleName(ctx)
                        await author.send('┐(￣ヘ￣;)┌\nDefault xp untuk simpanan user dimasukan dalam bentuk angka - silahkan coba lagi.')
                        continue
                gotIt = True
                
        ##########################################################################################################################
        # Hourly XP
        hourXPReal = self.settings.getServerStat(server, "HourlyXPReal")
        if hourXPReal == None:
            hourXPReal = 0
        msg = 'Berapa banyak xp (xp yang menentukan user role) yang akan didapatkan user setiap jam?\nSaat ini *{}*.'.format(hourXPReal)
        await author.send(msg)
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
                await author.send(msg)
                return
            else:
                # We got something
                if talk.content.lower() == "skip":
                    await author.send('Pendapatan xp setiap jam masih sama, yaitu *{}*.'.format(hourXPReal))
                    self.settings.setServerStat(server, "HourlyXPReal", hourXPReal)
                else:
                    try:
                        talkInt = int(talk.content)
                        await author.send('Pendapatan xp setiap jam sekarang *{}!*'.format(talkInt))
                        self.settings.setServerStat(server, "HourlyXPReal", talkInt)
                    except ValueError:
                        # await self.autoRoleName(ctx)
                        await author.send('┐(￣ヘ￣;)┌\nPendapatan xp setiap jam dimasukan dalam bentuk angka - silahkan coba lagi.')
                        continue
                gotIt = True
        
        ##########################################################################################################################
        # Hourly XP Reserve
        hourXP = self.settings.getServerStat(server, "HourlyXP")
        if hourXP == None:
            hourXP = 3
        msg = 'Berapa banyak limit untuk pendapatan xp setiap jam yang dapat di simpan user? (setiap user dapat transfer xp, gamble, atau memberi makan bot)\n\nSaat ini adalah  *{}*.'.format(hourXP)
        await author.send(msg)
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
                await author.send(msg)
                return
            else:
                # We got something
                if talk.content.lower() == "skip":
                    await author.send('Limit endapatan xp setiap jam yang dapat disimpan user masih tetap *{}*.'.format(hourXP))
                    self.settings.setServerStat(server, "HourlyXP", hourXP)
                else:
                    try:
                        talkInt = int(talk.content)
                        await author.send('Limit pendapatan xp setiap jam yang dapat disimpan user adalah *{}!*'.format(talkInt))
                        self.settings.setServerStat(server, "HourlyXP", talkInt)
                    except ValueError:
                        # await self.autoRoleName(ctx)
                        await author.send('┐(￣ヘ￣;)┌\nPendapatan xp setiap jam yang dapat disimpan user harus dimasukan dalam bentuk angka - silahkan coba lagi.')
                        continue
                gotIt = True

        ##########################################################################################################################
        # Required Online
        reqOnline = self.settings.getServerStat(server, "RequireOnline")
        msg = 'Apakah kamu ingin bot mengharuskan user berada pada status *online* untuk mendapatkan xp setiap jam? (y/n)\nSaat ini *{}*.'.format(reqOnline)
        await author.send(msg)
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
                await author.send(msg)
                return
            else:
                # We got something
                if talk.content.lower().startswith('y'):
                    self.settings.setServerStat(server, "RequireOnline", True)
                    await author.send('Status online saat ini *Yes.*')
                elif talk.content.lower().startswith('n'):
                    self.settings.setServerStat(server, "RequireOnline", False)
                    await author.send('Status online telah di setting ke *No.*')
                else:
                    # Skipping
                    await author.send('Status online akan tetap *{}*'.format(reqOnline))
                gotIt = True
                
        ##########################################################################################################################
        # XP Per Message
        messageXP = self.settings.getServerStat(server, "XPPerMessage")
        if messageXP == None:
            messageXP = 0
        msg = 'Berapa banyak xp (xp yang menentukan user role) yang akan didapatkan untuk user setiap pesan yang mereka kirim?\n\nSaat ini adalah *{}*.'.format(messageXP)
        await author.send(msg)
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
                await author.send(msg)
                return
            else:
                # We got something
                if talk.content.lower() == "skip":
                    await author.send('Pendapatan xp untuk setiap mengirim pesan masih tetap sama *{}*.'.format(messageXP))
                    self.settings.setServerStat(server, "XPPerMessage", messageXP)
                else:
                    try:
                        talkInt = int(talk.content)
                        await author.send('Pendapatan xp untuk setiap mengirim pesan saat ini adalah *{}!*'.format(talkInt))
                        self.settings.setServerStat(server, "XPPerMessage", talkInt)
                    except ValueError:
                        # await self.autoRoleName(ctx)
                        await author.send('┐(￣ヘ￣;)┌\nPendapatan xp untuk setiap mengirim pesan dimasukan dalam bentuk angka - silahkan coba lagi.')
                        continue
                gotIt = True
                
        ##########################################################################################################################
        # XP Reserve Per Message
        messageXPR = self.settings.getServerStat(server, "XPRPerMessage")
        if messageXPR == None:
            messageXPR = 0
        msg = 'Berapa limit xp yang dapat di dapatkan oleh user setiap mereka mengirim pesan? (setiap xp user dapat transfer xp, gamble, atau memberi makan bot)\n\nSaat ini adalah *{}*.'.format(messageXPR)
        await author.send(msg)
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
                await author.send(msg)
                return
            else:
                # We got something
                if talk.content.lower() == "skip":
                    await author.send('Limit pendapatan xp user setiap mengirim pesan masih tetap sama *{}*.'.format(messageXPR))
                    self.settings.setServerStat(server, "XPRPerMessage", messageXPR)
                else:
                    try:
                        talkInt = int(talk.content)
                        await author.send('Limit pendapatan xp user setiap mengirim pesan saat ini adalah *{}!*'.format(talkInt))
                        self.settings.setServerStat(server, "XPRPerMessage", talkInt)
                    except ValueError:
                        # await self.autoRoleName(ctx)
                        await author.send('┐(￣ヘ￣;)┌\nLimit pendapatan xp user harus dimasukan dalam bentuk angka - Silahkan coba lagi.')
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
        await author.send(msg)
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
                await author.send(msg)
                return
            else:
                # We got something
                if talk.content.lower() == "skip":
                    await author.send('XP role minimum saat ini adalah **{}**.'.format(reqXP))
                elif talk.content.lower() == "everyone":
                    self.settings.setServerStat(server, "RequiredXPRole", None)
                    await author.send('XP role minimum saat ini adalah **Everyone**.')
                else:
                    role = DisplayName.roleForName(talk.content, server)
                    if not role:
                        msg = "┐(￣ヘ￣;)┌\nSepertinya aku tidapat menemukan role **{}** dalam server mu - Silahkan coba lagi.".format(talk.content)
                        await author.send(msg)
                        continue
                    else:
                        self.settings.setServerStat(server, "RequiredXPRole", role.id)
                        await author.send('┐(￣ヘ￣;)┌Minimum xp role set to **{}**.'.format(role.name))
                gotIt = True

        ##########################################################################################################################
        # Admin Unlimited
        adminUnlimited = self.settings.getServerStat(server, "AdminUnlimited")
        msg = 'Apakah kamu menginginkan Admin memiliki limit xp yang tidak terbatas? (y/n)\n\nSaat ini adalah *{}*.'.format(adminUnlimited)
        await author.send(msg)
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
                await author.send(msg)
                return
            else:
                # We got something
                if talk.content.lower().startswith('y'):
                    self.settings.setServerStat(server, "AdminUnlimited", True)
                    await author.send('Tidak ada batasan limit untuk admin saat ini *Yes.*')
                elif talk.content.lower().startswith('n'):
                    self.settings.setServerStat(server, "AdminUnlimited", False)
                    await author.send('Tidak ada batasan limit untuk admin saat ini *No.*')
                else:
                    # Skipping
                    await author.send('Tidak ada batasan limit untuk admin saat ini masih tetap sama *{}*'.format(adminUnlimited))
                gotIt = True

        ##########################################################################################################################
        # Auto Promote
        xpProm = self.settings.getServerStat(server, "XPPromote")
        msg = 'Apakah kamu menginginkan ku untuk menaikan user xp role secara otomatis berdasarkan xp? (y/n)\n\nKamu dapat menentukan role mana yang dapat dipromote - dan persyaratan xp mereka.\n\nSaat ini adalah *{}*.'.format(xpProm)
        await author.send(msg)
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
                await author.send(msg)
                return
            else:
                # We got something
                if talk.content.lower().startswith('y'):
                    self.settings.setServerStat(server, "XPPromote", True)
                    await author.send('XP promote saat ini telah di set ke *Yes.*')
                elif talk.content.lower().startswith('n'):
                    self.settings.setServerStat(server, "XPPromote", False)
                    await author.send('XP promote saat ini telah di set ke *No.*')
                else:
                    # Skipping
                    await author.send('XP promote saat ini masih tetap sama *{}*'.format(xpProm))
                gotIt = True
                
        ##########################################################################################################################
        # Suppress Promote Message?
        suppProm = self.settings.getServerStat(server, "SuppressPromotions")
        msg = 'Apakah kamu ingin aku untuk tidak mengirimkan pesan ketika seorang user dinaikan role xpnya? (y/n)\n\nSaat ini adalah *{}*.'.format(suppProm)
        await author.send(msg)
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
                await author.send(msg)
                return
            else:
                # We got something
                if talk.content.lower().startswith('y'):
                    self.settings.setServerStat(server, "SuppressPromotions", True)
                    await author.send('Aku tidak akan mengimkan pesan promote')
                elif talk.content.lower().startswith('n'):
                    self.settings.setServerStat(server, "SuppressPromotions", False)
                    await author.send('Aku akan mengimkan pesan promote.')
                else:
                    # Skipping
                    await author.send('Promote message masih tetap sama *{}*'.format(suppProm))
                gotIt = True

        ##########################################################################################################################
        # Auto Demote
        xpDem = self.settings.getServerStat(server, "XPDemote")
        msg = 'Apakah kamu menginginkan aku menurunkan user role secara otomatis berdasarkan xp? (y/n)\n\nKamu dapat menentukan role mana yang dapat didemote - dan persyaratan xp mereka.\n\nCurrent is *{}*.'.format(xpDem)
        await author.send(msg)
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
                await author.send(msg)
                return
            else:
                # We got something
                if talk.content.lower().startswith('y'):
                    self.settings.setServerStat(server, "XPDemote", True)
                    await author.send('XP demote telah di set ke *Yes.*')
                elif talk.content.lower().startswith('n'):
                    self.settings.setServerStat(server, "XPDemote", False)
                    await author.send('XP demote telah di set ke *No.*')
                else:
                    # Skipping
                    await author.send('XP demote masih tetap sama *{}*'.format(xpDem))
                gotIt = True
                
        ##########################################################################################################################
        # Suppress Demote Message?
        suppDem = self.settings.getServerStat(server, "SuppressDemotions")
        msg = 'Apakah kamu menginginkan ku untuk tidak mengirim pesan saat user diturunkan rolenya? (y/n)\n\nSaat ini adalah *{}*.'.format(suppDem)
        await author.send(msg)
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
                await author.send(msg)
                return
            else:
                # We got something
                if talk.content.lower().startswith('y'):
                    self.settings.setServerStat(server, "SuppressDemotions", True)
                    await author.send('Aku tidak akan mengirimkan pesan saat user diturunkan role xpnya.')
                elif talk.content.lower().startswith('n'):
                    self.settings.setServerStat(server, "SuppressDemotions", False)
                    await author.send('Aku akan mengirimkan pesan saat user diturunkan role xpnya.')
                else:
                    # Skipping
                    await author.send('Pesan penurunan xp role masih sama *{}*'.format(suppDem))
                gotIt = True

        ##########################################################################################################################
        # XP Roles
        # Recheck xpProm and xpDem
        xpProm = self.settings.getServerStat(server, "XPPromote")
        xpDem = self.settings.getServerStat(server, "XPDemote")
        if xpProm or xpDem:
            msg = 'Untuk mengatur kenaikan/penurunan xp role - Kamu dapat mengetik `{}addxprole [role] [xp_yang_dibutuhkan]` untuk menambah role baru dalam server mu.\nDan `{}removexprole [role]` untuk menghapus role xp.\nCommand ini digunakan dalam server mu.'.format(ctx.prefix, ctx.prefix)
            await author.send(msg)

        await self.picThresh(ctx)


    async def picThresh(self, ctx):
        channel = ctx.message.channel
        author  = ctx.message.author
        server  = ctx.message.guild

        threshold = self.settings.getServerStat(server, "PictureThreshold")

        msg = 'Sebagai tindakan Anti-spam, Aku memiliki system cooldown untuk setiap gambar yang dapat saya tampilkan.\n Kamu menginginkan delay cooldown ini berapa lama? (dalam hitungan detik)?\n\nSaat ini adalah *{}*.'.format(threshold)
        await author.send(msg)
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
                await author.send(msg)
                return
            else:
                # We got something
                if talk.content.lower() == "skip":
                    await author.send('Cooldown Anti-spam gambar masih tetap sama *{}*.'.format(threshold))
                else:
                    try:
                        talkInt = int(talk.content)
                        await author.send('Cooldown Anti-spam gambar masih saat ini adalah *{}!*'.format(talkInt))
                        self.settings.setServerStat(server, "PictureThreshold", talkInt)
                    except ValueError:
                        # await self.autoRoleName(ctx)
                        await author.send('Cooldown Anti-spam gambar dimasukan dalam bentuk angka - Silahkan coba lagi.')
                        continue
                gotIt = True
        await self.hungerLock(ctx)

    async def hungerLock(self, ctx):
        channel = ctx.message.channel
        author  = ctx.message.author
        server  = ctx.message.guild

        hLock = self.settings.getServerStat(server, "HungerLock")
        msg = 'Apakah kamu menginginkan ku mengabaikan user saat aku kelaparan? (Aku *Selalu* Mengikuti apa kata admin) (y/n)\n\nSaat ini adalah *{}*.'.format(hLock)
        await author.send(msg)
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
                await author.send(msg)
                return
            else:
                # We got something
                if talk.content.lower().startswith('y'):
                    self.settings.setServerStat(server, "HungerLock", True)
                    await author.send('Pengingat tingkat kelaparan bot telah di set ke *Yes.*')
                elif talk.content.lower().startswith('n'):
                    self.settings.setServerStat(server, "HungerLock", False)
                    await author.send('Pengingat tingkat kelaparan bot telah di set ke *No.*')
                else:
                    # Skipping
                    await author.send('Pengingat tingkat kelaparan bot masih tetap sama *{}*'.format(hLock))
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
        msg = 'Apakah kamu menginginkan ku untuk melakukan mention @everyone dan @here dalam output command ku? (y/n)\n\nSaat ini adalah *{}*.'.format(hLock)
        await author.send(msg)
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
                await author.send(msg)
                return
            else:
                # We got something
                if talk.content.lower().startswith('y'):
                    self.settings.setServerStat(server, "SuppressMentions", True)
                    await author.send('Aku *akan* mention menggunakan @​everyone dan @​here.')
                elif talk.content.lower().startswith('n'):
                    self.settings.setServerStat(server, "SuppressMentions", False)
                    await author.send('Aku *tidak akan* mention menggunakan @​everyone dan @​here mentions.')
                else:
                    # Skipping
                    await author.send('Mention @​everyone dan @​here masih tetap sama *{}*'.format(hLock))
                gotIt = True
        await self.setupComplete(ctx)

    async def setupComplete(self, ctx):
        channel = ctx.message.channel
        author  = ctx.message.author
        server  = ctx.message.guild

        await author.send('__Setup Status untuk *{}*:__\n\n**COMPLETE**\n\nTerima kasih, *{}*, untuk meluangkan waktu mu untuk ku, dan menyiapkan berbagai hal untuk server mu.\nJika kamu tertarik untuk menjelajahi fitur ku yang lainnya, Jangan ragu untuk melihat semuanya dengan `{}help`.\n\nDan juga, Aku akan berusaha menjadi admin yang terbaik untuk server mu.\n\nThanks!'.format(self.suppressed(server, server.name), DisplayName.name(author), ctx.prefix))

# Calling a bot command:  await self.setup.callback(self, ctx)
