import asyncio, discord, base64, binascii, re, math, shutil, tempfile, os
from   discord.ext import commands
from   Cogs import Nullify, DL, Message
from   PIL import Image

def setup(bot):
    # Add the bot and deps
    settings = bot.get_cog("Settings")
    bot.add_cog(Encode(bot, settings))

class Encode(commands.Cog):

    # Init with the bot reference
    def __init__(self, bot, settings):
        self.bot = bot
        self.settings = settings
        self.regex = re.compile(r"(http|ftp|https)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?")

    def suppressed(self, guild, msg):
        # Check if we're suppressing @here and @everyone mentions
        if self.settings.getServerStat(guild, "SuppressMentions"):
            return Nullify.clean(msg)
        else:
            return msg

    async def download(self, url):
        url = url.strip("<>")
        # Set up a temp directory
        dirpath = tempfile.mkdtemp()
        tempFileName = url.rsplit('/', 1)[-1]
        # Strip question mark
        tempFileName = tempFileName.split('?')[0]
        filePath = dirpath + "/" + tempFileName
        rImage = None
        try:
            rImage = await DL.async_dl(url)
        except:
            pass
        if not rImage:
            self.remove(dirpath)
            return None
        with open(filePath, 'wb') as f:
            f.write(rImage)
        # Check if the file exists
        if not os.path.exists(filePath):
            self.remove(dirpath)
            return None
        return filePath
        
    def remove(self, path):
        if not path == None and os.path.exists(path):
            shutil.rmtree(os.path.dirname(path), ignore_errors=True)

    # Helper methods
    def _to_bytes(self, in_string):
        return in_string.encode('utf-8')
    
    def _to_string(self, in_bytes):
        return in_bytes.decode('utf-8')

    # Check hex value
    def _check_hex(self, hex_string):
        # Remove 0x/0X
        hex_string = hex_string.replace("0x", "").replace("0X", "")
        hex_string = re.sub(r'[^0-9A-Fa-f]+', '', hex_string)
        return hex_string

    # To base64 methods
    def _ascii_to_base64(self, ascii_string):
        ascii_bytes = self._to_bytes(ascii_string)
        base_64     = base64.b64encode(ascii_bytes)
        return self._to_string(base_64)

    def _hex_to_base64(self, hex_string):
        hex_string    = self._check_hex(hex_string)
        hex_s_bytes   = self._to_bytes(hex_string)
        hex_bytes     = binascii.unhexlify(hex_s_bytes)
        base64_bytes  = base64.b64encode(hex_bytes)
        return self._to_string(base64_bytes)

    # To ascii methods
    def _hex_to_ascii(self, hex_string):
        hex_string  = self._check_hex(hex_string)
        hex_bytes   = self._to_bytes(hex_string)
        ascii_bytes = binascii.unhexlify(hex_bytes)
        return self._to_string(ascii_bytes)

    def _base64_to_ascii(self, base64_string):
        base64_bytes  = self._to_bytes(base64_string)
        ascii_bytes   = base64.b64decode(base64_bytes)
        return self._to_string(ascii_bytes)

    # To hex methods
    def _ascii_to_hex(self, ascii_string):
        ascii_bytes = self._to_bytes(ascii_string)
        hex_bytes   = binascii.hexlify(ascii_bytes)
        return self._to_string(hex_bytes)

    def _base64_to_hex(self, base64_string):
        b64_string = self._to_bytes(base64_string)
        base64_bytes = base64.b64decode(b64_string)
        hex_bytes    = binascii.hexlify(base64_bytes)
        return self._to_string(hex_bytes)

    def _rgb_to_hex(self, r, g, b):
        return "#{:02x}{:02x}{:02x}".format(r,g,b).upper()

    def _hex_to_rgb(self, _hex):
        _hex = _hex.lower().replace("#", "").replace("0x","")
        l_hex = len(_hex)
        return tuple(int(_hex[i:i + l_hex // 3], 16) for i in range(0, l_hex, l_hex // 3))

    def _hex_to_cmyk(self, _hex):
        return self._rgb_to_cmyk(*self._hex_to_rgb(_hex))

    def _cmyk_to_hex(self, c, m, y, k):
        return self._rgb_to_hex(*self._cmyk_to_rgb(c,m,y,k))

    def _cmyk_to_rgb(self, c, m, y, k):
        c, m, y, k = [float(x)/100.0 for x in tuple([c, m, y, k])]
        return tuple([round(255.0 - ((min(1.0, x * (1.0 - k) + k)) * 255.0)) for x in tuple([c, m, y])])

    def _rgb_to_cmyk(self, r, g, b):
        c, m, y = [1 - x/255 for x in tuple([r, g, b])]
        min_cmy = min(c, m, y)
        return tuple([0,0,0,100]) if all(x == 0 for x in [r, g, b]) else tuple([round(x*100) for x in [(x - min_cmy) / (1 - min_cmy) for x in tuple([c, m, y])] + [min_cmy]])

    def _hex_int_to_tuple(self, _hex):
        return (_hex >> 16 & 0xFF, _hex >> 8 & 0xFF, _hex & 0xFF)

    @commands.command()
    async def color(self, ctx, *, value = None):
        """Melihat warna dengan kode HTML, RGB, dan CMYK
        Dengan format:

        Contoh:
        acx color #3399cc
        acx color rgb(3, 4, 5)
        acx color cmyk(1, 2, 3, 4)
        acx color 0xFF00FF
        """
        em = discord.Embed(color = 0XFF8C00, description =  "> Melihat informasi kode warna.\n> \n"
                                                            "> **Panduan pengunaan**\n"
                                                            "> `{}color [value]`\n> \n"
                                                            "> **Value Format**\n"
                                                            "> `{}color #3399cc` HTML Format\n"
                                                            "> `{}color rgb(3, 4, 5)` RGB Format\n"
                                                            "> `{}color cmyk(1, 2, 3, 4)` CMYK Format\n"
                                                            "> `{}color 0xFF00FF` HEX Format"
                                                            .format(ctx.prefix,
                                                                    ctx.prefix,
                                                                    ctx.prefix,
                                                                    ctx.prefix,
                                                                    ctx.prefix))
        em.set_author(name = "Color", icon_url = "https://cdn.discordapp.com/attachments/518118753226063887/725569194304733435/photo.jpg")
        em.set_footer(text = "Saat mengetik command, tanda [] tidak usah digunakan.\nHelp command color\nRequest By : {}".format(ctx.author.name), icon_url = f"{ctx.author.avatar_url}")
        if not value: return await ctx.send(embed = em)
        # Let's replace commas, and parethesis with spaces, then split on whitespace
        values = value.replace(","," ").replace("("," ").replace(")"," ").replace("%"," ").split()
        color_values  = []
        for x in values:
            if x.lower().startswith(("0x","#")) or any((y in x.lower() for y in "abcdef")):
                # We likely have a hex value
                try: color_values.append(int(x.lower().replace("#","").replace("0x",""),16))
                except: pass # Bad value - ignore
            else:
                # Try to convert it to an int
                try: color_values.append(int(x))
                except: pass # Bad value - ignore
        original_type = "hex" if len(color_values) == 1 else "rgb" if len(color_values) == 3 else "cmyk" if len(color_values) == 4 else None
        em = discord.Embed(color = 0XFF8C00, description =  "> Kode warna salah.\n"
                                                            "> `HTML` membutuhkan `1`.\n"
                                                            "> `RBG` membutuhkan `3`.\n"
                                                            "> `CMYK` membutuhkan `4`")
        em.set_author(name = "Oops ada yang salah!", icon_url = "https://cdn.discordapp.com/attachments/518118753226063887/725569194304733435/photo.jpg")
        em.set_footer(text = f"Request By : {ctx.author.name}", icon_url = f"{ctx.author.avatar_url}")
        if original_type == None: return await ctx.send(embed = em)
        # Verify values
        max_val = int("FFFFFF",16) if original_type == "hex" else 255 if original_type == "rgb" else 100
        if not all((0 <= x <= max_val for x in color_values)):
            em = discord.Embed(color = 0XFF8C00, description =  "> Kode warna diluar batas.\n"
                                                                "> `HTML` `#000000` sampai `#FFFFFF`.\n"
                                                                "> `RBG` `0` sampai `255`.\n"
                                                                "> `CMYK` `0` sampai `100`")
            em.set_author(name = "Oops ada yang salah!", icon_url = "https://cdn.discordapp.com/attachments/518118753226063887/725569194304733435/photo.jpg")
            em.set_footer(text = f"Request By : {ctx.author.name}", icon_url = f"{ctx.author.avatar_url}")
            return await ctx.send(embed = em)
        fields = []
        # Organize the data into the Message format expectations
        if original_type == "hex":
            hex_value = "#"+hex(color_values[0]).replace("0x","").rjust(6,"0").upper()
            title = "Color {}".format(hex_value)
            color = color_values[0]
            fields.extend([
                {"name":"RGB","value":"rgb({}, {}, {})".format(*self._hex_to_rgb(hex_value))},
                {"name":"CMYK","value":"cmyk({}, {}, {}, {})".format(*self._hex_to_cmyk(hex_value))}
                ])
        elif original_type == "rgb":
            title = "Color rgb({}, {}, {})".format(*color_values)
            color = int(self._rgb_to_hex(*color_values).replace("#",""),16)
            fields.extend([
                {"name":"Hex","value":self._rgb_to_hex(*color_values)},
                {"name":"CMYK","value":"cmyk({}, {}, {}, {})".format(*self._rgb_to_cmyk(*color_values))}
            ])
        else:
            title = "Color cmyk({}, {}, {}, {})".format(*color_values)
            color = int(self._cmyk_to_hex(*color_values).replace("#",""),16)
            fields.extend([
                {"name":"Hex","value":self._cmyk_to_hex(*color_values)},
                {"name":"RGB","value":"rgb({}, {}, {})".format(*self._cmyk_to_rgb(*color_values))}
            ])
        # Create the image
        file_path = "images/colornow.png"
        try:
            image = Image.new(mode="RGB",size=(512,256),color=self._hex_int_to_tuple(color))
            image.save(file_path)
            await Message.Embed(title=title,color=color,fields=fields,file=file_path).send(ctx)
        except:
            pass
        if os.path.exists(file_path):
            os.remove(file_path)

    def get_slide(self, start_addr = 0):
        # Setup our temp vars
        m1 = int("0x100000",16)
        m2 = int("0x200000",16)
        
        slide = int(math.ceil(( start_addr - m1 ) / m2))
        return 0 if slide < 0 else slide

    def get_available(self, line_list = []):
        available = []
        for line in line_list:
            line_split = [x for x in line.split(" ") if len(x)]
            if not len(line_split):
                continue
            if len(line_split) == 1:
                # No spaces - let's make sure it's hex and add it
                try: available.append({"start":int(line_split[0],16)})
                except: continue
            elif line_split[0].lower() == "available":
                # If our first item is "available", let's convert the others into ints
                new_line = []
                for x in line_split:
                    new_line.extend(x.split("-"))
                if len(new_line) < 3:
                    # Not enough info
                    continue
                try:
                    available.append({
                        "start":int(new_line[1],16),
                        "end":int(new_line[2],16),
                        "size": (int(new_line[2],16)-int(new_line[1],16))/4096 if len(new_line) < 4 else int(new_line[3],16)
                        })
                except: continue
        return available

    # @commands.command(pass_context=True)
    # async def slide(self, ctx, *, input_hex = None):
    #     """Calculates your slide value for Clover based on an input address (in hex)."""
    #     if input_hex == None and len(ctx.message.attachments) == 0: # No info passed - bail!
    #         return await ctx.send("Usage: `{}slide [hex address]`".format(ctx.prefix))
    #     # Check for urls
    #     matches = [] if input_hex == None else list(re.finditer(self.regex, input_hex))
    #     slide_url = ctx.message.attachments[0].url if input_hex == None else None if not len(matches) else matches[0].group(0)
    #     if slide_url:
    #         path = await self.download(slide_url)
    #         if not path: # It was just an attachment - bail
    #             return await ctx.send("Looks like I couldn't download that link...")
    #         # Got something - let's load it as text
    #         with open(path,"rb") as f:
    #             input_hex = f.read().decode("utf-8","ignore").replace("\x00","").replace("\r","")
    #         self.remove(path)
    #     # At this point - we might have a url, a table of data, or a single hex address
    #     # Let's split by newlines first, then by spaces
    #     available = self.get_available(input_hex.replace("`","").split("\n"))
    #     if not len(available):
    #         return await ctx.send("No available space was found in the passed values.")
    #     # Let's sort our available by their size - then walk the list until we find the
    #     # first valid slide
    #     available = sorted(available, key=lambda x:x.get("size",0),reverse=True)
    #     slides = []
    #     for x in available:
    #         slide = self.get_slide(x["start"])
    #         if slide >= 256 or x["start"] == 0: continue # Out of range
    #         # Got a good one - spit it out
    #         hex_str = "{:x}".format(x["start"]).upper()
    #         hex_str = "0"*(len(hex_str)%2)+hex_str
    #         slides.append(("0x"+hex_str,slide))
    #         # return await ctx.send("Slide value for starting address of 0x{}:\n```\nslide={}\n```".format(hex_str.upper(),slide))
    #     if not len(slides):
    #         # If we got here - we have no applicable slides
    #         return await ctx.send("No valid slide values were found for the passed info.")
    #     # Format the slides
    #     pad = max([len(x[0]) for x in slides])
    #     await ctx.send("**Applicable Slide Values:**\n```\n{}\n```".format("\n".join(["{}: slide={}".format(x[0].rjust(pad),x[1]) for x in slides])))
    
    # @commands.command(pass_context=True)
    # async def hexswap(self, ctx, *, input_hex = None):
    #     """Byte swaps the passed hex value."""
    #     if input_hex == None:
    #         await ctx.send("Usage: `{}hexswap [input_hex]`".format(ctx.prefix))
    #         return
    #     input_hex = self._check_hex(input_hex)
    #     if not len(input_hex):
    #         await ctx.send("Malformed hex - try again.")
    #         return
    #     # Normalize hex into pairs
    #     input_hex = list("0"*(len(input_hex)%2)+input_hex)
    #     hex_pairs = [input_hex[i:i + 2] for i in range(0, len(input_hex), 2)]
    #     hex_rev = hex_pairs[::-1]
    #     hex_str = "".join(["".join(x) for x in hex_rev])
    #     await ctx.send(hex_str.upper())
        
    @commands.command(pass_context=True)
    async def hexdec(self, ctx, *, input_hex = None):
        """Convert Hex menjadi Decimal."""
        if input_hex == None:
            em = discord.Embed(color = 0XFF8C00, description =  "Convert Hex menjadi Decimal\n\n"
                                                                "**Panduan**\n"
                                                               f"`{ctx.prefix}hexdec [hex]`")
            em.set_footer(text = "{}#{}".format(ctx.author.name, ctx.author.discriminator),
                          icon_url = f"{ctx.author.avatar_url}")
            await ctx.send(embed = em)
            return
        
        input_hex = self._check_hex(input_hex)
        if not len(input_hex):
            msg = "┐(￣ヘ￣;)┌\nFormat salah, coba lagi!"
            em = discord.Embed(color = 0XFF8C00, description = msg)
            em.set_footer(text = "{}#{}".format(ctx.author.name, ctx.author.discriminator),
                          icon_url = "{}".format(ctx.author.avatar_url))
            await ctx.send(embed = em)
            return
        
        try:
            dec = int(input_hex, 16)
        except Exception:
            msg = "Aku tidak dapat melakukan konversi itu!"
            em = discord.Embed(color = 0XFF8C00, description = msg)
            em.set_footer(text = "{}#{}".format(ctx.author.name, ctx.author.discriminator),
                          icon_url = "{}".format(ctx.author.avatar_url))
            await ctx.send(embed = em)
            return  
        em = discord.Embed(color = 0XFF8C00, description = "```{}```".format(dec))
        em.set_footer(text = "{}#{}".format(ctx.author.name, ctx.author.discriminator),
                      icon_url = "{}".format(ctx.author.avatar_url))
        await ctx.send(embed = em)

    @commands.command(pass_context=True)
    async def dechex(self, ctx, *, input_dec = None):
        """Convert Decimal menjadi Hex."""
        if input_dec == None:
            em = discord.Embed(color = 0XFF8C00, description =  "Convert Decimal menjadi Hex"
                                                                "**Panduan**\n"
                                                               f"`{ctx.prefix}dechex [Decimal]`")
            em.set_footer(text = "{}#{}".format(ctx.author.name, ctx.author.discriminator),
                          icon_url = "{}".format(ctx.author.avatar_url))
            await ctx.send(embed = em)
            return

        try:
            input_dec = int(input_dec)
        except Exception:
            msg = "Input harus berupa bilangan angka"
            em = discord.Embed(color = 0XFF8C00, description =  msg)
            em.set_footer(text = "{}#{}".format(ctx.author.name, ctx.author.discriminator),
                          icon_url = "{}".format(ctx.author.avatar_url))
            await ctx.send(embed = em)
            return
        min_length = 2
        hex_str = "{:x}".format(input_dec).upper()
        hex_str = "0"*(len(hex_str)%min_length)+hex_str
        em = discord.Embed(color = 0XFF8C00, description = "```0x```"+hex_str)
        em.set_footer(text = "{}#{}".format(ctx.author.name, ctx.author.discriminator),
                      icon_url = "{}".format(ctx.author.avatar_url))
        await ctx.send(embed = em)
        await ctx.send("0x"+hex_str)


    @commands.command(pass_context=True)
    async def strbin(self, ctx, *, input_string = None):
        """Convert string (text) menjadi binary"""
        if input_string == None:
            em = discord.Embed(color = 0XFF8C00, description = "Convert string (text) menjadi binary\n\n"
                                                               "**Panduan**\n"
                                                               "`{}strbin [input_string]`".format(ctx.prefix))
            em.set_footer(text = "{}#{}".format(ctx.author.name, ctx.author.discriminator),
                          icon_url = "{}".format(ctx.author.avatar_url))
            await ctx.send(embed = em)
            return
        msg = ''.join('{:08b}'.format(ord(c)) for c in input_string)
        # Format into blocks:
        # - First split into chunks of 8
        msg_list = re.findall('........?', msg)
        # Now we format!
        msg = "```\n"
        msg += " ".join(msg_list)
        msg += "```"    
        if len(msg) > 1000:
            em = discord.Embed(color = 0XFF8C00, description =  "> Terlalu banyak bilangan `1` dan `0` yang harus ku berikan.\n"
                                                                "> Cobalah masukan text yang lebih singkat")
            em.set_footer(text = f"Request By : {ctx.author.name}", icon_url = f"{ctx.author.avatar_url}")
            await ctx.send(embed = em)
            return
        em = discord.Embed(color = 0XFF8C00, description =  "**Input**\n```{}```\n" 
                                                            "**Output**\n "
                                                            .format(input_string) + msg)
        em.set_author(name = "Hasil Binary", icon_url = "https://cdn.discordapp.com/attachments/518118753226063887/725569194304733435/photo.jpg")
        em.set_footer(text = f"Request By : {ctx.author.name}", icon_url = f"{ctx.author.avatar_url}")
        await ctx.send(embed = em)

    @commands.command(pass_context=True)
    async def binstr(self, ctx, *, input_binary = None):
        """Convert input binary menjadi string (text)."""
        if input_binary == None:
            em = discord.Embed(color = 0XFF8C00, description =  "> **Panduan pengunaan**\n"
                                                               f"> `{ctx.prefix}binstr [text]`")
            em.set_author(name = "Help command binstr", icon_url = "https://cdn.discordapp.com/attachments/518118753226063887/725569194304733435/photo.jpg")
            em.set_footer(text = f"Request By : {ctx.author.name}", icon_url = f"{ctx.author.avatar_url}")
            await ctx.send(embed = em)
            return
        # Clean the string
        new_bin = ""
        for char in input_binary:
            if char == "0" or char == "1":
                new_bin += char
        if not len(new_bin):
            em = discord.Embed(color = 0XFF8C00, description =  "> **Panduan pengunaan**\n"
                                                               f"> `{ctx.prefix}binstr [binary]`")
            em.set_author(name = "Help command binstr", icon_url = "https://cdn.discordapp.com/attachments/518118753226063887/725569194304733435/photo.jpg")
            em.set_footer(text = f"Request By : {ctx.author.name}", icon_url = f"{ctx.author.avatar_url}")
            await ctx.send(embed = em)
            return
        msg = ''.join(chr(int(new_bin[i:i+8], 2)) for i in range(0, len(new_bin), 8))
        em = discord.Embed(color = 0XFF8C00, description =  "**Input**\n```{}```\n" 
                                                            "**Output**\n```{}```"
                                                            .format(input_binary,
                                                                    msg))
        em.set_author(name = "Hasil Binary", icon_url = "https://cdn.discordapp.com/attachments/518118753226063887/725569194304733435/photo.jpg")
        em.set_footer(text = f"Request By : {ctx.author.name}", icon_url = f"{ctx.author.avatar_url}")
        await ctx.send(embed=em)

    # @commands.command(pass_context=True)
    # async def binint(self, ctx, *, input_binary = None):
    #     """Converts the input binary to its integer representation."""
    #     if input_binary == None:
    #         await ctx.send("Usage: `{}binint [input_binary]`".format(ctx.prefix))
    #         return
    #     try:
    #         msg = int(input_binary, 2)
    #     except Exception:
    #         msg = "I couldn't make that conversion!"
    #     await ctx.send(msg)

    # @commands.command(pass_context=True)
    # async def intbin(self, ctx, *, input_int = None):
    #     """Converts the input integer to its binary representation."""
    #     if input_int == None:
    #         await ctx.send("Usage: `{}intbin [input_int]`".format(ctx.prefix))
    #         return
    #     try:
    #         input_int = int(input_int)
    #     except Exception:
    #         await ctx.send("Input must be an integer.")
    #         return

    #     await ctx.send("{:08b}".format(input_int))

    

    @commands.command(pass_context=True)
    async def encode(self, ctx, from_type = None , to_type = None, *, value = None):
        """Mengubah data dari ascii <--> hex <--> base64."""

        if value == None or from_type == None or to_type == None:
            em = discord.Embed(color = 0XFF8C00, description =  "> Mengubah data ascii <--> hex <--> base64\n> \n"
                                                                "> **Panduan pengunaan**\n"
                                                                "> `{} encode [from_type] [to_type] [message]`\n> \n"
                                                                "> **TYPE**\n"
                                                                "> `• ascii`\n"
                                                                "> `• hex`\n"
                                                                "> `• base64`"
                                                                .format(ctx.prefix))
            em.set_author(name = "Help command binstr", icon_url = "https://cdn.discordapp.com/attachments/518118753226063887/725569194304733435/photo.jpg")
            em.set_footer(text = f"Request By : {ctx.author.name}", icon_url = f"{ctx.author.avatar_url}")
            msg = em
            await ctx.send(embed = msg)
            return

        types = [ "base64", "hex", "ascii" ]
        
        # Allow first letters as well
        from_check = [x for x in types if x[0] == from_type.lower()]
        from_type = from_type if not len(from_check) else from_check[0]
        to_check = [x for x in types if x[0] == to_type.lower()]
        to_type = to_type if not len(to_check) else to_check[0]
        
        if not from_type.lower() in types:
            await ctx.send("Invalid *from* type!")
            return

        if not to_type.lower() in types:
            await ctx.send("Invalid *to* type!")
            return

        if from_type.lower() == to_type.lower():
            return

        try:
            if from_type.lower() == "base64":
                if to_type.lower() == "hex":
                    await ctx.send(self.suppressed(ctx.guild, self._base64_to_hex(value)))
                    return
                elif to_type.lower() == "ascii":
                    await ctx.send(self.suppressed(ctx.guild, self._base64_to_ascii(value)))
                    return
            elif from_type.lower() == "hex":
                if to_type.lower() == "ascii":
                    await ctx.send(self.suppressed(ctx.guild, self._hex_to_ascii(value)))
                    return
                elif to_type.lower() == "base64":
                    await ctx.send(self.suppressed(ctx.guild, self._hex_to_base64(value)))
                    return
            elif from_type.lower() == "ascii":
                if to_type.lower() == "hex":
                    await ctx.send(self.suppressed(ctx.guild, self._ascii_to_hex(value)))
                    return
                elif to_type.lower() == "base64":
                    await ctx.send(self.suppressed(ctx.guild, self._ascii_to_base64(value)))
                    return
        except Exception:
            em = discord.Embed(color = 0XFF8C00, description = "> ┐(￣ヘ￣;)┌\n"
                                                               "> Aku tidak dapat melakukan convert itu")
            await ctx.send(embed = em)
            return      
    
