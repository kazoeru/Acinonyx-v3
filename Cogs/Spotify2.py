import discord
import spotipy
import os
import dropbox
import ffmpeg
import re
import subprocess
import asyncio
import json
from   discord.ext    import commands
from   Cogs           import Settings
from   savify         import Savify
from   savify.types   import Type, Format, Quality
from   spotipy.oauth2 import SpotifyClientCredentials
from   pathlib        import Path

help_spotdl = """Command ini membutuhkan nama penyanyi dan judul lagu setelah command.
**Contoh / Example**
`acx music Neffex - gratefull`
"""

processing_file = """Memproses file musik dari server Acinonyx

• [DISCLAIMER](https://github.com/acinonyx-esports/Acinonyx-Bot/wiki/SPOTIFY-DOWNLOADER-DISCLAIMER)
• [HOW THIS BOT IS WORK?](https://github.com/acinonyx-esports/Acinonyx-Bot/wiki/HOW-SPOTIFY-DOWNLOADER-IS-WORK%3F)"""

uploading_file = """Mengunggah file musik ke discord, tunggu sebentar...

• [DISCLAIMER](https://github.com/acinonyx-esports/Acinonyx-Bot/wiki/SPOTIFY-DOWNLOADER-DISCLAIMER)
• [HOW THIS BOT IS WORK?](https://github.com/acinonyx-esports/Acinonyx-Bot/wiki/HOW-SPOTIFY-DOWNLOADER-IS-WORK%3F)"""

upload_dropbox = """File melebihi batas server discord 8MB, memulai upload ke dropbox tunggu sebentar

• [DISCLAIMER](https://github.com/acinonyx-esports/Acinonyx-Bot/wiki/SPOTIFY-DOWNLOADER-DISCLAIMER)
• [HOW THIS BOT IS WORK?](https://github.com/acinonyx-esports/Acinonyx-Bot/wiki/HOW-SPOTIFY-DOWNLOADER-IS-WORK%3F)"""

upload_complete = """File musik telah di upload ke dropbox silahkan klik link dibawah ini, file akan dihapus dalam 7 menit
"""

def setup(bot):
    try:
        settings = bot.get_cog("Settings")
    except:
        settings = None
    bot.add_cog(Spotify2(bot, settings))

