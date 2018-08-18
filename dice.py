import discord
import requests
from bs4 import BeautifulSoup
import random
import re
from datetime import datetime
import os

uptimebegin = datetime.now()

client = discord.Client(max_messages = 100)

@client.event
async def on_ready():
	print("ready")

async def getrandombot(query = "%20"):
	class Args:
		cap = 200
		lastrand = 0
		url = ""
		response = None
		doc = None
		bots = []
		bot = None
		inviteurl = ""
	
	if query != "%20":
		Args.cap = 50
	
	if query == "TOP":
		Args.cap = 70
	
	failmsg = "Failed to fetch bot!"

	async def handletry(retry = False):
		if retry:
			print(Args.lastrand)
			Args.cap = Args.lastrand - 10
			if Args.cap < 1:
				Args.cap = 1
		
		Args.lastrand = random.randint(1, Args.cap)
		if query == "TOP":
			Args.url = "https://discordbots.org/list/top?page=" + str(Args.lastrand)
		else:
			Args.url = "https://discordbots.org/search?q=" + query + "&page=" + str(Args.lastrand)

		print("trying " + Args.url)

		Args.response = requests.get(Args.url)
		Args.doc = BeautifulSoup(Args.response.text, "lxml")

		if "No bots found :(" in Args.response.text:
			return

		Args.bots = Args.doc.find_all("li", { "class": "column bot-card is-one-quarter" })

		if len(Args.bots) == 0:
			return

		Args.bot = random.choice(Args.bots)

		Args.response = requests.get("https://discordbots.org" + Args.bot.find("a").get("href"))
		Args.doc = BeautifulSoup(Args.response.text, "lxml")

		title = Args.doc.find("div", { "class": "titleandvote" })
		if title:
			Args.inviteurl = title.find_all("a")[1].get("href")
		else:
			Args.inviteurl = ""
	
	tries = 0
	await handletry()

	while len(Args.bots) == 0 or Args.inviteurl == "":
		await handletry(True)
		tries += 1
	
	if len(Args.bots) == 0 or Args.inviteurl == "":
		return failmsg
	
	botname = Args.bot.find("a", { "class": "bot-name" }).text
	botdesc = Args.bot.find("p", { "class": "bot-description" }).text
	boticon = Args.bot.find("img").get("src")

	embed = discord.Embed(
		title = botname,
		description = botdesc,
		url = Args.inviteurl,
		colour = 0xE95312
	)

	embed.set_thumbnail(url = boticon)

	embed.add_field(
		name = "Details",
		value = "Status: {0}\nType: {1}\nServers: {2}\nVotes this month: {3}\nID: {4}".format(
			"online" if Args.bot.find("span", { "class": "status gray" }) == None else "offline",
			re.sub("\s+", " ", Args.bot.find("span", { "class": "lib" }).text.replace("\t", "")).strip(),
			re.sub("\s+", " ", Args.bot.find("span", { "class": "servers btn btn-orange btn-1x" }).text).strip().split(" ")[0],
			Args.bot.find("button", { "data-tooltip": "Votes this month" }).text,
			Args.bot.find("a", { "class": "bot-name" }).get("id").split("-")[1]
		)
	)

	embed.set_footer(text = "Found on: " + Args.url)

	return embed

