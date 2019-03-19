import discord
import logging
import os
import psycopg2
import time
from discord.ext import commands

DATABASE_URL = os.environ['DATABASE_URL']

logging.basicConfig(level=logging.INFO)

client = commands.Bot(command_prefix="?")


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

    mentionMessages = []
    botActivity = discord.Activity(name=os.environ['activityName'], type=discord.ActivityType.watching)
    await client.change_presence(activity=botActivity)


@client.command()
async def ping(ctx):
    '''
    This text will be shown in the help command
    '''

    # Get the latency of the bot
    latency = client.latency  # Included in the Discord.py library
    # Send it to the user
    await ctx.send(latency)


async def is_staff(ctx):
    for permissionRole in ctx.author.roles:
        if permissionRole.id == int(os.environ['roleIDOfficer']) or permissionRole.id == int(
                os.environ['roleIDLeader']):
            return True


def nickOrName(dabbermember):
    if dabbermember.nick is not None:
        return dabbermember.nick
    else:
        return dabbermember.name

@client.command()
@commands.check(is_staff)
async def nicknameemojis(ctx):
    for dabbymember in ctx.guild.members:
        emojiRoleFound = False
        if dabbymember is not ctx.guild.owner and dabbymember.id is not int(os.environ['roleIDLeader']):

            for emojiRole in dabbymember.roles:
                if emojiRole.id == int(os.environ['roleIDOfficer']) or emojiRole.id == int(os.environ['roleIDLeader']):
                    if os.environ['emojiIDStaff'] not in nickOrName(dabbymember):
                        emojiRoleFound = True
                        await dabbymember.edit(nick=os.environ['emojiIDStaff'] + " " + nickOrName(dabbymember))
                    else:
                        emojiRoleFound = True
                        await dabbymember.edit(nick=nickOrName(dabbymember).replace(os.environ['emojiIDStaff'], os.environ['emojiIDStaff'] + " "))

            if not emojiRoleFound:

                for emojiRole in dabbymember.roles:

                    if emojiRole.id == int(os.environ['roleIDMember']):
                        if (os.environ['emojiIDMember'] not in nickOrName(dabbymember)):
                            emojiRoleFound = True
                            await dabbymember.edit(nick=os.environ['emojiIDMember'] + " " + nickOrName(dabbymember))
                        else:
                            emojiRoleFound = True
                            await dabbymember.edit(nick=nickOrName(dabbymember).replace(os.environ['emojiIDMember'], os.environ['emojiIDMember'] + " "))

            if not emojiRoleFound:

                for emojiRole in dabbymember.roles:

                    if emojiRole.id == int(os.environ['roleIDFriend']):
                        if (os.environ['emojiIDMember'] not in nickOrName(dabbymember)):
                            emojiRoleFound = True
                            await dabbymember.edit(nick=os.environ['emojiIDFriend'] + nickOrName(dabbymember))
                        else:
                            emojiRoleFound = True
                            await dabbymember.edit(nick=nickOrName(dabbymember).replace(os.environ['emojiIDFriend'], os.environ['emojiIDFriend'] + " "))


# await client.user.edit(username="Cephalon Lobby") #This can be used to change the bot username


# NEW MEMBER REACTION ROLES

