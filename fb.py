import discord, asyncio, sys, os, urllib.request, json, math, random, ast, datetime, base64, time
from discord.ext import commands

Client = discord.Client()
bot_prefix= "??"
client = commands.Bot(command_prefix=bot_prefix)

s = None
try: s = open("pass.txt","r")
except: sys.exit("[Error] pass.txt needed for Secret")
sl = []
for l in s: sl.append(l.replace("\n",""))
SECRET = sl[0]

CHAR_SUCCESS = "✅"
CHAR_FAILED = "❌"
CHAR_CONFIRM = "✔"
CHAR_CANCEL = "✖"

CHAR_A = "🇦"
CHAR_B = "🇧"
CHAR_C = "🇨"
CHAR_D = "🇩"
CHAR_E = "🇪"

def datasettings(file,method,line="",newvalue="",newkey=""):
    """
    :param file: (str).txt
    :param method: (str) get,change,remove,add
    :param line: (str)
    :param newvalue: (str)
    :param newkey: (str)
    """
    s = None
    try: s = open(file,"r")
    except: return None
    sl = []
    for l in s: sl.append(l.replace("\n",""))
    for nl in sl:
        if str(nl).startswith(line):
            if method == "get": s.close(); return str(nl).replace(line + "=","")
            elif method == "change": sl[sl.index(nl)] = line + "=" + newvalue; break
            elif method == "remove": sl[sl.index(nl)] = None; break
    if method == "add": sl.append(newkey + "=" + newvalue)
    if method == "get": return None
    s.close()
    s = open(file,"w")
    s.truncate()
    slt = ""
    for nl in sl:
        if nl is not None:
            slt += nl + "\n"
    s.write(slt); s.close(); return None

def alldatakeys(file) -> list:
    s = None
    try: s = open(file,"r")
    except: return []
    sl = []
    for l in s: sl.append(l.replace("\n", ""))
    for nl in sl:
        nla = str(nl).split("=")
        sl[sl.index(nl)] = nla[0]
    s.close()
    for nl in sl:
        if nl == "": sl.remove(nl)
    return sl

def cleardata(file):
    s = None
    try: s = open(file,"w")
    except: return
    s.truncate(); s.close()

def BotHasPermissions(ctx):
    if not ctx.message.guild: return True
    for member in ctx.guild:
        if str(member.id) == str(client.user.id):
            if member.guild.owner: return True
            for role in member.roles:
                if role.permissions.administrator: return True
    return False

def AuthorHasPermissions(ctx):
    if not ctx.message.guild: return True
    if ctx.author.guild.owner: return True
    for role in ctx.author.roles:
        if role.permissions.administrator: return True
    return False

async def ResponseMessage(ctx,response,messagereaction,preset=""):
    if preset != "":
        pi = {"authorlacksperms":"You do not have Permission to perform this!",
              "botlacksperms":client.user.name + " does not have Permissions to perform this!",
              "invalidparams":"Invalid parameters!"}
        response = pi[preset]
    await ctx.message.channel.send("**" + ctx.author.name + "**, " + response)
    mri = {"success":CHAR_SUCCESS,"failed":CHAR_FAILED}
    await ctx.message.add_reaction(mri[messagereaction])

async def ClearReactions(message):
    for reaction in message.reactions:
        async for user in reaction.users():
            await reaction.remove(user)

async def ReactionChoiceMessage(ctx,reactionmessage,choices):
    global reactionresponse
    # Max Reaction Choices = 5
    nif = {1:CHAR_A,2:CHAR_B,3:CHAR_C,4:CHAR_D,5:CHAR_E}
    nib = {CHAR_A:1,CHAR_B:2,CHAR_C:3,CHAR_D:4,CHAR_E:5}
    if choices == 0 or choices > 5: await reactionmessage.add_reaction(CHAR_CONFIRM)
    else:
        for n in range(1,6):
            if n <= choices: await reactionmessage.add_reaction(nif[n])
    await reactionmessage.add_reaction(CHAR_CANCEL)
    reactionresponse = 0
    # 0=None, 1-5=1-5, 6=Confirm, 7=Cancel
    def check(reaction,user):
        global reactionresponse
        if user == ctx.message.author:
            if choices == 0 and str(reaction.emoji) == CHAR_CONFIRM: reactionresponse = 6; return True
            try:
                if 1 <= nib[str(reaction.emoji)] <= choices: reactionresponse = nib[str(reaction.emoji)]; return True
            except KeyError: pass
            if str(reaction.emoji) == CHAR_CANCEL: reactionresponse = 7; return True
        return False
    try:
        reaction, user = await client.wait_for('reaction_add',timeout=60.0,check=check)
    except asyncio.TimeoutError: ClearReactions(reactionmessage)
    else: return reactionresponse
    return 0


@client.event
async def on_ready():
    print("Bot Ready!")
    print("Name: " + client.user.name + ", ID: " + str(client.user.id))
    sl = ""
    for server in client.guilds:
        if server is not None: sl += server.name + ", "
    print("Connected Guilds: " + sl[:len(sl) - 2])


@client.command(pass_context=True)
async def host(ctx):
    if AuthorHasPermissions(ctx):
        if ctx.guild:
            hostServer = await ctx.message.channel.send("Ready to host a new Megacollab?\n"
                                                        "**A** - In this Server\n"
                                                        "**B** - Create a new Server")
            hostServerResponse = await ReactionChoiceMessage(ctx,hostServer,2)
            print(hostServerResponse)

        else:
            await ResponseMessage(ctx,"You need to be in a Server to perform this!","failed")
    else:
        await ResponseMessage(ctx,"","failed","invalidparams")




client.run(SECRET)