async def getrandomserver(query = "%20"):
	class Args:
		cap = 345
		lastrand = 0
		url = ""
		response = None
		doc = None
		servers = []
		server = None
		inviteurl = ""
		invite = None
	
	if query != "%20":
		Args.cap = 151
	
	if query == "TOP":
		Args.cap = 70

	failmsg = "Failed to fetch server!"

	async def handletry(retry = False):
		if retry:
			print(Args.lastrand)
			Args.cap = Args.lastrand - 20
			if Args.cap < 1:
				Args.cap = 1

		Args.lastrand = random.randint(1, Args.cap)
		if query == "TOP":
			Args.url = "https://discordbots.org/servers/list/top?page=" + str(Args.lastrand)
		else:
			Args.url = "https://discordbots.org/servers/search?q=" + query + "&page=" + str(Args.lastrand)

		print("trying " + Args.url)

		Args.response = requests.get(Args.url)
		Args.doc = BeautifulSoup(Args.response.text, "lxml")
	
		Args.servers = Args.doc.find_all("li", { "class": "column bot-card is-one-fourth" })

		for server in Args.servers:
			if "No Server" in server:
				Args.servers.remove(server)
	
		Args.server = random.choice(Args.servers)

		Args.response = requests.get("https://discordbots.org" + Args.server.find("a").get("href"))
		Args.doc = BeautifulSoup(Args.response.text, "lxml")

		title = Args.doc.find("div", { "class": "titleandvote" })
		if title:
			try:
				Args.inviteurl = title.find("a").get("href")
				Args.invite = await client.get_invite(Args.inviteurl)
				if Args.invite.revoked:
					Args.inviteurl = ""
					Args.invite = None
			except:
				Args.inviteurl = ""
				Args.invite = None
		else:
			Args.inviteurl = ""
			Args.invite = None
	
	tries = 0
	await handletry()

	while tries < 3 and ("Error" in Args.doc.find("title") or len(Args.servers) == 0 or Args.invite == None or Args.invite.revoked or Args.server == None):
		await handletry("Error" in Args.doc.find("title") or len(Args.servers) == 0)
		tries += 1
	
	if "Error" in Args.doc.find("title") or len(Args.servers) == 0 or Args.invite == None or Args.invite.revoked or Args.server == None:
		return failmsg

	servername = Args.server.find("a", { "class": "bot-name" }).text
	serverdesc = Args.server.find("p", { "class": "bot-description" }).text
	servericon = Args.server.find("img").get("src")

	serveremotes = re.sub("[^0-9]", "", Args.server.find_all("span", { "class": "servers btn btn-orange btn-1x" })[1].text)

	embed = discord.Embed(
		title = servername,
		description = serverdesc,
		url = Args.inviteurl,
		colour = 0xE95312
	)

	embed.set_thumbnail(url = servericon)

	embed.add_field(
		name = Args.inviteurl.replace("https://", ""),
		value = "Invite created by: {0}#{1}\n   Channel: #{2}\n   Custom emojis: {3}".format(
			Args.invite.inviter.name,
			Args.invite.inviter.discriminator,
			Args.invite.channel.name,
			serveremotes
		),
		inline = False
	)

	embed.set_footer(text = "Found on: " + Args.url)
	
	return embed

def helpmenu():
	embed = discord.Embed(
		title = "Available Commands",
		colour = 0xE95312
	)

	embed.add_field(
		name = ">dice help",
		value = "Displays this help menu.",
		inline = False
	)

	embed.add_field(
		name = ">dice info",
		value = "Displays info about the bot.",
		inline = False
	)

	embed.add_field(
		name = ">dice roll",
		value = "Fetches a random valid server invite from https://discordbots.org/servers.",
		inline = False
	)

	embed.add_field(
		name = ">dice query [query]",
		value = "Fetches a random valid server invite based on your query.",
		inline = False
	)

	embed.add_field(
		name = ">dice search [query]",
		value = "An alternative to >dice query.",
		inline = False
	)

	embed.add_field(
		name = ">dice roll bot",
		value = "Fetches a random bot invite from https://discordbots.org.",
		inline = False
	)

	embed.add_field(
		name = ">dice query bot [query]",
		value = "Fetches a random bot invite based on your query.",
		inline = False
	)

	embed.add_field(
		name = ">dice search bot [query]",
		value = "An alternative to >dice query bot.",
		inline = False
	)

	embed.add_field(
		name = ">dice top",
		value = "Fetches a random valid server invite in the top 70 pages from https://discordbots.org/servers/list/top.",
		inline = False
	)

	embed.add_field(
		name = ">dice top bot",
		value = "Fetches a random bot invite in the top 70 pages from https://discordbots.org/list/top.",
		inline = False
	)

	return embed

