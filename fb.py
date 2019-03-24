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

def paramquotationlist(p):
    params = []
    while True:
        try:
            p1 = p.index("\""); p = p[:p1] + p[p1 + 1:]
            p2 = p.index("\""); p = p[:p2] + p[p2 + 1:]
            params.append(p[p1:p2])
        except ValueError:
            if params == []: return None
            return params

def paramnumberlist(p):
    params = []; i = -1; tempparam = [""]; inquotations = False; addingdone = True
    while True:
        try:
            i += 1
            tp = int(p[i])
            if not inquotations:
                addingdone = False
                tempparam[0] += str(tp)
        except ValueError:
            if p[i] == "\"":
                if inquotations: inquotations = False
                elif not inquotations: inquotations = True
            if p[i] == " " and not inquotations and not addingdone:
                params.append(int(tempparam[0]))
                tempparam[0] = ""
                addingdone = True
        except IndexError:
            if not addingdone:
                params.append(int(tempparam[0]))
                tempparam[0] = ""
            if params == []: return None
            return params

def paramlistlist(p,i):
    params = paramquotationlist(p)
    if params is None: return None
    if len(params) == 0: return None
    params = params[i]; params = params.split(",")
    for n in params:
        if str(n).startswith(" "): params[params.index(n)] = n[1:]
        if n[len(n) - 1] == " ": params[params.index(n)] = n[:len(n) - 1]
    return params

def BotHasPermissions(ctx):
    if not ctx.message.guild: return True
    for member in ctx.guild.members:
        if str(member.id) == str(client.user.id):
            for role in member.roles:
                if role.permissions.administrator and role.permissions.manage_messages: return True
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

async def ReactionChoiceMessage(ctx,reactionmessage,choices: int):
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
    except asyncio.TimeoutError: await reactionmessage.clear_reactions()
    else: return reactionresponse
    return 0

def PREListCompare(parameters,newparameters):
    PRECheck = True
    for np in newparameters:
        for p in parameters:
            if np[0] == p[0] and np[1] == p[1]:
                if np[2] == p[2] and p[3]: PRECheck = False
    return PRECheck

async def ParameterResponseEmbed(ctx,title,parameters: list):
    global newparameters; global responsedonecalled
    # parameters: [['name','string',"",True],['parts','integer',0,True],['creators','list',[],False]]
    if len(parameters) == 0: return []
    newparameters = []
    for param in parameters: newparameters.append(param)
    responseembed = discord.Embed(title=title,description=
    "*Type >>param \"parameter\" \"new value(s)\" to change conditions, and >>done when done*",color=0x5c5c5c)
    for param in newparameters:
        paramr = " "
        if param[3]: paramr = " *"
        paramvalue = ""
        if param[1] == "string": paramvalue = param[2]
        if param[1] == "integer": paramvalue = str(param[2])
        if param[1] == "list":
            if not param[2]: paramvalue = "None"
            else:paramvalue = str(param[2]).replace("[","").replace("]","")
        responseembed.add_field(name=param[0] + paramr,value=paramvalue,inline=False)
        newparameters[newparameters.index(param)].append(newparameters.index(param))
    responseembedmessage = await ctx.message.channel.send(embed=responseembed)
    responsedonecalled = False
    def check(message):
        global newparameters; global responsedonecalled
        if str(message.content).startswith(">>done"): responsedonecalled = True; return True
        if str(message.content).startswith(">>param "):
            paramresponse = str(message.content).replace(">>param",""); paramq = paramquotationlist(paramresponse)
            if paramq is None: return False
            if len(paramq) != 2: return False
            for p in newparameters:
                if str(p[0]).lower() == str(paramq[0]).lower():
                    if p[1] == "list": paramq[1] = paramlistlist(paramresponse,1)
                    newparameters[newparameters.index(p)][2] = paramq[1]
                    responseembed.set_field_at(p[4],name=p[0],value=str(paramq[1]))
                    return True
        return False
    while True:
        if responsedonecalled: break
        try:
            message = await client.wait_for('message',timeout=60.0,check=check)
        except asyncio.TimeoutError: return []
        else:
            await responseembedmessage.edit(embed=responseembed)
            await message.add_reaction(CHAR_SUCCESS)
    if not PREListCompare(parameters,newparameters): return None
    return newparameters


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
            if BotHasPermissions(ctx):
                hostServer = await ctx.message.channel.send("Ready to host a new Megacollab?\n"
                                                            "**A** - In this Server\n"
                                                            "**B** - Create a new Server")
                hostServerResponse = await ReactionChoiceMessage(ctx,hostServer,2)
                await hostServer.clear_reactions()
                if hostServerResponse == 1 or hostServerResponse == 2:
                    hostMC_NAME = "None"
                    hostMC_SONG = "None"
                    hostMC_DIFFICULTY = "Extreme Demon"
                    hostMC_OTHERHOSTS = []
                    hostMC_PARTS = 4
                    hostMC1R = await ParameterResponseEmbed(ctx,"Start a Megacollab",[["Name","string",hostMC_NAME,True],
                                                                                      ["Song","string",hostMC_SONG,True],
                                                                                      ["Difficulty","string",hostMC_DIFFICULTY,True],
                                                                                      ["Other Hosts","list",hostMC_OTHERHOSTS,False],
                                                                                      ["Parts","integer",hostMC_PARTS,False]])
                    print(hostMC1R)
                    if hostServerResponse == 2:
                        await ResponseMessage(ctx,"Server for Megacollabs are not supported yet!","failed")
                    elif hostServerResponse == 1:
                        hostMC_SERVER = ctx.message.guild
            else:
                await ResponseMessage(ctx,"","failed","botlacksperms")
        else:
            await ResponseMessage(ctx,"You need to be in a Server to perform this!","failed")
    else:
        await ResponseMessage(ctx,"","failed","authorlacksperms")




client.run(SECRET)