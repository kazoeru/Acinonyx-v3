import asyncio
import discord
import os
import time
import random
from   datetime import datetime
from   discord.ext import commands

def setup(bot):
    # Add the bot and deps
    settings = bot.get_cog("Settings")
    bot.add_cog(GlobalMigration(bot, settings))

# This is the GlobalMigration module.

class GlobalMigration(commands.Cog):

    # Init with the bot reference, and a reference to the settings var
    def __init__(self, bot, settings):
        self.bot = bot
        self.settings = settings


    @commands.command(pass_context=True, hidden=True)
    async def clearlocal(self, ctx, setting = None):
        """Clear local setting user. (owner-only)"""
        # Only allow owner
        isOwner = self.settings.isOwner(ctx.author)
        if isOwner == None:
            msg = 'I have not been claimed, *yet*.'
            await ctx.channel.send(msg)
            return
        elif isOwner == False:
            msgText = ["Siapa yaa?\nKamu bukan owner ku",
                       "Kamu bukan owner ku",
                       "Hus hus, jangan main main sama command ini",
                       "Command ini bahaya loh dek, jangan main main!"]
            msg = random.choice(msgText)
            await ctx.channel.send(msg)
            return

        if not setting:
            msg = "Owner o'on.\nLu butuh nama setting yang jelas untuk menggunakan command ini"
            await ctx.channel.send(msg)
            return

        for guild in self.bot.guilds:
            for member in guild.members:
                # Clear the setting
                self.settings.setUserStat(member, guild, setting, None)
        msg = "Local stat cleared!"
        await ctx.channel.send(msg)


    @commands.command(pass_context=True, hidden=True)
    async def migrate(self, ctx, setting = None):
        """Migrasi local setting menjadi global (owner only)."""
        # Only allow owner
        isOwner = self.settings.isOwner(ctx.author)
        if isOwner == None:
            msg = 'Belum ada owner.'
            await ctx.channel.send(msg)
            return
        elif isOwner == False:
            msgText = ["Siapa yaa?\nKamu bukan owner ku",
                       "Kamu bukan owner ku",
                       "Hus hus, jangan main main sama command ini",
                       "Command ini bahaya loh dek, jangan main main!"]
            msg = random.choice(msgText)
            await ctx.channel.send(msg)
            return

        if not setting:
            msg = "Owner o'on.\nLu butuh nama setting yang jelas untuk menggunakan command ini."
            await ctx.channel.send(msg)
            return

        for member in ctx.guild.members:
            # Check this guild first
            if self.settings.getGlobalUserStat(member, setting):
                # Already set - continue
                continue
            tempStat = self.settings.getUserStat(member, ctx.guild, setting)
            self.settings.setGlobalUserStat(member, setting, tempStat)

        for guild in self.bot.guilds:
            if guild is ctx.guild:
                continue
            for member in guild.members:
                if self.settings.getGlobalUserStat(member, setting):
                    # Already set - continue
                    continue
                tempStat = self.settings.getUserStat(member, guild, setting)
                self.settings.setGlobalUserStat(member, setting, tempStat)

        msg = "Migrasi stat berhasil!"
        await ctx.channel.send(msg)