@client.event
async def on_raw_reaction_add(
        payload):  # Will be dispatched every time a user adds a reaction to a message the bot can see
    role = ""
    badBool = False
    inviterBool = False

    print("Reaction added")
    if not payload.guild_id:
        # In this case, the reaction was added in a DM channel with the bot
        print("Dafuq")
        return

    guild = client.get_guild(payload.guild_id)  # You need the guild to get the member who reacted
    member = guild.get_member(payload.user_id)  # Now you have the key part, the member who should receive the role

    if payload.message_id != int(os.environ['messageID']):
        print(os.environ['messageID'])
        print(payload.message_id)
        print("Not role reaction")

        conn = psycopg2.connect(DATABASE_URL, sslmode='require')

        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM mentionMessageTable WHERE id=%s", (str(payload.message_id),))
            mentionMessage = cur.fetchone()
            for memberRole in member.roles:
                if memberRole.id == int(os.environ['inviterRoleID']) or memberRole.id == int(
                        os.environ['recruiterRoleID']):
                    inviterBool = True
                    break
            if mentionMessage[0] == payload.message_id and str(payload.emoji) == str(
                    os.environ['emojiIDInviter']) and inviterBool:
                cur.execute("DELETE FROM mentionMessageTable WHERE id=%s;", (str(payload.message_id),))
                conn.commit()
                welcomeChannel = client.get_channel(int(os.environ['welcomeChannelID']))
                print("Message ID matches inviter ping message id, sending welcome message...")
                await welcomeChannel.send("Welcome " + "<@" + mentionMessage[1] + ">" + "!" + """

You're now invited to the in-game clan, please check your inbox in-game!

To gain access to the clan dojo you'll have to build a Clan Key, you will be granted the blueprint for this immediately upon joining the clan in-game.

Feel free to ask us any questions you might have about the game.

Also please take a quick read through """ + client.get_channel(
                    389879532636733461).mention + """ and """ + client.get_channel(421809355676188701).mention + """

Have fun!""")
            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
        return

    print("Reaction added to message")

    if str(payload.emoji) == str(os.environ[
                                     'emojiIDMember']):  # payload.emoji is a PartialEmoji. You have different possibilities to check for a proper reaction
        print("Emoji matches")
        role = guild.get_role(int(os.environ['roleIDMember']))  # You also need the role
        messageChannel = client.get_channel(int(os.environ['inviterChannelID']))

        if member.nick is not None:

            if "*" in member.nick:
                await member.edit(nick=payload.emoji + member.name)

            mentionMessageDab = await messageChannel.send(os.environ['inviterPingMessage'] + " and " + os.environ[

                'recruiterPingMessage'] + " please invite " + member.nick + " to the clan.")


        else:

            errorMessage = await                 messageChannel.send(member.mention + """ Please read through this whole message before doing anything. 


        If your Warframe ign and your discord username are different please change your discord nickname on this server to """ + member.name + """


        If your discord username is the same as your Warframe ign then please change your nickname to just "*"


        To change your discord nickname on desktop you have to right click the mention (the first word in this message) and press "change nickname". On mobile this is done by going to the channel selection menu by clicking on the three lines in the top left, pressing "team hydra" and then pressing change nickname.


        If you need help with anything concerning this process feel free to contact any of the officers or leaders on this server and we’ll help you out.

        """)
            time.sleep(10)

            await errorMessage.delete()

            return
        try:
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            cur = conn.cursor()
            cur.execute("INSERT INTO mentionMessageTable VALUES (%s, %s);",
                        (str(mentionMessageDab.id), str(payload.user_id)))
            conn.commit()
            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()

        print("Sent message")
    # Gotta do same thing for friends
    elif str(payload.emoji) == str(os.environ['emojiIDFriend']):
        role = guild.get_role(int(os.environ['roleIDFriend']))
    else:
        # An improper emoji has been used to react to the message
        print("Wrong emoji")
        print(os.environ['emojiIDFriend'])
        print(os.environ['emojiIDMember'])
        print(payload.emoji)
        badBool = True

    reactionChannel = client.get_channel(payload.channel_id)
    reactionMessage = await reactionChannel.get_message(payload.message_id)
    await reactionMessage.remove_reaction(payload.emoji, member)
    if badBool == False:
        await member.add_roles(role, reason='Invited to clan')  # Finally add the role to the member
        await member.add_roles(guild.get_role(int(os.environ['roleIDSeparator'])),
                               reason='Invited to clan')  # Finally add the role to the member
        await member.remove_roles(guild.get_role(int(os.environ['roleIDPending'])))
        print("Added role")


client.run(os.environ['discordToken'])
