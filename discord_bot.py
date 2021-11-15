import discord
from discord.ext import commands
from discord.ext.commands import CommandNotFound
import requests
from ocr import img_to_str
import cv2
import numpy as np
import requests

#TOKEN = 'Nzg5NjY0MTg2MjU0NjIyNzMw.X91WFQ.raTu5tULhisu8qI-7TipiNYXXPM' #bot token
TOKEN = 'ODQ3OTQ0OTc4NzU5OTQyMTQ0.YLFcTA.7xU4Ad_t7zCX4AQQvLmPV9VOhRE' #test bot
bot = commands.Bot(command_prefix = '!')
bot.remove_command('help')
admin = 272117022622482432
chan = 864167588837064725

@bot.event
async def on_ready():
	print('Logged in as :')
	print(bot.user.name)
	print(bot.user.id)
	print(discord.__version__)
	print('Servers connected to :')
	for guild in bot.guilds:
		print(guild.name)
	channel = bot.get_channel(chan)
	await channel.send('on')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    raise error

async def embed(text, channel):
	try:
		looser_index = text.index('Perdants')
		winners = text[2 : looser_index]
		loosers = text[looser_index + 1 :]
		color = '992d22'
		if text[0] == "Victoire":
			color = '1f8b4c'
		for item in text:
			if " " in item:
				if text.index(item) > looser_index:
					desc = "Attaque "
				else:
					desc = "Defense "
				if "Prisme" in item:
					desc += "Prisme"
				else:
					desc += "Perco"
		embed = discord.Embed(title = text[0], description = desc, color=int(color, 16))
		embed.add_field(name = "Gagnants", value = ", ".join(winners), inline = False)
		embed.add_field(name = "Perdants", value = ", ".join(loosers), inline = False)
		embed.add_field(name = "Txt", value = text, inline = False)
		await channel.send(embed = embed)
	except:
		await channel.send("Error in read")

@bot.event
async def on_message(message):
	await bot.process_commands(message)
	if message.author.bot:
		return
	if message.channel.id == chan:
		if message.attachments:
			url = message.attachments[0].url
			resp = requests.get(url, stream=True).raw
			image = np.asarray(bytearray(resp.read()), dtype="uint8")
			image = cv2.imdecode(image, cv2.IMREAD_COLOR)
			try:
				await embed(img_to_str(image), message.channel)
				await message.add_reaction("✅")
			except:
				await message.add_reaction("❎")

@bot.command()
async def ocr(ctx):
	if ctx.channel.id == chan:
		await ctx.send(file=discord.File('ocr.png'))

def main():
	bot.run(TOKEN)

if __name__=='__main__':
    main()