async def infomenu():
	embed = discord.Embed(
		title = "Dice Info",
		colour = 0xE95312
	)

	embed.set_thumbnail(url = client.user.avatar_url)

	embed.add_field(
		name = "Servers",
		value = str(len(client.servers))
	)

	utdiff = (datetime.now() - uptimebegin).total_seconds()

	utdays = int(utdiff / 86400)
	uthours = int(utdiff / 3600) - (utdays * 86400)
	utminutes = int(utdiff / 60) - (uthours * 3600)
	utseconds = int(utdiff) - (utminutes * 60)

	embed.add_field(
		name = "Uptime",
		value = "{0} days, {1} hours, {2} minutes and {3} seconds".format(utdays, uthours, utminutes, utseconds)
	)

	embed.add_field(
		name = "Written in",
		value = "Python, using discord.py (https://github.com/Rapptz/discord.py)"
	)

	embed.add_field(
		name = "Bot invite link",
		value = "http://bit.ly/dicediscordbot"
	)

	embed.add_field(
		name = "My server invite link",
		value = "https://discord.gg/GyPaSWB"
	)

	my = await client.get_user_info("264163473179672576")

	embed.set_footer(
		text = "Developed by " + my.name + "#" + my.discriminator,
		icon_url = my.avatar_url
	)

	return embed

@client.event
async def on_message(message):
	if message.author.bot == True:
		return

	msg = message.content.lower()

	if msg.startswith(">dice"):
		args = message.content.lower().split(" ")
		cmd = re.sub("[^A-Za-z]", "", args[1])

		if cmd == "help":
			return await client.send_message(message.channel, embed = helpmenu())
		
		elif cmd == "info":
			return await client.send_message(message.channel, embed = await infomenu())

		elif cmd == "roll" or cmd == "top":
			if len(args) > 2 and re.sub("[^a-z]", "", args[2]) == "bot":
				pending = await client.send_message(message.channel, "Fetching random bot invite...")

				try:
					bot = await getrandombot() if cmd == "roll" else await getrandombot("TOP")
					if type(bot) is discord.Embed:
						await client.send_message(message.channel, embed = bot)
					else:
						await client.send_message(message.channel, "Failed to fetch bot!")
				except:
					await client.send_message(message.channel, "Failed to fetch bot!")
				return await client.delete_message(pending)
			else:
				pending = await client.send_message(message.channel, "Fetching random server invite...")

				try:
					server = await getrandomserver() if cmd == "roll" else await getrandomserver("TOP")
					if type(server) is discord.Embed:
						await client.send_message(message.channel, embed = server)
						await client.send_message(message.channel, server.url)
					else:
						await client.send_message(message.channel, "Failed to fetch server!")
				except:
					await client.send_message(message.channel, "Failed to fetch server!")
				return await client.delete_message(pending)
		
		elif cmd == "query" or cmd == "search":
			if len(args) > 3 and re.sub("[^a-z]", "", args[3]) == "bot":
				pending = await client.send_message(message.channel, "Fetching random bot invite...")

				try:
					bot = await getrandombot(re.sub("[^A-Z a-z]", "", " ".join(args[4:])))
					if type(bot) is discord.Embed:
						await client.send_message(message.channel, embed = bot)
					else:
						await client.send_message(message.channel, "Failed to fetch bot!")
				except:
					await client.send_message(message.channel, "Failed to fetch bot!")
				return await client.delete_message(pending)
			else:
				pending = await client.send_message(message.channel, "Fetching random server invite...")

				try:
					server = await getrandomserver(re.sub("[^A-Z a-z]", "", " ".join(args[3:])))
					if type(server) is discord.Embed:
						await client.send_message(message.channel, embed = server)
						await client.send_message(message.channel, server.url)
					else:
						await client.send_message(message.channel, "Failed to fetch server!")
				except:
					await client.send_message(message.channel, "Failed to fetch server!")
				return await client.delete_message(pending)
		
		else:
			return await client.send_message(message.channel, "This is not a valid command! Type `>dice help` to view all available commands.")

client.run(os.getenv("BOT_TOKEN"))