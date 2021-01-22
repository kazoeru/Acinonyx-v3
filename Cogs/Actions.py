import asyncio
import discord
import random
import datetime
from   discord.ext import commands
from   Cogs import DisplayName
from   Cogs import Nullify

def setup(bot):
	# Menambahkan bot
	bot.add_cog(Actions(bot))

class Actions(commands.Cog):
	## class untuk handle storing dan action message
	class actionable:
		## harus diisi di kelas override. setiap {} diganti dengan target member name
		nothingList = [] # saat kamu memanggil tanpa argument
		botList = [] # saat action dilakukan dengan bot
		selfList = [] # saat action dilakukan pada user yang memanggilnya
		memberList = [] # saat action dilakukan kepada user lain
		itemList = [] # saat action dilakukan pada string text yang bukan anggota

		def computeAction(self, bot, ctx, target):
			'''return pesan berdasarkan context dan argument command'''
			mesg = ""

			if not target: # tidak ada arguments
				mesg = random.choice(self.nothingList)
			else:
				targetMember = DisplayName.memberForName(target, ctx.message.guild)

				if targetMember:
					if self.botList and targetMember.id == bot.user.id: # action dengan bot
						mesg = random.choice(self.botList) # jika botList kosong, akan dialihkan ke member list
					elif self.selfList and targetMember.id == ctx.message.author.id: # action dengan diri sendiri
						mesg = random.choice(self.selfList)
					else: # action dengan user lain
						mesg = random.choice(self.memberList).replace("{}",DisplayName.name(targetMember))
				else: # action dengan Item
					mesg = random.choice(self.itemList)
					if '{}' in mesg:
						mesg = mesg.format(target)

			mesgFull = '*{}*, {}'.format(DisplayName.name(ctx.message.author), mesg)
			mesgFull = Nullify.clean(mesgFull)
			return mesgFull

	## Kumpulan pesan dari semua action
	class eating(actionable):
		nothingList = [ 'kamu hanya duduk diam, bengong sambil mikirin mantan, dan gak lagi makan apa apa :(...',
						'*yakin* kamu punya sesuatu untuk dimakan? kamu tu cuma bisa gigit jari doang...']
		botList = [ 'kamu mau makan *aku*? tapi sayang loh, ku cuma bot, aku cuma ada baut untuk kamu makan.',
					'saat mulut mu terbuka lebar dalam beberapa detik kamu sadar *aku* telah memakan *mu*.',
					'aku hanya bot. kamu tidak dapat memakan ku.',
					'saat kamu menutup mulut mu... tunggu... tidak ada apa-apa, karena aku hanyalah bot digital!*.',
					'akan jadi bot seperti apa aku ini?, kalau aku membiarkan mu memakan ku']
		selfList = ['kamu menggigit tangan mu sendiri - tidak heran, jika itu menyakitkan.',
					'kamu memasukan satu jari kedalam mulut mu, tetapi kamu *tidak bisa* untuk menggigitnya.',
					'tunggu - kamu bukan makanan!',
					'mungkin kamu bukan yang paling pintar...']
		memberList = [  'kamu membuka mulut dengan lebar dan memakan *{}* dalam satu gigitan.',
						'kamu mencoba memakan *{}*, tapi kamu tidak dapat melakukannya - lalu kamu memuntahkannya, *{}* memiliki rasa yang seperti bau ketiak...',
						'kamu menggigit *{}* dengan sangat cepat. bahkan dia tidak dapat menyadarinya.',
						'kamu menggigit *{}* tepat dibahunya - lalu dia menghadapkan mukanya ke arah mu dan memiliki bola mata yang putih semua, kamu berusaha lari secepatnya sambil ngompol.']
		itemList = [ 	'kamu mengambil gigitan besar *{}*, dan rasanya anjim banget',
						'kamu mengambil gigitan pertama *{}* - dan rasanya menakjubkan!!',
						'kamu sangat rakus dan merobek *{}* hingga kecil-kecil!',
						'kamu sudah sangat kenyang dan tidak dapat memaksa dirimu untuk memakan *{}*, jadi kamu hanya meninggalkannya...']

	class drinking(actionable):
		nothingList = [ 'kamu metanap gelas yang penuh dengan *angin*...',
						'cangkir itu pasti berisi sesuatu, lalu kamu mengambilnya dan akhirnya kamu hanya meminum *angin*...',
						'mungkin kamu butuh minum, sana ambil air dan cepat minum.',
						'terlihat sebuah meja oleh mu, ketika kamu mendekat - dan tidak ada apa-apa',
						'kamu tau kan bagaimana caranya minum?',
						'kamu mencari mati-matian sesuatu untuk di minum']
		botList = [ 'kamu yakin mau meminum *ku*',
					'kamu mencari *ku* untuk meminum *ku*? saat kamu sadar *aku* telah meminum *mu*!',
					'aku cuma bot, kamu tidak bisa meminum ku.',
					'you stick a straw in... wait... in nothing, because I\'m *digital!*.',
					'apa yang kamu pikirkan jika aku membiarkan mu meminum ku?',
					'aku pikir sepertinya kamu tidak akan suka rasanya jika kamu mencicipi ku',
					'kamu tidak dapat meminum ku, aku hanyalah sebuah program!']
		selfList = ['kamu menusuk dirimu sendiri dengan sedotan - tidak heran, jika itu menyakitkan.',
					'kamu mencoba masuk kedalam sebuah cangkir, tapi kamu tidak dapat melakukannya.',
					'tunggu dulu - kamu bukan minuman!',
					'mungkin kamu bukan yang paling pintar...',
					'kamu mungkin memiliki beberapa masalah...',
					'kamu mencoba meminum dirimu sendiri.',
					'kepana kamu mau meminum dirimu sendiri?']
		memberList = [  'kamu mengambil sedotan keberuntungan mu dan meminum *{}* dalam satu kali sedot.',
						'kamu mencoba meminum *{}*, tetapi kamu tidak dapat melakukannya - lalu kamu meludahkannya, rasanya seperti air got...',
						'kamu meminum sedikit minuman milik *{}* dengan cepat. bahkan dia tidak menyadarinya.',
						'kamu menusuk *{}* dengan sedotan tepat di bahunya - lalu kamu melarikan diri saat dia mengejar mu.',
						'kamu terlihat sangat haus - *{}* mengorbankan dirinya untuk mu.']
		itemList = ['kamu mengambil isapan besar *{}*. *Muantaaaaap!*',
					'sedotan mu tenggelam di *{}* - rasanya uenak sekali.',
					'kamu tidak bisa memaksakan dirimu untuk meminum *{}* - jadi kamu menahannya...',
					'kamu meminum *{}*.']

	# class booping(actionable):
	# 	nothingList = [ 'you stretch out your hand in the air, but there\'s nothing there...',
	# 					'you try and find someone to boop, but there\'s no one there.',
	# 					'you look around the channel for someone to boop.',
	# 					'you eye all the heads in the room, just waiting to be booped.',
	# 					'are you sure you have someone to boop?',
	# 					'I get it. You want to boop *someone*.']
	# 	selfList = ['you boop yourself on the nose with your finger.',
	# 				'you try to boop your head, but your hand gets lost along the way.',
	# 				'you happily boop yourself, but you are now very giddy.',
	# 				'wait - are you sure you want to boop yourself?',
	# 				'you might not be the smartest...',
	# 				'you might have some issues.',
	# 				'you try to boop yourself.',
	# 				'why would you boop yourself?']
	# 	memberList = [  'you outstretch your lucky finger and boop *{}* in one go.',
	# 					'you try to boop *{}*, but you just can\'t quite do it - you miss their head, the taste of failure hanging stuck to your hand...',
	# 					'you sneak a boop onto *{}*.  They probably didn\'t even notice.',
	# 					'you poke your hand onto *{}\'s* hand - You run away as they run after you.',
	# 					'you happily drum your fingers away - *{}* starts to look annoyed.',
	# 					'you\'re feeling boopy - *{}* sacrifices themself involuntarily.',
	# 					'somehow you end up booping *{}*.',
	# 					'you climb *{}*\'s head and  use it as a bouncy castle... they feel amused.']
	# 	itemList = ['you put your hand onto *{}*\'s head. *Bliss.*',
	# 				'your hand touches *{}*\'s snoot - it feels satisfying.',
	# 				'you happily boop *{}*, it\'s lovely!',
	# 				'you just can\'t bring yourself to boop *{}* - so you just let your hand linger...',
	# 				'you attempt to boop *{}*, but you\'re clumsier than you remember - and fail...',
	# 				'you boop *{}*.',
	# 				'*{}* feels annoyed from your booping.',
	# 				'*{}* starts resembling a happy pupper.']

	class spooky(actionable):
		nothingList = [ 'kamu mencoba menakut-nakuti tapi tidak ada siapa siapa',
						'kamu menakut-nakuti angin...',
						'sayangnya, tidak ada yang takut padamu']
		botList = [ 'you scared the living pumpkin out of me!',
					'kamu mencoba menakut-nakuti ku dengan begitu keras, wooo garing...', # https://www.myenglishteacher.eu/blog/idioms-for-being-afraid/
					'kamu mencoba menakut-nakuti ku? tapi aku hanyalah sebuah bot... aku tidak bisa kamu takuti :P',
					'maaf, tapi aku tidak akan membiarkan mu menakut nakuti ku!'
					'aaaaaaaaaah! jangan menakut-nakuti ku seperti itu!']
		selfList = ['cobalah untuk menonton film horror!',
					'booo! kamu takut dengan dirimu sendiri?',
					'kamu berjalan menuju cermin dan kamu ketakutan saat melihat wajah mu sendiri...',
					'kamu ketakutan... oleh dirimu sendiri?']
		memberList = [  'kamu menakut nakuiti *{}* dan dia mulai menjerit!',
						'kamu mencoba menyelinap ke *{}*, tapi dia sadar dan gagal...',
						'selamat! kamu menakuti *{}* dan dia ketakutan.']
		itemList = ['kamu mencoba menakuti *{}* dan tidak ada reaksi apa-apa, lalu pergi meninggalkan mu dan berpikir kamu itu aneh...',
					'kamu mencoba menakut-nakuti *{}* dan tidak ada reaksi apa-apa...',
					'kamu melakukan yang terbaik untuk menakuti *{}*, tapi gagal...',
					'sp00py time! *{}* terlihat sangat ketakutan dari yang kamu bayangkan, dan dia mulai menangis!']

	# class highfives(actionable):
	# 	nothingList = [ 'kamu berdiri sendiri untuk selamanya, sambil mengangkat tangan - dan tidak ada yang peduli...',
	# 					'kamu mengayunkan tangan mu sekuat tenaga - dan kamu - high fiveless...',
	# 					'the only sound you hear as a soft *whoosh* as your hand connects with nothing...']
	# 	botList = [ 'the sky erupts with 1\'s and 0\'s as our hands meet in an epic high five of glory!',
	# 				'you beam up to the cloud and receive a quick high five from me before downloading back to Earth.',
	# 				'I unleash a fork-bomb of high five processes!',
	# 				'01001000011010010110011101101000001000000100011001101001011101100110010100100001']
	# 	selfList = ['ahh - high fiving yourself, classy...',
	# 				'that\'s uh... that\'s just clapping...',
	# 				'you run in a large circle - *totally* high fiving all your friends...',
	# 				'now you\'re at both ends of a high five!']
	# 	memberList = [  'you and *{}* jump up for an epic high five - freeze-framing as the credits roll and some wicked 80s synth plays out.',
	# 					'you and *{}* elevate to a higher plane of existence in wake of that tremendous high five!',
	# 					'a 2 hour, 3 episode anime-esque fight scene unfolds as you and *{}* engage in a world-ending high five!',
	# 					'it *was* tomorrow - before you and *{}* high fived with enough force to spin the Earth in reverse!',
	# 					'like two righteous torpedoes - you and *{}* connect palms, subsequently deafening everyone in a 300-mile radius!']
	# 	itemList = ['neat... you just high fived *{}*.',
	# 				'your hand flops through the air - hitting *{}* with a soft thud.',
	# 				'you reach out a hand, gently pressing your palm to *{}*.  A soft *"high five"* escapes your lips as a tear runs down your cheek...',
	# 				'like an open-handed piston of ferocity - you drive your palm into *{}*.']

	class petting(actionable): # meow
		nothingList = [ 'kamu tanpa sadar hanya membelai angin.',
						'kamu bersumpah, kamu telah melihat se-ekor kucing disana!',
						'kamu mengingatnya bahwa tidak ada kucing disini.',
						'kamu mencoba untuk membelai kucing, tetapi kucing itu telah pergi.']
		botList = [ 'aku mungkin hanya sebuah digital, tapi saya masih mau di belai-belai.',
					'*purrrrrrrrrrrrrrr*.',
					'kamu tersengat listrik saat membelai sebuah komputer.']
		selfList = ['kamu memberi belaian dikapala mu sendiri.',
					'sayang sekali tidak ada yang mau membelaimu.',
					'rambut mu begitu hangat dan lembut.']
		memberList = [  'kamu memberi sebuah belaian ke *{}* dikepalanya.',
						'kamu membelai rambut milik *{}*.',
						'*{}* tersenyum oleh belaian mu.',
						'kamu mencoba membelai *{}*, tetapi kamu gagal karena dia bersembunyi di bawah kasur.',
						'kamu membelai *{}* tapi dia menggigit tangan mu',
						'kamu mencoba membelai *{}* dan gagal lalu dia lari.']
		itemList = ['kamu membelai *{}* tapi itu tidak terasa seperti kucing.',
					'kamu menyakiti tangan mu sendiri, saat ingin membelai *{}*.']

	# Init with the bot reference, and a reference to the settings var
	def __init__(self, bot):
		self.bot = bot
		global Utils, DisplayName
		Utils = self.bot.get_cog("Utils")
		DisplayName = self.bot.get_cog("DisplayName")

	@commands.command(pass_context=True)
	async def eat(self, ctx, *, member : str = None):
		"""Makan boss."""

		msg = self.eating.computeAction(self.eating, self.bot, ctx, member) #python is silly and makes me do this for uninitialized classes
		await ctx.channel.send(msg)
		return

	@commands.command(pass_context=True)
	async def drink(self, ctx, *, member : str = None):
		"""Minum dulu boss."""

		msg = self.drinking.computeAction(self.drinking, self.bot, ctx, member)
		await ctx.channel.send(msg)
		return

	# @commands.command(pass_context=True)
	# async def boop(self, ctx, *, member : str = None):
	# 	"""Boop da snoot."""

	# 	msg = self.booping.computeAction(self.booping, self.bot, ctx, member)
	# 	await ctx.channel.send(msg)
	# 	return

	@commands.command(pass_context=True)
	async def spook(self, ctx, *, member : str = None):
		"""booo~"""

		if datetime.date.today().month == 10:
			# make it extra sp00py because it is spooktober
			await ctx.message.add_reaction("🎃")
		msg = self.spooky.computeAction(self.spooky, self.bot, ctx, member)
		await ctx.channel.send(msg)
		return

	# @commands.command(pass_context=True)
	# async def highfive(self, ctx, *, member : str = None):
	# 	"""High five like a boss."""

	# 	msg = self.highfives.computeAction(self.highfives, self.bot, ctx, member)
	# 	await ctx.channel.send(msg)
	# 	return

	@commands.command(pass_context=True)
	async def pet(self, ctx, *, member : str = None):
		"""pet kitties."""

		msg = self.petting.computeAction(self.petting, self.bot, ctx, member)
		await ctx.channel.send(msg)
		return
