import asyncio, discord, time
from   operator import itemgetter
from   discord.ext import commands
from   Cogs import Utils, ReadableTime, DisplayName

def setup(bot):
    # Add the bot and deps
    settings = bot.get_cog("Settings")
    mute     = bot.get_cog("Mute")
    bot.add_cog(Fliptime(bot, settings, mute))

# This is the Uptime module. It keeps track of how long the bot's been up

class Fliptime(commands.Cog):

    # Init with the bot reference, and a reference to the settings var
    def __init__(self, bot, settings, mute):
        self.bot = bot
        self.settings = settings
        self.mute = mute
        global Utils, DisplayName
        Utils = self.bot.get_cog("Utils")
        DisplayName = self.bot.get_cog("DisplayName")

    async def message_edit(self, before_message, message):
        # Pipe the edit into our message func to respond if needed
        return await self.message(message)

    async def test_message(self, message):
        # Implemented to bypass having this called twice
        return { "Ignore" : False, "Delete" : False }

    async def message(self, message):
        # Check the message and see if we should allow it - always yes.
        # This module doesn't need to cancel messages.
        # Check if our server supports it
        table = self.settings.getServerStat(message.guild, "TableFlipMute")

        if not table:
            return { 'Ignore' : False, 'Delete' : False}

        # Check for admin status
        ctx = await self.bot.get_context(message)
        isAdmin = Utils.is_bot_admin(ctx)

        # Check if the message contains the flip chars
        conts = message.content
        face = table = False
        table_list  = [ '┻', '╙', '╨', '╜', 'ǝʃqɐʇ', '┺' ]
        front_list = [ '(' ]
        back_list  = [ ')', '）' ]
        if any(ext in conts for ext in front_list) and any(ext in conts for ext in back_list):
            face = True
        if any(ext in conts for ext in table_list):
            table = True
        if face and table:  
            # Contains all characters
            # Table flip - add time
            currentTime = int(time.time())
            cooldownFinal = currentTime+60
            alreadyMuted = self.settings.getUserStat(message.author, message.guild, "Muted")
            if not isAdmin:
                # Check if we're muted already
                previousCooldown = self.settings.getUserStat(message.author, message.guild, "Cooldown")
                if not previousCooldown:
                    if alreadyMuted:
                        # We're perma-muted - ignore
                        return { 'Ignore' : False, 'Delete' : False}
                    previousCooldown = 0
                if int(previousCooldown) > currentTime:
                    # Already cooling down - add to it.
                    cooldownFinal = previousCooldown+60
                    coolText = ReadableTime.getReadableTimeBetween(currentTime, cooldownFinal)
                    res = '> ┬─┬ ノ( ゜-゜ノ)\n> *{}*, Aku mengerti jika kamu sedang frustasi.\n> Tapi kami tidak melempar meja di server ini\nKenapa kamu tidak menenangkan diri dulu untuk *{}*.'.format(DisplayName.name(message.author), coolText)
                    em = discord.Embed(color = 0XFF8C00,
                                       description = res)
                    em.set_author(name = "⚠ GAK BOLEH TABLE FLIP", icon_url = "https://cdn.discordapp.com/attachments/518118753226063887/725569194304733435/photo.jpg")
                else:
                    # Not cooling down - start it
                    coolText = ReadableTime.getReadableTimeBetween(currentTime, cooldownFinal)
                    res = '> ┬─┬ ノ( ゜-゜ノ)\n> *{}*, kita tidak menggunakan table flip disini.\n> Aku akan membuat kamu cooldown selama *{}*'.format(DisplayName.name(message.author), coolText)
                    em = discord.Embed(color = 0XFF8C00,
                                       description = res)
                    em.set_author(name = "⚠ GAK BOLEH TABLE FLIP", icon_url = "https://cdn.discordapp.com/attachments/518118753226063887/725569194304733435/photo.jpg")
                # Do the actual muting
                await self.mute._mute(message.author, message.guild, cooldownFinal)

                await message.channel.send(embed=em)
                return { 'Ignore' : True, 'Delete' : True }     

        return { 'Ignore' : False, 'Delete' : False}

    @commands.command(pass_context=True)
    async def tableflip(self, ctx, *, yes_no = None):
        """Menyalakan on/off table flip mute dalam server (bot-admin only)."""
        if not await Utils.is_admin_reply(ctx): return
        await ctx.send(Utils.yes_no_setting(ctx,"Table flip muting","TableFlipMute",yes_no))
