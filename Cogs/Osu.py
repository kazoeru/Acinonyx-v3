import discord
from discord.ext import commands
import requests, json, re, random

def setup(bot):
    bot.add_cog(Osu(bot))

class Osu(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        global Utils, DisplayName
        Utils = self.bot.get_cog("Utils")
        DisplayName = self.bot.get_cog("DisplayName")


    @commands.command()
    async def osustd(self, ctx):
        """Mencari informasi player mode standard"""
        print ("{} Menggunakan command OSU STANDARD".format(ctx.author.name))
        num = 30
        split = ctx.message.content.split(" ")
        nvstarapp = ctx.message.content.replace(split[0] + " ","")
        banner_avatar = ctx.message.content.replace(split[0] + " ","")
        # STATISTIC PLAYER
        r = requests.get("https://osu.ppy.sh/api/get_user?k=526d85b33ad4b0912850229a00e17e91b612d653&m=0&u={}".format(nvstarapp))
        data = r.text
        data = json.loads(data)
        a = data
        #BEST PERFORMANCE
        r2 = requests.get("https://osu.ppy.sh/api/get_user_best?k=526d85b33ad4b0912850229a00e17e91b612d653&limit=1&m=0&u={}".format(str(a[0]["username"])))
        data2 = r2.text
        data2 = json.loads(data2)
        b = data2
        # BEATMAPS
        r3 = requests.get("https://osu.ppy.sh/api/get_beatmaps?k=526d85b33ad4b0912850229a00e17e91b612d653&b={}".format(str(b[0]["beatmap_id"])))
        data3 = r3.text
        data3 = json.loads(data3)
        c = data3
        # PEMBULATAN KABAWAH UNTUK LEVEL
        level = a[0]["level"]
        flevel = float(level)
        rlevel = int(flevel)
        # PEMBULATAN KEBAWAH UNTUK PERFORMANCE
        pp = a[0]["pp_raw"]
        fpp = float(pp)
        rpp = int(fpp)
        # PEMBULATAN KEBAWAH UNTUK AKURASI
        acc = a[0]["accuracy"]
        facc = float(acc)
        racc = int(facc)
        # PEMBULATAN UNTUK BEST PERFORMANCE
        bpp = b[0]["pp"]
        rbpp = float(bpp)
        rbpp = round(rbpp)
        # PENGAMBILAN 2 ANGKA DI BELAKANG KOMA UNTUK DIFFICULT BEATMAPS
        dbm = c[0]["difficultyrating"]
        rdbm = "{:.2f}".format(float(dbm))
        # PENAMBAHAN TITIK SETIAP 3 DIGIT UNTUK SCORE
        tds = b[0]["score"]
        ttds = re.sub(r"(?<!^)(?=(\d{3})+$)", r".", "{}".format(tds))
        # EMBED BOT UNTUK STATISTIC PLAYER
        em = discord.Embed(color = 0XFF8C00, title = "INFORMASI PLAYER STANDARD")
        em.add_field(name = "Nama PLayer", value = "{}".format(str(a[0]["username"])))
        em.add_field(name = "Level", value = "{}".format(str(rlevel)))
        em.add_field(name = "Performance (PP)", value = "{}".format(str(rpp)))
        em.add_field(name = "Akurasi (ACC)", value = "{}%".format(str(racc)))
        em.add_field(name = "Peringkat Dunia", value = "#{}".format(str(a[0]["pp_rank"])))
        em.add_field(name = "Peringkat Negara", value = "#{}".format(str(a[0]["pp_country_rank"])))
        em.add_field(name = "Homepage Link", value = "https://osu.ppy.sh/users/{}".format(str(a[0]["user_id"])), inline = False)
        em.add_field(name = "Request By", value = f"{ctx.author.mention}")
        em.set_footer(text = f"Klik tombol reaction ▶️ untuk melihat Best Performance\n", icon_url=ctx.author.avatar_url)
        em.set_image(url = "http://lemmmy.pw/osusig/sig.php?colour=hexee8833&uname={}&removeavmargin&flagshadow&flagstroke&darkheader&darktriangles&opaqueavatar&rankedscore&onlineindicator=undefined&xpbar&xpbarhex".format(str(a[0]["user_id"])))
        msg = await ctx.send(embed = em)
        await msg.add_reaction('◀️')
        await msg.add_reaction('▶️')
        while True:
            try:
                reaction, user = await ctx.bot.wait_for(event = "reaction_add", timeout = num)
                if user == ctx.author:
                    emoji = str(reaction.emoji)
                    if emoji == '◀️':
                        em = discord.Embed(color = 0XFF8C00, title = "INFORMASI PLAYER STANDARD")
                        em.add_field(name = "Nama PLayer", value = "{}".format(str(a[0]["username"])))
                        em.add_field(name = "Level", value = "{}".format(str(rlevel)))
                        em.add_field(name = "Performance (PP)", value = "{}".format(str(rpp)))
                        em.add_field(name = "Akurasi (ACC)", value = "{}%".format(str(racc)))
                        em.add_field(name = "Peringkat Dunia", value = "#{}".format(str(a[0]["pp_rank"])))
                        em.add_field(name = "Peringkat Negara", value = "#{}".format(str(a[0]["pp_country_rank"])))
                        em.add_field(name = "Homepage Link", value = "https://osu.ppy.sh/users/{}".format(str(a[0]["user_id"])), inline = False)
                        em.add_field(name = "Request By", value = f"{ctx.author.mention}")
                        em.set_footer(text = f"Klik tombol reaction ▶️ untuk melihat Best Performance\n", icon_url=ctx.author.avatar_url)
                        em.set_image(url = "http://lemmmy.pw/osusig/sig.php?colour=hexee8833&uname={}&removeavmargin&flagshadow&flagstroke&darkheader&darktriangles&opaqueavatar&rankedscore&onlineindicator=undefined&xpbar&xpbarhex".format(str(a[0]["user_id"])))
                        await msg.edit(embed = em)
                    elif emoji == '▶️':
                        em = discord.Embed(color = 0XFF8C00, title = "{}'s STANDARD BEST PERFORMANCE".format(str(a[0]["username"])))
                        em.set_thumbnail(url = "https://b.ppy.sh/thumb/{}l.jpg".format(str(c[0]["beatmapset_id"])))
                        em.add_field(name = "Tanggal & Jam", value = "{}".format(str(b[0]["date"])))
                        em.add_field(name = "Judul lagu", value = "{}".format(str(c[0]["title"])), inline = False)
                        em.add_field(name = "Tingkat Kesulitan", value = "{}☆".format(str(rdbm)))
                        em.add_field(name = "Artist", value = "{}".format(str(c[0]["artist"])))
                        em.add_field(name = "Score", value = "{}".format(ttds))
                        em.add_field(name = "Max Combo", value = "{}".format(str(b[0]["maxcombo"])))
                        em.add_field(name = "Performance", value = "{}".format(str(rbpp)))
                        em.add_field(name = "Map link", value = "https://osu.ppy.sh/beatmapsets/{}".format(str(c[0]["beatmapset_id"])), inline = False)
                        em.add_field(name = "Request By", value = f"{ctx.author.mention}")
                        em.set_footer(text = "Klik tombol reaction ◀️ untuk melihat Informasi Player", icon_url=ctx.author.avatar_url)
                        em.set_image(url = "http://lemmmy.pw/osusig/sig.php?colour=hexee8833&uname={}&removeavmargin&flagshadow&flagstroke&darkheader&darktriangles&opaqueavatar&rankedscore&onlineindicator=undefined&xpbar&xpbarhex".format(str(a[0]["user_id"])))
                        await msg.edit(embed = em)
                # if self.bot.user != user:
                #     await msg.remove_reaction(reaction, user)
            except TimeoutError:
                break

    @commands.command()
    async def osutaiko(self, ctx):
        """Mencari informasi player mode taiko"""
        print ("{} Menggunakan command OSU TAIKO".format(ctx.author.name))
        num = 30
        split = ctx.message.content.split(" ")
        nvstarapp = ctx.message.content.replace(split[0] + " ","")
        # STATISTIC PLAYER
        r = requests.get("https://osu.ppy.sh/api/get_user?k=526d85b33ad4b0912850229a00e17e91b612d653&m=1&u={}".format(nvstarapp))
        data = r.text
        data = json.loads(data)
        a = data
        #BEST PERFORMANCE
        r2 = requests.get("https://osu.ppy.sh/api/get_user_best?k=526d85b33ad4b0912850229a00e17e91b612d653&limit=1&m=1&u={}".format(str(a[0]["username"])))
        data2 = r2.text
        data2 = json.loads(data2)
        b = data2
        # BEATMAPS
        r3 = requests.get("https://osu.ppy.sh/api/get_beatmaps?k=526d85b33ad4b0912850229a00e17e91b612d653&b={}".format(str(b[0]["beatmap_id"])))
        data3 = r3.text
        data3 = json.loads(data3)
        c = data3
        # PEMBULATAN KABAWAH UNTUK LEVEL
        level = a[0]["level"]
        flevel = float(level)
        rlevel = int(flevel)
        # PEMBULATAN KEBAWAH UNTUK PERFORMANCE
        pp = a[0]["pp_raw"]
        fpp = float(pp)
        rpp = int(fpp)
        # PEMBULATAN KEBAWAH UNTUK AKURASI
        acc = a[0]["accuracy"]
        facc = float(acc)
        racc = int(facc)
        # PEMBULATAN UNTUK BEST PERFORMANCE
        bpp = b[0]["pp"]
        rbpp = float(bpp)
        rbpp = round(rbpp)
        # PENGAMBILAN 2 ANGKA DI BELAKANG KOMA UNTUK DIFFICULT BEATMAPS
        dbm = c[0]["difficultyrating"]
        rdbm = "{:.2f}".format(float(dbm))
        # PENAMBAHAN TITIK SETIAP 3 DIGIT UNTUK SCORE
        tds = b[0]["score"]
        ttds = re.sub(r"(?<!^)(?=(\d{3})+$)", r".", "{}".format(tds))
        # EMBED BOT UNTUK STATISTIC PLAYER
        em = discord.Embed(color = 0XFF8C00, title = "INFORMASI PLAYER TAIKO")
        em.add_field(name = "Nama PLayer", value = "{}".format(str(a[0]["username"])))
        em.add_field(name = "Level", value = "{}".format(str(rlevel)))
        em.add_field(name = "Performance (PP)", value = "{}".format(str(rpp)))
        em.add_field(name = "Akurasi (ACC)", value = "{}%".format(str(racc)))
        em.add_field(name = "Peringkat Dunia", value = "#{}".format(str(a[0]["pp_rank"])))
        em.add_field(name = "Peringkat Negara", value = "#{}".format(str(a[0]["pp_country_rank"])))
        em.add_field(name = "Homepage Link", value = "https://osu.ppy.sh/users/{}".format(str(a[0]["user_id"])), inline = False)
        em.add_field(name = "Request By", value = f"{ctx.author.mention}")
        em.set_footer(text = "Klik tombol reaction ▶️ untuk melihat Best Performance", icon_url=ctx.author.avatar_url)
        em.set_image(url = "http://lemmmy.pw/osusig/sig.php?colour=hexee8833&uname={}&mode=1&removeavmargin&flagshadow&flagstroke&darkheader&darktriangles&opaqueavatar&rankedscore&onlineindicator=undefined&xpbar&xpbarhex".format(str(a[0]["user_id"] )))
        msg = await ctx.send(embed = em)
        await msg.add_reaction('◀️')
        await msg.add_reaction('▶️')
        while True:
            try:
                reaction, user = await ctx.bot.wait_for(event = "reaction_add", timeout = num)
                if user == ctx.author:
                    emoji = str(reaction.emoji)
                    if emoji == '◀️':
                        em = discord.Embed(color = 0XFF8C00, title = "INFORMASI PLAYER TAIKO")
                        em.add_field(name = "Nama PLayer", value = "{}".format(str(a[0]["username"])))
                        em.add_field(name = "Level", value = "{}".format(str(rlevel)))
                        em.add_field(name = "Performance (PP)", value = "{}".format(str(rpp)))
                        em.add_field(name = "Akurasi (ACC)", value = "{}%".format(str(racc)))
                        em.add_field(name = "Peringkat Dunia", value = "#{}".format(str(a[0]["pp_rank"])))
                        em.add_field(name = "Peringkat Negara", value = "#{}".format(str(a[0]["pp_country_rank"])))
                        em.add_field(name = "Homepage Link", value = "https://osu.ppy.sh/users/{}".format(str(a[0]["user_id"])), inline = False)
                        em.add_field(name = "Request By", value = f"{ctx.author.mention}")
                        em.set_footer(text = "Klik tombol reaction ▶️ untuk melihat Best Performance", icon_url=ctx.author.avatar_url)
                        em.set_image(url = "http://lemmmy.pw/osusig/sig.php?colour=hexee8833&uname={}&mode=1&removeavmargin&flagshadow&flagstroke&darkheader&darktriangles&opaqueavatar&rankedscore&onlineindicator=undefined&xpbar&xpbarhex".format(str(a[0]["user_id"] )))
                        await msg.edit(embed = em)
                    elif emoji == '▶️':
                        em = discord.Embed(color = 0XFF8C00, title = "{}'s TAIKO BEST PERFORMANCE".format(str(a[0]["username"])))
                        em.set_thumbnail(url = "https://b.ppy.sh/thumb/{}l.jpg".format(str(c[0]["beatmapset_id"])))
                        em.add_field(name = "Tanggal & Jam", value = "{}".format(str(b[0]["date"])))
                        em.add_field(name = "Judul lagu", value = "{}".format(str(c[0]["title"])), inline = False)
                        em.add_field(name = "Tingkat Kesulitan", value = "{}☆".format(str(rdbm)))
                        em.add_field(name = "Artist", value = "{}".format(str(c[0]["artist"])))
                        em.add_field(name = "Score", value = "{}".format(ttds))
                        em.add_field(name = "Max Combo", value = "{}".format(str(b[0]["maxcombo"])))
                        em.add_field(name = "Performance", value = "{}".format(str(rbpp)))
                        em.add_field(name = "Map link", value = "https://osu.ppy.sh/beatmapsets/{}".format(str(c[0]["beatmapset_id"])), inline = False)
                        em.add_field(name = "Request By", value = f"{ctx.author.mention}")
                        em.set_footer(text = "Klik tombol reaction ◀️ untuk melihat Informasi Player", icon_url=ctx.author.avatar_url)
                        em.set_image(url = "http://lemmmy.pw/osusig/sig.php?colour=hexee8833&uname={}&mode=1&removeavmargin&flagshadow&flagstroke&darkheader&darktriangles&opaqueavatar&rankedscore&onlineindicator=undefined&xpbar&xpbarhex".format(str(a[0]["user_id"] )))
                        await msg.edit(embed = em)
                # if self.bot.user != user:
                #     await msg.remove_reaction(reaction, user)
            except TimeoutError:
                break

    @commands.command()
    async def osuctb(self, ctx):
        """Mencari informasi player mode catch the beat"""
        print ("{} Menggunakan command OSU CATCH THE BEAT".format(ctx.author.name))
        num = 30
        split = ctx.message.content.split(" ")
        nvstarapp = ctx.message.content.replace(split[0] + " ","")
        # STATISTIC PLAYER
        r = requests.get("https://osu.ppy.sh/api/get_user?k=526d85b33ad4b0912850229a00e17e91b612d653&m=2&u={}".format(nvstarapp))
        data = r.text
        data = json.loads(data)
        a = data
        #BEST PERFORMANCE
        r2 = requests.get("https://osu.ppy.sh/api/get_user_best?k=526d85b33ad4b0912850229a00e17e91b612d653&limit=1&m=2&u={}".format(str(a[0]["username"])))
        data2 = r2.text
        data2 = json.loads(data2)
        b = data2
        # BEATMAPS
        r3 = requests.get("https://osu.ppy.sh/api/get_beatmaps?k=526d85b33ad4b0912850229a00e17e91b612d653&b={}".format(str(b[0]["beatmap_id"])))
        data3 = r3.text
        data3 = json.loads(data3)
        c = data3
        # PEMBULATAN KABAWAH UNTUK LEVEL
        level = a[0]["level"]
        flevel = float(level)
        rlevel = int(flevel)
        # PEMBULATAN KEBAWAH UNTUK PERFORMANCE
        pp = a[0]["pp_raw"]
        fpp = float(pp)
        rpp = int(fpp)
        # PEMBULATAN KEBAWAH UNTUK AKURASI
        acc = a[0]["accuracy"]
        facc = float(acc)
        racc = int(facc)
        # PEMBULATAN UNTUK BEST PERFORMANCE
        bpp = b[0]["pp"]
        rbpp = float(bpp)
        rbpp = round(rbpp)
        # PENGAMBILAN 2 ANGKA DI BELAKANG KOMA UNTUK DIFFICULT BEATMAPS
        dbm = c[0]["difficultyrating"]
        rdbm = "{:.2f}".format(float(dbm))
        # PENAMBAHAN TITIK SETIAP 3 DIGIT UNTUK SCORE
        tds = b[0]["score"]
        ttds = re.sub(r"(?<!^)(?=(\d{3})+$)", r".", "{}".format(tds))
        # EMBED BOT UNTUK STATISTIC PLAYER
        em = discord.Embed(color = 0XFF8C00, title = "INFORMASI PLAYER CATCH THE BEAT")
        em.add_field(name = "Nama PLayer", value = "{}".format(str(a[0]["username"])))
        em.add_field(name = "Level", value = "{}".format(str(rlevel)))
        em.add_field(name = "Performance (PP)", value = "{}".format(str(rpp)))
        em.add_field(name = "Akurasi (ACC)", value = "{}%".format(str(racc)))
        em.add_field(name = "Peringkat Dunia", value = "#{}".format(str(a[0]["pp_rank"])))
        em.add_field(name = "Peringkat Negara", value = "#{}".format(str(a[0]["pp_country_rank"])))
        em.add_field(name = "Homepage Link", value = "https://osu.ppy.sh/users/{}".format(str(a[0]["user_id"])), inline = False)
        em.add_field(name = "Request By", value = f"{ctx.author.mention}")
        em.set_footer(text = "Klik tombol reaction ▶️ untuk melihat Best Performance", icon_url=ctx.author.avatar_url)
        em.set_image(url = "http://lemmmy.pw/osusig/sig.php?colour=hexee8833&uname={}&mode=2&removeavmargin&flagshadow&flagstroke&darkheader&darktriangles&opaqueavatar&rankedscore&onlineindicator=undefined&xpbar&xpbarhex".format(str(a[0]["user_id"] )))
        msg = await ctx.send(embed = em)
        await msg.add_reaction('◀️')
        await msg.add_reaction('▶️')
        while True:
            try:
                reaction, user = await ctx.bot.wait_for(event = "reaction_add", timeout = num)
                if user == ctx.author:
                    emoji = str(reaction.emoji)
                    if emoji == '◀️':
                        em = discord.Embed(color = 0XFF8C00, title = "INFORMASI PLAYER CATCH THE BEAT")
                        em.add_field(name = "Nama PLayer", value = "{}".format(str(a[0]["username"])))
                        em.add_field(name = "Level", value = "{}".format(str(rlevel)))
                        em.add_field(name = "Performance (PP)", value = "{}".format(str(rpp)))
                        em.add_field(name = "Akurasi (ACC)", value = "{}%".format(str(racc)))
                        em.add_field(name = "Peringkat Dunia", value = "#{}".format(str(a[0]["pp_rank"])))
                        em.add_field(name = "Peringkat Negara", value = "#{}".format(str(a[0]["pp_country_rank"])))
                        em.add_field(name = "Homepage Link", value = "https://osu.ppy.sh/users/{}".format(str(a[0]["user_id"])), inline = False)
                        em.add_field(name = "Request By", value = f"{ctx.author.mention}")
                        em.set_footer(text = "Klik tombol reaction ▶️ untuk melihat Best Performance", icon_url=ctx.author.avatar_url)
                        em.set_image(url = "http://lemmmy.pw/osusig/sig.php?colour=hexee8833&uname={}&mode=2&removeavmargin&flagshadow&flagstroke&darkheader&darktriangles&opaqueavatar&rankedscore&onlineindicator=undefined&xpbar&xpbarhex".format(str(a[0]["user_id"] )))
                        await msg.edit(embed = em)
                    elif emoji == '▶️':
                        em = discord.Embed(color = 0XFF8C00, title = "{}'s CATCH THE BEAT BEST PERFORMANCE".format(str(a[0]["username"])))
                        em.set_thumbnail(url = "https://b.ppy.sh/thumb/{}l.jpg".format(str(c[0]["beatmapset_id"])))
                        em.add_field(name = "Tanggal & Jam", value = "{}".format(str(b[0]["date"])))
                        em.add_field(name = "Judul lagu", value = "{}".format(str(c[0]["title"])), inline = False)
                        em.add_field(name = "Tingkat Kesulitan", value = "{}☆".format(str(rdbm)))
                        em.add_field(name = "Artist", value = "{}".format(str(c[0]["artist"])))
                        em.add_field(name = "Score", value = "{}".format(ttds))
                        em.add_field(name = "Max Combo", value = "{}".format(str(b[0]["maxcombo"])))
                        em.add_field(name = "Performance", value = "{}".format(str(rbpp)))
                        em.add_field(name = "Map link", value = "https://osu.ppy.sh/beatmapsets/{}".format(str(c[0]["beatmapset_id"])), inline = False)
                        em.add_field(name = "Request By", value = f"{ctx.author.mention}")
                        em.set_footer(text = "Klik tombol reaction ◀️ untuk melihat Informasi Player", icon_url=ctx.author.avatar_url)
                        em.set_image(url = "http://lemmmy.pw/osusig/sig.php?colour=hexee8833&uname={}&mode=2&removeavmargin&flagshadow&flagstroke&darkheader&darktriangles&opaqueavatar&rankedscore&onlineindicator=undefined&xpbar&xpbarhex".format(str(a[0]["user_id"] )))
                        await msg.edit(embed = em)
                # if self.bot.user != user:
                #     await msg.remove_reaction(reaction, user)
            except TimeoutError:
                break

    @commands.command()
    async def osumania(self, ctx):
        """Mencari informasi player mode mania"""
        print ("{} Menggunakan command OSU MANIA".format(ctx.author.name))
        num = 30
        split = ctx.message.content.split(" ")
        nvstarapp = ctx.message.content.replace(split[0] + " ","")
        # STATISTIC PLAYER
        r = requests.get("https://osu.ppy.sh/api/get_user?k=526d85b33ad4b0912850229a00e17e91b612d653&m=3&u={}".format(nvstarapp))
        data = r.text
        data = json.loads(data)
        a = data
        #BEST PERFORMANCE
        r2 = requests.get("https://osu.ppy.sh/api/get_user_best?k=526d85b33ad4b0912850229a00e17e91b612d653&limit=1&m=3&u={}".format(str(a[0]["username"])))
        data2 = r2.text
        data2 = json.loads(data2)
        b = data2
        # BEATMAPS
        r3 = requests.get("https://osu.ppy.sh/api/get_beatmaps?k=526d85b33ad4b0912850229a00e17e91b612d653&b={}".format(str(b[0]["beatmap_id"])))
        data3 = r3.text
        data3 = json.loads(data3)
        c = data3
        # PEMBULATAN KABAWAH UNTUK LEVEL
        level = a[0]["level"]
        flevel = float(level)
        rlevel = int(flevel)
        # PEMBULATAN KEBAWAH UNTUK PERFORMANCE
        pp = a[0]["pp_raw"]
        fpp = float(pp)
        rpp = int(fpp)
        # PEMBULATAN KEBAWAH UNTUK AKURASI
        acc = a[0]["accuracy"]
        facc = float(acc)
        racc = int(facc)
        # PEMBULATAN UNTUK BEST PERFORMANCE
        bpp = b[0]["pp"]
        rbpp = float(bpp)
        rbpp = round(rbpp)
        # PENGAMBILAN 2 ANGKA DI BELAKANG KOMA UNTUK DIFFICULT BEATMAPS
        dbm = c[0]["difficultyrating"]
        rdbm = "{:.2f}".format(float(dbm))
        # PENAMBAHAN TITIK SETIAP 3 DIGIT UNTUK SCORE
        tds = b[0]["score"]
        ttds = re.sub(r"(?<!^)(?=(\d{3})+$)", r".", "{}".format(tds))
        # EMBED BOT UNTUK STATISTIC PLAYER
        em = discord.Embed(color = 0XFF8C00, title = "INFORMASI PLAYER MANIA")
        em.set_thumbnail(url = "http://s.ppy.sh/a/{}".format(str(a[0]["user_id"])))
        em.add_field(name = "Nama PLayer", value = "{}".format(str(a[0]["username"])))
        em.add_field(name = "Level", value = "{}".format(str(rlevel)))
        em.add_field(name = "Performance (PP)", value = "{}".format(str(rpp)))
        em.add_field(name = "Akurasi (ACC)", value = "{}%".format(str(racc)))
        em.add_field(name = "Peringkat Dunia", value = "#{}".format(str(a[0]["pp_rank"])))
        em.add_field(name = "Peringkat Negara", value = "#{}".format(str(a[0]["pp_country_rank"])))
        em.add_field(name = "Homepage Link", value = "https://osu.ppy.sh/users/{}".format(str(a[0]["user_id"])), inline = False)
        em.add_field(name = "Request By", value = f"{ctx.author.mention}")
        em.set_footer(text = "Klik tombol reaction ▶️ untuk melihat Best Performance", icon_url=ctx.author.avatar_url)
        em.set_image(url = "http://lemmmy.pw/osusig/sig.php?colour=hexee8833&uname={}&mode=3&removeavmargin&flagshadow&flagstroke&darkheader&darktriangles&opaqueavatar&rankedscore&onlineindicator=undefined&xpbar&xpbarhex".format(str(a[0]["user_id"] )))
        msg = await ctx.send(embed = em)
        await msg.add_reaction('◀️')
        await msg.add_reaction('▶️')
        while True:
            try:
                reaction, user = await ctx.bot.wait_for(event = "reaction_add", timeout = num)
                if user == ctx.author:
                    emoji = str(reaction.emoji)
                    if emoji == '◀️':
                        em = discord.Embed(color = 0XFF8C00, title = "INFORMASI PLAYER MANIA")
                        em.add_field(name = "Nama PLayer", value = "{}".format(str(a[0]["username"])))
                        em.add_field(name = "Level", value = "{}".format(str(rlevel)))
                        em.add_field(name = "Performance (PP)", value = "{}".format(str(rpp)))
                        em.add_field(name = "Akurasi (ACC)", value = "{}%".format(str(racc)))
                        em.add_field(name = "Peringkat Dunia", value = "#{}".format(str(a[0]["pp_rank"])))
                        em.add_field(name = "Peringkat Negara", value = "#{}".format(str(a[0]["pp_country_rank"])))
                        em.add_field(name = "Homepage Link", value = "https://osu.ppy.sh/users/{}".format(str(a[0]["user_id"])), inline = False)
                        em.add_field(name = "Request By", value = f"{ctx.author.mention}")
                        em.set_footer(text = "Klik tombol reaction ▶️ untuk melihat Best Performance")
                        em.set_image(url = "http://lemmmy.pw/osusig/sig.php?colour=hexee8833&uname={}&mode=3&removeavmargin&flagshadow&flagstroke&darkheader&darktriangles&opaqueavatar&rankedscore&onlineindicator=undefined&xpbar&xpbarhex".format(str(a[0]["user_id"] )))
                        await msg.edit(embed = em)
                    elif emoji == '▶️':
                        em = discord.Embed(color = 0XFF8C00, title = "{}'s MANIA BEST PERFORMANCE".format(str(a[0]["username"])))
                        em.add_field(name = "Tanggal & Jam", value = "{}".format(str(b[0]["date"])))
                        em.add_field(name = "Judul lagu", value = "{}".format(str(c[0]["title"])), inline = False)
                        em.add_field(name = "Tingkat Kesulitan", value = "{}☆".format(str(rdbm)))
                        em.add_field(name = "Artist", value = "{}".format(str(c[0]["artist"])))
                        em.add_field(name = "Score", value = "{}".format(ttds))
                        em.add_field(name = "Max Combo", value = "{}".format(str(b[0]["maxcombo"])))
                        em.add_field(name = "Performance", value = "{}".format(str(rbpp)))
                        em.add_field(name = "Map link", value = "https://osu.ppy.sh/beatmapsets/{}".format(str(c[0]["beatmapset_id"])), inline = False)
                        em.add_field(name = "Request By", value = f"{ctx.author.mention}")
                        em.set_footer(text = "Klik tombol reaction ◀️ untuk melihat Informasi Player")
                        em.set_image(url = "http://lemmmy.pw/osusig/sig.php?colour=hexee8833&uname={}&mode=3&removeavmargin&flagshadow&flagstroke&darkheader&darktriangles&opaqueavatar&rankedscore&onlineindicator=undefined&xpbar&xpbarhex".format(str(a[0]["user_id"] )))
                        await msg.edit(embed = em)
                # if self.bot.user != user:
                #     await msg.remove_reaction(reaction, user)
            except TimeoutError:
                break