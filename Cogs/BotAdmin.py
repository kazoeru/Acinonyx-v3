import asyncio, discord, re, random
from   operator import itemgetter
from   discord.ext import commands
from   Cogs import Utils, DisplayName, Message

def setup(bot):
    # hkan bot dan depenciesnya
    settings = bot.get_cog("Settings")
    bot.add_cog(BotAdmin(bot, settings))

class BotAdmin(commands.Cog):

    # Tambahkan init dengan referensi bot, dan referensi dari settings var.
    def __init__(self, bot, settings):
        self.bot = bot
        self.settings = settings
        self.dregex =  re.compile(r"(?i)(discord(\.gg|app\.com)\/)(?!attachments)([^\s]+)")
        self.mention_re = re.compile(r"\<\@!{0,1}[0-9]+\>")
        global Utils, DisplayName
        Utils = self.bot.get_cog("Utils")
        DisplayName = self.bot.get_cog("DisplayName")

    async def message(self, message):
        # Periksa invite link dan hapus jika ditemukan, lakukan pengecekan tiap server settings
        if not self.dregex.search(message.content): return None # Jika tidak ada invite pada pesan dari member abaikan saja, return None 
        # Acinonyx mendapatkan invite link dari pesan member, cek apakah Acinonyx harus menghapusnya?
        if not self.settings.getServerStat(message.guild,"RemoveInviteLinks",False): return None # Nilai False berarti abaikan saja, return None
        # Acinonyx *memiliki* izin untuk menghapus invite link
        # cek dulu, apakah pesan itu dari admin server yang memiliki izin untuk melakukan post invite link?
        ctx = await self.bot.get_context(message)
        if Utils.is_bot_admin(ctx): return None # Kalau pesan itu dari admin abaikan saja, return None
        # Disini Acinonyx mendapat invite link tapi bukan dari admin server yang tidak memiliki izin untuk post invite link
        # hapus saja pesannya
        return { 'Ignore' : True, 'Delete' : True}

    @commands.command(pass_context=True)
    async def removeinvitelinks(self, ctx, *, yes_no = None):
        """**INDONESIA**
        on/off auto-delete discord invite links dalam chat.

        **ENGLISH**
        Enables/Disables auto-deleting discord invite links in chat.
        (Admin server only)."""
        LangCheck = self.settings.getUserStat(ctx.message.author, ctx.message.guild, "Language")

        if LangCheck == None:
            # Author belum memilih bahasa
            await self.language_not_set(ctx)

        if not await Utils.is_bot_admin_reply(ctx): return
        await ctx.send(Utils.yes_no_setting(ctx,"Remove discord invite links","RemoveInviteLinks",yes_no))

    # @commands.command(pass_context=True)
    # async def setuserparts(self, ctx, member : discord.Member = None, *, parts : str = None):
    #     """Set user parts list (owner only)."""
    #     # Only allow owner
    #     isOwner = self.settings.isOwner(ctx.author)
    #     if isOwner == None:
    #         msg = 'Aku belum ada owner.'
    #         return await ctx.send(msg)
    #     elif isOwner == False:
    #         msgText = ["Siapa yaa?\nKamu bukan owner ku",
    #                    "Kamu bukan owner ku",
    #                    "Hus hus, jangan main main sama command ini",
    #                    "Command ini bahaya loh dek, jangan main main!",
    #                    "ikjdfahguiyaewgkljasdcbngiuefabhg\nkamu bukan owner ku!!!"]
    #         msg = random.choice(msgText)
    #         em = discord.Embed(color = 0XFF8C00, description = msg)
    #         em.set_footer(text = "{}#{}".format(ctx.author.name, ctx.author.discriminator))
    #         return await ctx.send(embed = em)
            
    #     if member == None:
    #         msg = 'Panduan: `{}setuserparts [member] "[parts text]"`'.format(ctx.prefix)
    #         return await ctx.send(msg)

    #     if type(member) is str:
    #         try:
    #             member = discord.utils.get(ctx.guild.members, name=member)
    #         except:
    #             return await ctx.send("Tidak dapat menemukan member")

    #     if not parts:
    #         parts = ""
            
    #     self.settings.setGlobalUserStat(member, "Parts", parts)
    #     msg = '*{}* parts telah di set ke:\n{}'.format(DisplayName.name(member), parts)
    #     await ctx.send(Utils.suppressed(ctx,msg))
        
    # @setuserparts.error
    # async def setuserparts_error(self, error, ctx):
    #     # do stuff
    #     msg = 'setuserparts Error: {}'.format(error)
    #     await ctx.send(msg)

    @commands.command(pass_context=True)
    async def ignore(self, ctx, *, member = None):
        """**INDONESIA**
        Menambahkan member kedalam ignore list.
        Member yang masuk kedalam ignore list tidak dapat menggunakan bot ini dalam server mu.

        **ENGLISH**
        Adds a member to the bot's "ignore" list.
        Member in my ignore list, i will ignore them when they use my commands"""
        LangCheck = self.settings.getUserStat(ctx.message.author, ctx.message.guild, "Language")

        if LangCheck == None:
            # Author belum memilih bahasa
            await self.language_not_set(ctx)

        if not await Utils.is_bot_admin_reply(ctx): return
            
        if member == None:
            if LangCheck == "ID":
                em = discord.Embed(color = 0XFF8C00, description = "> Menambahkan member agar tidak dapat menggunakan bot ini dalam server mu\n> \n"
                                                                   "> **Panduan Penggunaan**\n"
                                                                  f"> `{ctx.prefix}ignore [member]`\n")
                em.set_footer(text = "Saat mengetik command, tanda [] tidak usah digunakan\nRequest by : {}".format(ctx.author),
                              icon_url = "{}".format(ctx.author.avatar_url))
            if LangCheck == "EN":
                em = discord.Embed(color = 0XFF8C00, description = "> Adds a member to the bot's \"ignore\" list, Member in my ignore list, i will ignore them when they use my commands\n> \n"
                                                                   "> **Panduan Penggunaan**\n"
                                                                  f"> `{ctx.prefix}ignore [member]`\n")
                em.set_footer(text = "Saat mengetik command, tanda [] tidak usah digunakan\n{}".format(ctx.author),
                              icon_url = "{}".format(ctx.author.avatar_url))
            return await ctx.send(embed = msg)

        if type(member) is str:
            memberName = member
            member = DisplayName.memberForName(memberName, ctx.guild)
            if not member:
                msg = '┐(￣ヘ￣;)┌\nAku tidak dapat menemukan *{}* dalam server mu...'.format(memberName)
                em = discord.Embed(color = 0XFF8C00, description = msg)
                em.set_footer(text = "{}#{}".format(ctx.author.name, ctx.author.discriminator))
                return await ctx.send(embed = em)
                # return await ctx.send(Utils.suppressed(ctx,embed = em))

        ignoreList = self.settings.getServerStat(ctx.guild, "IgnoredUsers")

        for user in ignoreList:
            if str(member.id) == str(user["ID"]):
                # Found our user - already ignored
                em = discord.Embed(color = 0XFF8C00, description = "User <@{}>\n"
                                                                   "Telah dimasukan kedalam ignore list, dan tidak dapat menggunakan bot ini dalam server mu\n> \n"
                                                                   "**Daftar list ignore**\n"
                                                                   "`{}ignored`\n"
                                                                   "**Panduan penghapusan member**\n"
                                                                   "`{}listen [member]`"
                                                                   .format(member.id,
                                                                           ctx.prefix,
                                                                           ctx.prefix))
                em.set_footer(text = "Saat mengetik command, tanda [] tidak usah digunakan\n{}".format(ctx.author.name), icon_url = "{}".format(ctx.author.avatar_url))
                return await ctx.send(embed = em)
                # return await ctx.send('*{}* telah terdaftar dalam ignore list.'.format(DisplayName.name(member)))
        # Let's ignore someone
        ignoreList.append({ "Name" : member.name, "ID" : member.id })
        self.settings.setServerStat(ctx.guild, "IgnoredUsers", ignoreList)
        em = discord.Embed(color = 0XFF8C00, description = "User <@{}>\n"
                                                           "Telah dimasukan kedalam ignore list, dan tidak dapat menggunakan bot ini dalam server mu\n> \n"
                                                           "**Daftar list ignore**\n"
                                                           "`{}ignored`\n"
                                                           "**Panduan penghapusan member**\n"
                                                           "`{}listen [member]`"
                                                           .format(member.id,
                                                                   ctx.prefix,
                                                                   ctx.prefix))
        em.set_footer(text = "Saat mengetik command, tanda [] tidak usah digunakan\n{}".format(ctx.author.name), icon_url = "{}".format(ctx.author.avatar_url))
        await ctx.send(embed = em)
        
    @ignore.error
    async def ignore_error(self, error, ctx):
        # do stuff
        msg = 'ignore Error: {}'.format(error)
        await ctx.send(msg)


    @commands.command(pass_context=True)
    async def listen(self, ctx, *, member = None):
        """Menghapus member dari list ignore dalam server mu (bot-admin only)."""
        if not await Utils.is_bot_admin_reply(ctx): return
            
        if member == None:
            em = discord.Embed(color = 0XFF8C00, description = "> Menghapus member dari list ignore, dan dapat menggunakan bot ini dalam server mu\n> \n"
                                                               "> **Panduan Penggunaan**\n"
                                                               "> `{}listen [member]`"
                                                               .format(ctx.prefix))
            em.set_author(name = "Command listen", url = "https://acinonyxesports.com", icon_url = "https://cdn.discordapp.com/attachments/518118753226063887/725569194304733435/photo.jpg")
            em.set_footer(text = "Saat mengetik command, tanda [] tidak usah digunakan\nRequest by : {}".format(ctx.author.name), icon_url = "{}".format(ctx.author.avatar_url))
            return await ctx.send(embed = em)

        if type(member) is str:
            memberName = member
            member = DisplayName.memberForName(memberName, ctx.guild)
            if not member:
                msg = '┐(￣ヘ￣;)┌\nAku tidak dapat menemukan *{}* dalam list ignore...'.format(memberName)
                return await ctx.send(Utils.suppressed(ctx,msg))

        ignoreList = self.settings.getServerStat(ctx.guild, "IgnoredUsers")

        for user in ignoreList:
            if str(member.id) == str(user["ID"]):
                # Found our user - already ignored
                ignoreList.remove(user)
                self.settings.setServerStat(ctx.guild, "IgnoredUsers", ignoreList)
                em = discord.Embed(color = 0XFF8C00, description =  "> User <@{}>\n"
                                                                    "> Telah dihapus dari ignore list, dan dapat menggunakan bot ini dalam server mu\n> \n"
                                                                    "> **Panduan penambahan member**\n"
                                                                    "> `{}ignore [member]`\n"
                                                                   .format(member.id,
                                                                           ctx.prefix))
                em.set_author(name = "Command ignore", url = "https://acinonyxesports.com", icon_url = "https://cdn.discordapp.com/attachments/518118753226063887/725569194304733435/photo.jpg")
                em.set_footer(text = "Saat mengetik command, tanda [] tidak usah digunakan\nRequest by : {}".format(ctx.author.name), icon_url = "{}".format(ctx.author.avatar_url))
                return await ctx.send(embed = em)

        await ctx.send('*{}* tidak terdaftar dalam list ignore...'.format(DisplayName.name(member)))
        
    @listen.error
    async def listen_error(self, error, ctx):
        # do stuff
        msg = 'listen Error: {}'.format(error)
        await ctx.send(msg)


    @commands.command(pass_context=True)
    async def ignored(self, ctx):
        """List member yang tidak dapat menggunakan bot ini dalam server mu."""
        ignoreArray = self.settings.getServerStat(ctx.guild, "IgnoredUsers")
        promoSorted = sorted(ignoreArray, key=itemgetter('Name'))
        if not len(promoSorted):
            msg = "┐(￣ヘ￣;)┌\nTidak ada seseorang yang ada dalam ignore list ku"
            em = discord.Embed(color = 0XFF8C00, description = msg)
            em.set_footer(text = "{}#{}".format(ctx.author.name, ctx.author.discriminator))
            return await ctx.send(embed = em)
        ignored = ["*{}*".format(DisplayName.name(ctx.guild.get_member(int(x["ID"])))) for x in promoSorted if ctx.guild.get_member(int(x["ID"]))]
        em = discord.Embed(color = 0XFF8C00, description = "**List Member:**\n"
                                                           "{}".format("\n".join(ignored)))
        em.set_author(name = "List ignore", url = "https://acinonyxesports.com", icon_url = "https://cdn.discordapp.com/attachments/518118753226063887/725569194304733435/photo.jpg")
        em.set_footer(text = "Request by : {}".format(ctx.author.name), icon_url = "{}".format(ctx.author.avatar_url))
        await ctx.send(embed = em)

    
    async def kick_ban(self, ctx, members_and_reason = None, command_name = "kick"):
        # Helper method to handle the lifting for kick and ban
        if not await Utils.is_bot_admin_reply(ctx): return
        # isOwner = self.settings.isOwner(ctx.author)
        # if isOwner == False:
        #     return
        if not members_and_reason:
            em = discord.Embed(color = 0XFF8C00, description = "> **Panduan {} member**\n"
                                                               "> `{}{} [mention member, spasi dibutuhkan jika lebih dari 1 orang] [alasan]`"
                                                               .format(command_name,
                                                                       ctx.prefix,
                                                                       command_name))
            em.set_author(name = f"{command_name}", url = "https://acinonyxesports.com", icon_url = "https://cdn.discordapp.com/attachments/518118753226063887/725569194304733435/photo.jpg")
            em.set_footer(text = "Saat mengetik command, tanda [] tidak usah digunakan\n{}#{}".format(ctx.author.name, ctx.author.discriminator), icon_url = "{}".format(ctx.author.avatar_url))
            return await ctx.send(embed = em)
        # Force a mention - we don't want any ambiguity
        args = members_and_reason.split()
        # Get our list of targets
        targets = []
        reason = ""
        for index,item in enumerate(args):
            if self.mention_re.search(item): # Check if it's a mention
                # Resolve the member
                member = ctx.guild.get_member(int(re.sub(r'\W+', '', item)))
                # If we have an invalid mention - bail - no ambiguity
                msg = "┐(￣ヘ￣;)┌\nInvalid mention"
                em = discord.Embed(color = 0XFF8C00, description = msg)
                em.set_footer(text = "{}#{}".format(ctx.author.name, ctx.author.discriminator),
                              icon_url = "{}".format(ctx.author.avatar_url))
                if member is None: return await ctx.send(embed = em)
                # We should have a valid member - let's make sure it's not:
                # 1. The bot, 2. The command caller, 3. Another bot-admin/admin
                msg = "╥﹏╥ Noooooo\nAku gak mau keluar dari sini!!"
                em = discord.Embed(color = 0XFF8C00, description = msg)
                em.set_footer(text = "{}#{}".format(ctx.author.name, ctx.author.discriminator),
                              icon_url = "{}".format(ctx.author.avatar_url))
                if member.id == self.bot.user.id: return await ctx.send(embed = em)
                msg = "(￣ー￣;)ゞ\nKok nge{} diri sendiri...?".format(command_name)
                em = discord.Embed(color = 0XFF8C00, description = msg)
                em.set_footer(text = "{}#{}".format(ctx.author.name, ctx.author.discriminator),
                              icon_url = "{}".format(ctx.author.avatar_url))
                if member.id == ctx.author.id: return await ctx.send(embed = em)
                msg = "┐(￣ヘ￣;)┌\nKamu tidak dapat melakukan {} pada admin lain!".format(command_name)
                em = discord.Embed(color = 0XFF8C00, description = msg)
                em.set_footer(text = "{}#{}".format(ctx.author.name, ctx.author.discriminator),
                              icon_url = "{}".format(ctx.author.avatar_url))
                if Utils.is_bot_admin(ctx,member): return await ctx.send(embed = em)
                targets.append(member)
            else:
                # Not a mention - must be the reason, dump the rest of the items into a string
                # separated by a space
                reason = " ".join(args[index:])
                break
        msg = "┐(￣ヘ￣;)┌\nAku tidak dapat menemukan member yang kamu cari"
        em = discord.Embed(color = 0XFF8C00, description = msg)
        em.set_footer(text = "{}#{}".format(ctx.author.name, ctx.author.discriminator),
                      icon_url = "{}".format(ctx.author.avatar_url))
        if not len(targets): return await ctx.send(embed = em)
        msg = "┐(￣ヘ￣;)┌\nKamu hanya dapat menggunakan {} sampai dengan 5 member dalam 1 command!".format(command_name)
        em = discord.Embed(color = 0XFF8C00, description = msg)
        em.set_footer(text = "{}#{}".format(ctx.author.name, ctx.author.discriminator),
                      icon_url = "{}".format(ctx.author.avatar_url))
        if len(targets) > 5: return await ctx.send(embed = em)
        msg = "┐(￣ヘ￣;)┌\nAlasan {} dibutuhkan".format(command_name)
        em = discord.Embed(color = 0XFF8C00, description = msg)
        em.set_footer(text = "{}#{}".format(ctx.author.name, ctx.author.discriminator),
                      icon_url = "{}".format(ctx.author.avatar_url))
        if not len(reason): return await ctx.send(embed = em)
        # We should have a list of targets, and the reason - let's list them for confirmation
        # then generate a 4-digit confirmation code that the original requestor needs to confirm
        # in order to follow through
        confirmation_code = "".join([str(random.randint(0,9)) for x in range(4)])
        msg = "**Untuk {} member berikut{}:**\n{}\n\n**Dengan alasan:**\n\"{}\"\n\n**Silahkan ketik:**\n`{}`".format(
            command_name,
            "" if len(targets) == 1 else "",
            "\n".join([x.name+"#"+x.discriminator for x in targets]),
            reason,
            confirmation_code
            )
        confirmation_message = await Message.EmbedText(title="Konfirmasi {} member".format(command_name.capitalize()),description=msg,color=0XFF8C00).send(ctx)
        def check_confirmation(message):
            return message.channel == ctx.channel and ctx.author == message.author # Just making sure it's the same user/channel
        try: confirmation_user = await self.bot.wait_for('message', timeout=60, check=check_confirmation)
        except: confirmation_user = ""
        # Delete the confirmation message
        await confirmation_message.delete()
        # Verify the confirmation
        msg = "┐(￣ヘ￣;)┌\nKode verifikasi salah.\n{} member dibatalkan!".format(command_name.capitalize())
        em = discord.Embed(color = 0XFF8C00, description = msg)
        em.set_footer(text = "{}#{}".format(ctx.author.name, ctx.author.discriminator),
                      icon_url = "{}".format(ctx.author.avatar_url))
        if not confirmation_user.content == confirmation_code: return await ctx.send(embed = em)
        # We got the authorization!
        message = await Message.EmbedText(title="{}ing...".format("Bann" if command_name == "ban" else "Kick"),color=0XFF8C00).send(ctx)
        canned = []
        cant = []
        command = ctx.guild.ban if command_name == "ban" else ctx.guild.kick
        for target in targets:
            try:
                await command(target,reason="{}#{}: {}".format(ctx.author.name,ctx.author.discriminator,reason))
                canned.append(target)
            except: cant.append(target)
        msg = ""
        if len(canned):
            msg += "**Aku berhasil {} member berikut:**\n{}\n\n".format(command_name,"\n".join([x.name+"#"+x.discriminator for x in canned]))
        if len(cant):
            msg += "**Aku tidak dapat {} member berikut:**\n{}\n\n".format(command_name,"\n".join([x.name+"#"+x.discriminator for x in cant]))
        await Message.EmbedText(color = 0XFF8C00,title="Hasil {}".format(command_name.capitalize()),description=msg).edit(ctx,message)

    @commands.command(pass_context=True)
    async def kick(self, ctx, *, members = None, reason = None):
        """Kick member yang kamu tuju dan berikan alasannya.
        Semua target kick harus di mention untuk menghindari kesamaan nama.
        Kamu dapat melakukan kick hingga 5 user sekaligus.
        Alasan kick dibutuhkan (bot-admin only).
        
        contoh:  acx!ban @user1#1234 @user2#5678 @user3#9012 spam lu anj"""
        await self.kick_ban(ctx,members, "kick")
        
        
    @commands.command(pass_context=True)
    async def ban(self, ctx, *, members = None, reason = None):
        """Ban member yang kamu tuju dan berikan alasannya.
        Semua target ban harus di mention untuk menghindari kesamaan nama.
        Kamu dapat melakukan ban hingga 5 user sekaligus.
        Alasan ban dibutuhkan (bot-admin only).
        
        contoh:  acx!ban @user1#1234 @user2#5678 @user3#9012 spam lu anj"""
        await self.kick_ban(ctx,members, "ban")


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
