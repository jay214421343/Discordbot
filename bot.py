import discord
import asyncio
import logging

logging.basicConfig(level=logging.INFO)

client = discord.Client()
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message(message):
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
			if (epiccount < 5):
				epicLikeliness = "are probably not epic"
			elif (epiccount < 10):
				epicLikeliness = "might be epic"
			elif (epiccount < 20):
				epicLikeliness = "are likely epic"
			elif (epiccount < 30):
				epicLikeliness = "are very likely epic"
			elif (epiccount < 50):
				epicLikeliness = "are epic"
			await client.send_message(message.channel, f'{mention} has now been called epic {epiccount} {timeform}\n They {epicLikeliness}')

	elif message.content.startswith('!sleep'):
		await asyncio.sleep(5)
		await client.send_message(message.channel, 'Done sleeping')

client.run('NTQ5NjY1ODU1MTM5NzQxNzE3.D1XNOQ.hyUFWZrsLGHO0lJC3VSddHwkYMU')
