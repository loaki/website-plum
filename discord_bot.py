import discord
from discord.ext import commands
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

@bot.event
async def on_ready():
	print('Logged in as :')
	print(bot.user.name)
	print(bot.user.id)
	print(discord.__version__)
	print('Servers connected to :')
	for guild in bot.guilds:
		print(guild.name)

'''embed = discord.Embed(title = , description = , color=, embed.set_thumbnail(url = data[ctx.guild.name]['mthumbnail'])
	for i in range(0, len(s)):
		if i == 0:
			medal = ':first_place:'
		elif i == 1:
			medal = ':second_place:'
		elif i == 2:
			medal = ':third_place:'
		else:
			medal = f'**{i}**. '
		embed.add_field(name = f"{medal}{s[i][0]}", value = f"**{float('{:.2f}'.format(s[i][1]))}** points", inline = False)'''

@bot.event
async def on_message(message):
    await bot.process_commands(message)
    if message.channel.id == 864167588837064725:
        if message.attachments:
            url = message.attachments[0].url
            resp = requests.get(url, stream=True).raw
            image = np.asarray(bytearray(resp.read()), dtype="uint8")
            image = cv2.imdecode(image, cv2.IMREAD_COLOR)
            await message.channel.send(img_to_str(image))
            await message.add_reaction("✅")
            await message.channel.send(file=discord.File('test.png'))

bot.run(TOKEN)