class Spotify2(commands.Cog):
    def __init__(self, bot, settings):
        self.preloads = ("Cogs.Settings")
        self.bot = bot
        self.settings = settings
        global Utils, DisplayName
        Utils = self.bot.get_cog("Utils")
        DisplayName = self.bot.get_cog("DisplayName")

    @commands.command(pass_context=True)
    async def music(self, ctx, *, music = None):
      with open ("/home/nvstar/Corp-ina.py/Settings.json") as settingsJson:
        data = json.load(settingsJson)
        Freemium = data["Servers"]["440765395172065280"]["Members"]
        user = "{}".format(ctx.author.id)
        isOwner = self.settings.isOwner(ctx.author)
        #if isOwner == None:
        #    return
        #elif isOwner == False:
        #    msgText = "Command ini sedang dalam tahap pengembangan"
        #    em = discord.Embed(color = 0XFF8C00, description = msgText)
        #    await ctx.channel.send(embed = em)
        #    return
        
        if user not in Freemium:
            msg = "Ini adalah fitur ***PREMIUM***\n"
            msg += "Dengan bergabung server kami, kamu dapat menggunakan fitur ini\n\n"
            msg += "**[Klik Disini](https://discord.gg/vMcMe8f)** untuk bergabung dengan kami"
            em = discord.Embed(color = 0XFF8C00,
                               description = msg)
            em.set_author(name = "PREMION ONLY")
            em.set_footer(text = "{}".format(ctx.author), icon_url= "{}".format(ctx.author.avatar_url))
            return await ctx.send(embed = em)

        if music == None:
            em = discord.Embed(title = "<a:exclamation:750557709107068939>**COMMAND FAILURE**<a:exclamation:750557709107068939>",
                              color = 0XFF8C00,
                              description = help_spotdl)
            em.set_thumbnail(url = "https://cdn.discordapp.com/attachments/518118753226063887/725569194304733435/photo.jpg")
            em.set_footer(text = f"Request by : {ctx.author.name}", icon_url = f"{ctx.author.avatar_url}")
            return await ctx.send(embed = em)


        sp = spotipy.Spotify(auth_manager = SpotifyClientCredentials(client_id = "690da446e39b44a7baf8deaff12be418",
                                                                     client_secret = "782ddebbf58846f1a1d70a074d62ce1a"))

        results = sp.search(q = f'{music}', limit = 1)
        for idx, track in enumerate(results['tracks']['items']):
            artist_name = track['artists'][0]['name']
            album_info = track['album']
            album_images = album_info['images'][0]
            album_images_url = album_images['url']
            album_artist = album_info['artists'][0]
            album_artist_name = album_artist['name']
            external_urls = track['external_urls']
            #external_urls_json = json.loads(external_urls)
            track_name = track['name']
            spotify_urls = external_urls['spotify']
            #embed dan hasil output
            em = discord.Embed(title = None, 
                               color = 0XFF8C00, 
                               description = f"> [{album_artist_name} - {track_name}]({spotify_urls})\n> \n> • [DISCLAIMER](https://github.com/acinonyx-esports/Acinonyx-Bot/wiki/SPOTIFY-DOWNLOADER-DISCLAIMER)\n> • [HOW THIS BOT IS WORK?](https://github.com/acinonyx-esports/Acinonyx-Bot/wiki/HOW-SPOTIFY-DOWNLOADER-IS-WORK%3F)\n> \n> <a:acx_mp3:744868331382767617> **.MP3 Format**")
            em.set_author(name = "Spotify downloader", 
                          url = "https://github.com/acinonyx-esports/Acinonyx-Bot/wiki/SPOTIFY-DOWNLOADER-DISCLAIMER", 
                          icon_url = "https://cdn.discordapp.com/attachments/726031951101689897/739778620658155602/spotify-logo-png-7061.png")
            em.set_thumbnail(url = album_images_url)
            em.set_footer(text = "Request by : {}".format(ctx.message.author.name),
                          icon_url = ctx.message.author.avatar_url)
            msg = await ctx.send(embed = em, delete_after = 15)
            await msg.add_reaction('<a:acx_mp3:744868331382767617>')
            while True:
                    reaction, user = await self.bot.wait_for(event='reaction_add',)
                    if user == ctx.author:
                        emoji = str(reaction.emoji)
                        if emoji == '<a:acx_mp3:744868331382767617>':
                            await msg.delete()
                            s = Savify(api_credentials=("690da446e39b44a7baf8deaff12be418","782ddebbf58846f1a1d70a074d62ce1a"),
                                       quality = Quality.BEST,
                                       download_format = Format.MP3,
                                       group='{}'.format(ctx.author.id),
                                       output_path=Path('/home/nvstar/Corp-ina.py/Temp'))
                            em = discord.Embed(title = None, 
                                               color = 0XFF8C00, 
                                               description = f"[{album_artist_name} - {track_name}]({spotify_urls})\n" + processing_file)
                            em.set_author(name = "Spotify downloader",
                                          url = "https://github.com/acinonyx-esports/Acinonyx-Bot/wiki/SPOTIFY-DOWNLOADER-DISCLAIMER",
                                          icon_url = "https://cdn.discordapp.com/attachments/726031951101689897/739778620658155602/spotify-logo-png-7061.png")
                            em.set_thumbnail(url = album_images_url)
                            em.set_footer(text = f"{ctx.author}",
                                          icon_url = ctx.message.author.avatar_url)
                            dld = await ctx.send(embed = em)

                            musicDownload = s.download("{}".format(spotify_urls))

                            checkServer = ctx.guild.premium_tier
                            if checkServer > 1:
                                em = discord.Embed(title = None, 
                                                    color = 0XFF8C00 , 
                                                    description = f"[{album_artist_name} - {track_name}]({spotify_urls})\n" + uploading_file)
                                em.set_author(name = "Spotify downloader",
                                              url = "https://github.com/acinonyx-esports/Acinonyx-Bot/wiki/SPOTIFY-DOWNLOADER-DISCLAIMER",
                                              icon_url = "https://cdn.discordapp.com/attachments/726031951101689897/739778620658155602/spotify-logo-png-7061.png")
                                em.set_thumbnail(url = album_images_url)
                                em.set_footer(text = f"{ctx.author}",
                                               icon_url = ctx.message.author.avatar_url)
                                await dld.edit(embed = em)
                                await ctx.send(file = discord.File(f"/home/nvstar/Corp-ina.py/Temp/{ctx.author.id}/{artist_name} - {track_name}.mp3"))

                                botKernel_DeleteFile = subprocess.Popen(["rm", "-rf", f"/home/nvstar/Corp-ina.py/Temp/{ctx.author.id}/{artist_name} - {track_name}.mp3"], stdout = subprocess.PIPE).communicate()[0]
                                
                                await dld.delete()
                                await ctx.send(f"{ctx.author.mention} :arrow_up:")

                            checkFile = os.path.getsize(f"/home/nvstar/Corp-ina.py/Temp/{ctx.author.id}/{artist_name} - {track_name}.mp3")
                            if checkFile > 8000000:
                                await dld.delete()
                                em = discord.Embed(
                                    title = "<a:exclamation:750557709107068939>**EXCEED THE LIMIT**<a:exclamation:750557709107068939>",
                                    color = 0XFF8C00,
                                    description = f"[{album_artist_name} - {track_name}]({spotify_urls})\n\n" + upload_dropbox)
                                em.set_thumbnail(url = album_images_url)
                                em.set_footer(text = f"{ctx.author}", 
                                              icon_url = f"{ctx.author.avatar_url}")
                                msg2 = await ctx.send(embed = em)

                                # MEMULAI UPLOAD DROPBOX
                                dropbox_access_token = "INmLpmjvCLQAAAAAAAAAAa--h2Jb571-pTJ_UHPdqp3XoMC0KJuSekPufnCI-a2y"
                                computer_path = '/home/nvstar/Corp-ina.py/Temp/{}/{} - {}.mp3'.format(ctx.author.id, artist_name, track_name)
                                dropbox_path = f"/Apps/Acinonyc music file/{album_artist_name} - {track_name}.mp3"
                                client = dropbox.Dropbox(dropbox_access_token)
                                print("[SUCCESS] dropbox account linked")
                                client.files_upload(open(computer_path, "rb").read(), dropbox_path, mode = dropbox.files.WriteMode("overwrite"))
                                print("[UPLOADED] {}".format(computer_path))
                                d = dropbox.Dropbox(dropbox_access_token)
                                target = dropbox_path
                                link_dropbox = d.sharing_create_shared_link(target)
                                dl_link = re.sub(r"\?dl\=0", "?dl=1", str(link_dropbox.url))
                                botKernel_DeleteFile = subprocess.Popen(["rm", "-rf", '/home/nvstar/Corp-ina.py/Temp/{}/{} - {}.mp3'.format(ctx.author.id, artist_name, track_name)], stdout = subprocess.PIPE).communicate()[0]
                                
                                #EMBED FILE SELESAI UPLOAD
                                em = discord.Embed(
                                    title = None,
                                    color = 0XFF8C00,
                                    description = f"{upload_complete}\n**[DOWNLOAD HERE]({dl_link})**")
                                em.set_author(name = "Spotify downloader",
                                               url = "https://github.com/acinonyx-esports/Acinonyx-Bot/wiki/SPOTIFY-DOWNLOADER-DISCLAIMER",
                                               icon_url = "https://cdn.discordapp.com/attachments/726031951101689897/739778620658155602/spotify-logo-png-7061.png")
                                em.set_thumbnail(url = album_images_url)
                                em.set_footer(text = f"{ctx.author.name}", icon_url = f"{ctx.author.avatar_url}")
                                await msg2.delete()
                                msg3 = await ctx.send(embed = em)

                                #DELETE FILES
                                await asyncio.sleep(420)
                                dropbox_delete = d.files_delete(dropbox_path)
                                await msg3.delete()                             

                            em2 = discord.Embed(title = None, 
                                                color = 0XFF8C00 , 
                                                description = f"[{album_artist_name} - {track_name}]({spotify_urls})\n" + uploading_file)
                            em2.set_author(name = "Spotify downloader",
                                          url = "https://github.com/acinonyx-esports/Acinonyx-Bot/wiki/SPOTIFY-DOWNLOADER-DISCLAIMER",
                                          icon_url = "https://cdn.discordapp.com/attachments/726031951101689897/739778620658155602/spotify-logo-png-7061.png")
                            em2.set_thumbnail(url = album_images_url)
                            em2.set_footer(text = f"{ctx.author}",
                                           icon_url = ctx.message.author.avatar_url)
                            await dld.edit(embed = em2)
                            await ctx.send(file = discord.File('/home/nvstar/Corp-ina.py/Temp/{}/{} - {}.mp3'.format(ctx.author.id, artist_name, track_name)))

                            botKernel_DeleteFile = subprocess.Popen(["rm", "-rf", '/home/nvstar/Corp-ina.py/Temp/{}/{} - {}.mp3'.format(ctx.author.id, artist_name, track_name)], stdout = subprocess.PIPE).communicate()[0]
                            
                            await dld.delete()
                            await ctx.send(f"{ctx.author.mention} :arrow_up:")
                    # if self.bot.user != user:
                    #     await msg.remove_reaction()

    @commands.command(pass_context=True)
    async def printspot(self, ctx, *, music = None):
        isOwner = self.settings.isOwner(ctx.author)
        if isOwner == None:
            return
        elif isOwner == False:
            msgText = "Command ini sedang dalam tahap pengembangan"
            em = discord.Embed(color = 0XFF8C00, description = msgText)
            await ctx.channel.send(msg)
            return

        sp = spotipy.Spotify(auth_manager = SpotifyClientCredentials(client_id = "690da446e39b44a7baf8deaff12be418",
                                                                     client_secret = "782ddebbf58846f1a1d70a074d62ce1a"))

        results = sp.search(q = f'{music}', limit = 1)
        for idx, track in enumerate(results['tracks']['items']):
            artist_name = track['artists'][0]['name']

            album_info = track['album']
            album_images = album_info['images'][0]
            album_images_url = album_images['url']
            album_artist = album_info['artists'][0]
            album_artist_name = album_artist['name']
            external_urls = track['external_urls']
            #external_urls_json = json.loads(external_urls)
            track_name = track['name']
            spotify_urls = external_urls['spotify']
            await ctx.send("```{}```".format(album_info))