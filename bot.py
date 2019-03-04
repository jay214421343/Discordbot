import discord
import asyncio
import logging
import os
import psycopg2

DATABASE_URL = os.environ['DATABASE_URL']

conn = psycopg2.connect(DATABASE_URL, sslmode='require')

logging.basicConfig(level=logging.INFO)

client = discord.Client()
@client.event
async def on_ready():
	print('Logged in as')
	print(client.user.name)
	print(client.user.id)
	print('------')
	
	botActivity = discord.Activity(name=os.environ['activityName'],type=discord.ActivityType.watching)
	await client.change_presence(activity = botActivity)

@client.event
async def on_message(message):
	if message.author == client.user:
		return
	print(f"Message sent by {message.author}")
	if message.content.startswith("<@") and len(message.content.split()) == 3:
		print("Mention found")
		print(message.content.split())
		print(len(message.content.split()))
		mention,wordis,epicword = message.content.split()
		if wordis == "is" and epicword == "epic":
			print("is epic")
			with open("botdatabase","r") as db:
				dbLines = db.readlines()
			namefound = False
			dbNewLines = []
			for line in dbLines:
				userElements = line.split('=')
				if userElements[0] == mention:
					print("ID found")
					timeform = "times"
					userElements[1] = str(int(userElements[1]) + 1)
					print("Epiccounter = " + userElements[1])
					epiccount = userElements[1] 
					namefound = True
					print("Modified line:" + userElements[0] + "=" + userElements[1])
					if len(userElements) == 2:
						dbNewLines.append(f"{userElements[0]}={userElements[1]}\n")
					break
				print(userElements[0] + "=" + userElements[1] + "not matching")
				if len(userElements) == 2:
					dbNewLines.append(f"{userElements[0]}={userElements[1]}")
			if namefound == True:
				with open("botdatabase","w") as dbw:
					dbw.writelines(dbNewLines)
			else:
				with open("botdatabase","a") as dba:
					dba.write(f"{mention}=1" + "\n")
				epiccount = 1
				timeform = "time"
			if int(epiccount) < 5:
				epicLikeliness = "are probably not epic"
			elif int(epiccount) < 10:
				epicLikeliness = "might be epic"
			elif int(epiccount) < 20:
				epicLikeliness = "are likely epic"
			elif int(epiccount) < 30:
				epicLikeliness = "are very likely epic"
			elif int(epiccount) < 50:
				epicLikeliness = "are epic"
			await message.channel.send(f'{mention} has now been called epic {epiccount} {timeform}\n They {epicLikeliness}')
			
@client.event
async def on_raw_reaction_add(payload):  # Will be dispatched every time a user adds a reaction to a message the bot can see
	role = ""
	print("Reaction added")
	if not payload.guild_id:
		# In this case, the reaction was added in a DM channel with the bot
		print("Dafuq")
		return
		
	# At this point, you'd have to implement something like a check to ensure the reaction was added to the proper message
	# Either by hardcoding the ID or using a better way like storing the message id.
	if str(payload.message_id) != str(os.environ['messageID']):
		print(os.environ['messageID'])
		print(payload.message_id)
		print("Wrong messageID")
		return
	print("Reaction added to message")
	guild = client.get_guild(payload.guild_id)  # You need the guild to get the member who reacted
	member = guild.get_member(payload.user_id)  # Now you have the key part, the member who should receive the role

	# At this point you may vary between different reactions.
	if payload.emoji.id == os.environ['emojiIDMember']:  # payload.emoji is a PartialEmoji. You have different possibilities to check for a proper reaction
		role = discord.Object(os.environ['roleIDMember']) # You also need the role
		messageChannel = discord.Object(os.environ['channelID'])
		messageChannel.send(os.environ['memberJoinMessage'])
	# Gotta do same thing for friends
	elif payload.emoji.id == os.environ['emojiIDFriend']:
		role = discord.Object(os.environ['roleIDFriend'])
	else:
		# An improper emoji has been used to react to the message
		print("Wrong emoji")
		return

	await member.add_roles(role, reason='Invited to clan')  # Finally add the role to the member
	
client.run(os.environ['discordToken'])
