from discord.ext import commands
from xml.etree import ElementTree as ET
from xml import etree
import aiohttp, asyncio, json, time, requests, xmltodict, discord, xml, ecuas as nh

## @file_url, @tags, @score
'''		TODOS:
	* doujinshi
		- fix ecuas library
		
	* r34
		- fix bubble sort algorimth thing << this might actually work, not sure why it will randomly display like score 4s tho
		- add banned tags list (optional)
		- minimium score requirement (optional)
		- searches multiple pages
		- add an already sent list to prevent repeats
		- actually posts 20 items
			> top20r34 works
			> tr34 works
		- make a first 50 one
		
	* general
		- help menu
			> make a help menu
			> change the status to playing ..help
			> maybe have the bot dm the help thing to you
		- work on a change prefix command
		- add a logout command only for you

'''

bot = commands.Bot("..")
token = open("token.txt", "r").read()

async def fetch(url):
	async with aiohttp.ClientSession() as cs:
		async with cs.get(url) as r:
			return await r.text()

async def etree_to_dict(t):
	d = {t.tag : map(etree_to_dict, t.iterchildren())}
	d.update(('@' + k, v) for k, v in t.attrib.iteritems())
	d['text'] = t.text
	return d

async def r34(tags):
	url = "https://rule34.xxx/index.php?page=dapi&s=post&q=index&tags="
	for item in tags:
		if item == tags[0]:
			print('',end='')
		elif item == tags[-1]:
			url+=item
		else:
			url += item+"+"
	url += '&pid='+item[0]
	response = await fetch(url)
	my_dict = xmltodict.parse(response)
	resp =  json.dumps(my_dict,indent=1)
	return resp
	
async def Sort(sub_li): 
	l = len(sub_li) 
	for i in range(0, l): 
		for j in range(0, l-i-1): 
			if (sub_li[j][0] < sub_li[j + 1][0]): 
				tempo = sub_li[j] 
				sub_li[j]= sub_li[j + 1] 
				sub_li[j + 1]= tempo 
	return sub_li
	
@bot.event
async def on_ready():
	print('Logged in as')
	print(bot.user.name)
	print(bot.user.id)
	print('------')
	await bot.change_presence(status=discord.Status.online, activity=discord.Game("with my dick"))

@bot.command()
async def ping(ctx):
	await ctx.send("Pong")

@bot.command()
async def tr34(ctx, *args):
	res = await r34(args)
	with open('t.txt','w+') as f:
		f.write(res)
	resp = json.loads(res)
	sorted_posts = []
	for post in resp['posts']['post']:
		score = post['@score']
		url = post['@file_url']
		tags = post['@tags']
		sorted_posts.append([score,tags,url])
	sorted_posts = await Sort(sorted_posts)
	await ctx.send("Score: "+sorted_posts[0][0]+'\n'+sorted_posts[0][2])

@bot.command()
async def top20r34(ctx, *args):
	br = False
	page = 1
	pn = 0 ##post sent count
	info = []
	info.append(page)
	for tag in args:
		info.append(tag)
	res = await r34(info)
	with open('t.txt','w+') as f:
		f.write(res)
	resp = json.loads(res)
	sorted_posts = []
	if resp['posts']['@count'] == '0':
		await ctx.send("Nothing matches those tags.")
	else:
		while True:
			if br:
				break
			for post in resp['posts']['post']:
				score = post['@score']
				url = post['@file_url']
				tags = post['@tags']
				sorted_posts.append([score,tags,url])
			sorted_posts = await Sort(sorted_posts)
			lasturl = ''
			for post in sorted_posts:
				if pn == int(resp['posts']['@count']) or pn == 20:
					br = True
					break
				elif lasturl != post[2]:
					await ctx.send("Score: "+post[0]+'\nTags:'+post[1]+'\n'+post[2])
					pn+=1
				lasturl = post[2]

@bot.command()
async def nsearch(ctx, args):
	d = nh.Doujinshi(args)
	await ctx.send("this is a beta command")
	await ctx.send('Name:'+d.name+'\nTags: '+d.tags+'\nPages: '+d.pages+'\n'+d.cover)
	
	
	








bot.run(token)
