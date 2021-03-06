import discord, asyncio, sys, os, random, datetime,copy, pickle, traceback, shutil, re
from discord.ext import commands

Client = discord.Client()
bot_prefix= "??"
client = commands.Bot(command_prefix=bot_prefix)
client.remove_command("help")

s = None
try: s = open("pass.txt","r")
except: sys.exit("[Error] pass.txt needed for Secret")
sl = []
for l in s: sl.append(l.replace("\n",""))
SECRET = sl[0]


# https://discordapp.com/api/oauth2/authorize?client_id=558890112855834624&permissions=0&scope=bot

CHAR_SUCCESS = "✅"
CHAR_FAILED = "❌"
CHAR_CONFIRM = "✔"
CHAR_CANCEL = "✖"

CHAR_A = "🇦"
CHAR_B = "🇧"
CHAR_C = "🇨"
CHAR_D = "🇩"
CHAR_E = "🇪"

EMOJI_EMPTY = "<:empty:560341877212315658>"
EMOJI_ASSIGNED = "<:assigned:560341866445537300>"
EMOJI_PROGRESS = "<:progress:560341884992487425>"
EMOJI_FINISHED = "<:finished:560341892881973248>"
statusEmoji = {"empty":EMOJI_EMPTY,"assigned":EMOJI_ASSIGNED,"progress":EMOJI_PROGRESS,"finished":EMOJI_FINISHED}



def isnumber(n):
    try: nn = int(n); return True
    except: return False

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

def latestdata(file):
    ld = alldatakeys(file)
    if ld == []: return None
    return ld[len(ld) - 1]

def cleardata(file):
    s = None
    try: s = open(file,"w")
    except: return
    s.truncate(); s.close()

def newfile(file):
    s = None
    try:
        s = open(file, "r")
        return None
    except: pass
    f = open(file,"a")
    f.close()

MEDIAFOLDER = "fp-savedmedia/"

async def datamedia(method,message,filename=""):
    global MEDIAFOLDER
    """
    :param method: save,send
    """
    savedattachments = []
    if method == "save":
        ati = 0
        for attachment in message.attachments:
            atype = attachment.filename[attachment.filename.index("."):]
            await attachment.save(MEDIAFOLDER + str(message.guild.id) + "-" + str(message.id) + "-" + str(ati) + atype)
            savedattachments.append(MEDIAFOLDER + str(message.guild.id) + "-" + str(message.id) + "-" + str(ati) + atype)
            ati += 1
        return savedattachments
    if method == "send":
        with open(filename,"rb") as dmi:
            await message.channel.send(file=discord.File(fp=dmi))


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


def GetMember(mn,s):
    if str(mn).startswith("<@"):
        mid = mn.replace("<@",""); mid = mid.replace(">","")
        return discord.utils.find(lambda m: str(mid) in str(m.id), s.members)
    try:
        mid = int(mn)
        return discord.utils.find(lambda m: str(mid) in str(m.id), s.members)
    except: return discord.utils.find(lambda m: mn.lower() in m.name.lower(), s.members)

def GetMemberGlobal(mn):
    if mn is None: return None
    if mn == "None": return None
    for s in client.guilds:
        if str(mn).startswith("<@"):
            mid = mn.replace("<@",""); mid = mid.replace(">","")
            mt = discord.utils.find(lambda m: str(mid) in str(m.id), s.members)
            if mt is not None: return mt
        try:
            mid = int(mn)
            mt = discord.utils.find(lambda m: str(mid) in str(m.id), s.members)
            if mt is not None: return mt
        except:
            mt = discord.utils.find(lambda m: mn.lower() in m.name.lower(), s.members)
            if mt is not None: return mt
    return client.get_user(mn)

def GetRole(s,rn):
    try:
        rid = int(rn)
        return discord.utils.find(lambda r: str(rid) in str(r.id), s.roles)
    except:
        try: return discord.utils.find(lambda r: rn.lower() in r.name.lower(), s.roles)
        except: return None

def GetChannel(s,cn):
    if str(cn).startswith("<#"):
        cid = cn.replace("<#",""); cid = cid.replace(">","")
        return discord.utils.find(lambda m: str(cid) in str(m.id), s.channels)
    try:
        cid = int(cn)
        return discord.utils.find(lambda m: str(cid) in str(m.id), s.channels)
    except: return discord.utils.find(lambda m: cn.lower() in m.name.lower(), s.channels)

def GetGuild(sid):
    for guild in client.guilds:
        if str(guild.id) == str(sid): return guild
        if sid in guild.name: return guild
    return None

async def GetMessage(channel,mid):
    async for message in channel.history(limit=200):
        if str(message.id) == str(mid): return message

def BotHasPermissions(ctx):
    if not ctx.message.guild: return True
    for member in ctx.guild.members:
        if str(member.id) == str(client.user.id):
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
              "invalidparams":"Invalid parameters!",
              "nomc":"You are not in a Megacollab here!",
              "nothost":"You are not the Host of this Megacollab!"}
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
                if np[2] == p[2] and p[3] and np[3]:
                    PRECheck = False
    return PRECheck

newparametersglobal = {}
responsedonecalledglobal = {}
parammediaglobal = {}

async def ParameterResponseEmbed(ctx,title,parameters: list):
    global newparametersglobal; global responsedonecalledglobal; global parammediaglobal
    paramauthor = ctx.author
    # parameters: [['name','string',"",True],['parts','integer',0,True],['creators','list',[],False],['progress','media','None',False]]
    # param types: string, integer, list, discord user, list of discord users, boolean
    if len(parameters) == 0: return []
    newparameters = copy.deepcopy(parameters); newparametersglobal.update({ctx.author.id:newparameters})
    responseembed = discord.Embed(title=title,description=
    "*Type >>param \"parameter\" \"new value(s)\" to change conditions, and >>done when done*",color=0x5c5c5c)
    for param in newparameters:
        if param != ctx.author.id:
            paramr = " "
            if param[3]: paramr = " *"
            paramvalue = ""
            if param[1] == "string": paramvalue = param[2]
            if param[1] == 'media': paramvalue = param[2]
            if param[1] == "boolean": paramvalue = param[2]
            if param[1] == "integer": paramvalue = str(param[2])
            if param[1] == "list":
                if not param[2]: paramvalue = "None"
                else: paramvalue = str(param[2]).replace("[","").replace("]","")
            if param[1] == "discord user":
                paramvalue = GetMember(param[2],ctx.guild)
                if paramvalue is None: paramvalue = "None"
                else: paramvalue = paramvalue.name
            if param[1] == "list of discord users":
                if not param[2]: paramvalue = "None"
                else:
                    paramvalue = []
                    for pv in param[2]: paramvalue.append(pv)
                    for p in paramvalue:
                        tp = GetMember(p,ctx.guild)
                        if tp is None: paramvalue[paramvalue.index(p)] = "None"
                        else: paramvalue[paramvalue.index(p)] = tp.name
                    paramvalue = str(paramvalue)
                    newparameters[newparameters.index(param)][2] = StrToLODU(param[2],ctx.guild)
            responseembed.add_field(name=param[0] + paramr,value=paramvalue,inline=False)
            newparameters[newparameters.index(param)].append(newparameters.index(param))
    responseembedmessage = await ctx.message.channel.send(embed=responseembed)
    responsedonecalled = False; responsedonecalledglobal.update({ctx.author.id:responsedonecalled})
    parammediaglobal.update({ctx.author.id:None})
    def check(message):
        if message.author == paramauthor:
            global newparametersglobal; global responsedonecalledglobal; global parammediaglobal
            newparameters = newparametersglobal[message.author.id]
            if str(message.content).startswith(">>done"): responsedonecalledglobal[message.author.id] = True; return True
            if str(message.content).startswith(">>param "):
                paramresponse = str(message.content).replace(">>param",""); paramq = paramquotationlist(paramresponse)
                if paramq is None: return False
                if len(paramq) == 1:
                    for p in newparameters:
                        if str(p[0]).lower() == str(paramq[0]).lower():
                            if p[1] == "media":
                                parammediamessage = ""
                                if message.attachments:
                                    for mat in message.attachments: parammediamessage += "Media "
                                    parammediaglobal[ctx.author.id] = [message,p[4],p[0]]
                                    responseembed.set_field_at(p[4],name=p[0],value=parammediamessage,inline=False)
                                    return True
                            else: return False
                if len(paramq) != 2: return False
                for p in newparameters:
                    if str(p[0]).lower() == str(paramq[0]).lower():
                        paramql = []
                        if p[1] == "boolean":
                            if paramq[1].lower() != "false" and paramq[1].lower() != "true": return False
                        if p[1] == "list": paramq[1] = paramlistlist(paramresponse,1)
                        if p[1] == "discord user":
                            paramq[1] = GetMember(paramq[1],ctx.guild)
                            if paramq[1] is None: return False
                        if p[1] == "list of discord users":
                            paramq[1] = paramlistlist(paramresponse, 1)
                            paramql = paramq[1]
                            for pq in paramql:
                                pqt = GetMember(pq,ctx.guild)
                                if pqt is None: return False
                                paramql[paramql.index(pq)] = pqt
                            paramq[1] = paramql
                        newparameters[newparameters.index(p)][2] = paramq[1]
                        responseembed.set_field_at(p[4],name=p[0],value=str(paramq[1]),inline=False)
                        if p[1] == "discord user": responseembed.set_field_at(p[4],name=p[0],value=paramq[1].name,inline=False)
                        if p[1] == "list of discord users":
                            newparameters[newparameters.index(p)][2] = paramql
                            paramq[1] = []
                            for q in paramql: paramq[1].append(q)
                            for pq in paramq[1]:
                                paramq[1][paramq[1].index(pq)] = pq.name
                            responseembed.set_field_at(p[4], name=p[0], value=str(paramq[1]),inline=False)
                        return True
        return False
    while True:
        if responsedonecalledglobal[ctx.author.id]: break
        try:
            message = await client.wait_for('message',timeout=120.0,check=check)
        except asyncio.TimeoutError:
            return []
        else:
            if parammediaglobal[ctx.author.id] is not None:
                mats = await datamedia(method="save",message=parammediaglobal[ctx.author.id][0])
                for p in newparameters:
                    if str(p[0]).lower() == str(parammediaglobal[ctx.author.id][2]).lower():
                        matm = ""
                        for an in mats: matm += an + " "
                        responseembed.set_field_at(parammediaglobal[ctx.author.id][1],
                                                   name=parammediaglobal[ctx.author.id][2], value=matm, inline=False)
                        newparameters[newparameters.index(p)][2] = mats
                        parammediaglobal[ctx.author.id] = None
                        break
            await responseembedmessage.edit(embed=responseembed)
            await message.add_reaction(CHAR_SUCCESS)
    if not PREListCompare(parameters,newparametersglobal[ctx.author.id]):
        for gd in list(newparametersglobal):
            if gd == ctx.author.id: del newparametersglobal[gd]
        for gd in list(responsedonecalledglobal):
            if gd == ctx.author.id: del responsedonecalledglobal[gd]
        return None
    newparametersreturn = newparametersglobal[ctx.author.id]
    for gd in list(newparametersglobal):
        if gd == ctx.author.id: del newparametersglobal[gd]
    for gd in list(responsedonecalledglobal):
        if gd == ctx.author.id: del responsedonecalledglobal[gd]
    for gd in list(parammediaglobal):
        if gd == ctx.author.id: del parammediaglobal[gd]
    return newparametersreturn

def RandomColor():
    return discord.Color.from_rgb(r=random.randint(0,255),g=random.randint(0,255),b=random.randint(0,255))

def GetAdminRole(ctx,user):
    for member in ctx.message.guild.members:
        if str(member.id) == str(user.id):
            for role in member.roles:
                if role.permissions.administrator and role.permissions.manage_messages: return role
    return None

async def MCContext(ctx):
    """
    0: Name
    1: Song
    2: Difficulty
    3: Parts
    4: Co-Hosts
    5: Verifier
    6: Host
    7: Server
    8: ID
    """
    mcsfound = []
    for mcid in alldatakeys("fp-mcdir.txt"):
        mcd = datasettings(file="fp-mcdir.txt",method="get",line=mcid); mcd = mcd.split(";")
        mcd.append(mcid)
        mchost = GetMemberGlobal(mcd[6]); mcserver = GetGuild(mcd[7])
        if mchost is None: continue
        if mcserver is None: continue
        mcd[6] = mchost; mcd[7] = mcserver
        mcd[4] = GetMemberGlobal(mcd[4]); mcd[5] = StrToLODU(mcd[5],ctx.guild)
        if mchost == ctx.author and mcserver == ctx.guild: mcsfound.append(mcd)
        for n in range(1, int(mcd[3]) + 1):
            nCreators = StrToLODU(datasettings(file="fp-mc/" + mcd[8] + "/PART" + str(n) + ".txt", method="get", line="CREATORS"),ctx.guild)
            for c in nCreators:
                if c == ctx.author and mcserver == ctx.guild and mcd not in mcsfound: mcsfound.append(mcd)
    if not mcsfound: return None
    if len(mcsfound) == 1: return mcsfound[0]
    else:
        iin = 1; mcfmcs = ""
        for mc in mcsfound:
            iil = "**A** - "
            if iin == 2: iil = "**B** - "
            if iin == 3: iil = "**C** - "
            if iin == 4: iil = "**D** - "
            if iin == 5: iil = "**E** - "
            mcfmcs += iil + mc[0] + "\n"
            iin += 1
        mcfm = await ctx.message.channel.send("**" + ctx.author.name + "**, which megacollab are you referring to?\n" + mcfmcs)
        mcmresponse = await ReactionChoiceMessage(ctx,mcfm,iin - 1)
        if 1 <= mcmresponse <= 5: return mcsfound[mcmresponse - 1]
        else: return None

async def SimMCContext(sguild,smember,schannel):
    """
        0: Name
        1: Song
        2: Difficulty
        3: Parts
        4: Co-Hosts
        5: Verifier
        6: Host
        7: Server
        8: ID
        """
    mcsfound = []
    for mcid in alldatakeys("fp-mcdir.txt"):
        mcd = datasettings(file="fp-mcdir.txt", method="get", line=mcid); mcd = mcd.split(";")
        mcd.append(mcid)
        mchost = GetMemberGlobal(mcd[6]); mcserver = GetGuild(mcd[7])
        if mchost is None: continue
        if mcserver is None: continue
        mcd[6] = mchost; mcd[7] = mcserver
        mcd[4] = GetMemberGlobal(mcd[4]); mcd[5] = StrToLODU(mcd[5], sguild)
        if mchost == smember and mcserver == sguild: mcsfound.append(mcd)
        for n in range(1, int(mcd[3]) + 1):
            nCreators = StrToLODU(
                datasettings(file="fp-mc/" + mcd[8] + "/PART" + str(n) + ".txt", method="get", line="CREATORS"),
                sguild)
            for c in nCreators:
                if c == smember and mcserver == sguild and mcd not in mcsfound: mcsfound.append(mcd)
    if not mcsfound: return None
    if len(mcsfound) == 1:
        return mcsfound[0]
    else:
        iin = 1; mcfmcs = ""
        for mc in mcsfound:
            iil = "**A** - "
            if iin == 2: iil = "**B** - "
            if iin == 3: iil = "**C** - "
            if iin == 4: iil = "**D** - "
            if iin == 5: iil = "**E** - "
            mcfmcs += iil + mc[0] + "\n"
            iin += 1
        await schannel.send("**" + smember.name + "**, which megacollab are you referring to?\n" + mcfmcs)

def AutoMCContext(channel,user):
    """
    0: Name
    1: Song
    2: Difficulty
    3: Parts
    4: Co-Hosts
    5: Verifier
    6: Host
    7: Server
    8: ID
    """
    mcsfound = []
    for mcid in alldatakeys("fp-mcdir.txt"):
        mcd = datasettings(file="fp-mcdir.txt",method="get",line=mcid); mcd = mcd.split(";")
        mcd.append(mcid)
        mchost = GetMemberGlobal(mcd[6]); mcserver = GetGuild(mcd[7])
        if mchost is None: continue
        if mcserver is None: continue
        mcd[6] = mchost; mcd[7] = mcserver
        try: mcd[4] = GetMemberGlobal(mcd[4]); mcd[5] = StrToLODU(mcd[5],channel.guild)
        except: return None
        if mchost == user and mcserver == channel.guild: mcsfound.append(mcd)
    if not mcsfound: return None
    if len(mcsfound) == 1: return mcsfound[0]
    else:
        for mcc in mcsfound:
            msChannelParts = GetChannel(channel.guild,
                                        datasettings(file="fp-mc/" + mcc[8] + ".txt", method="get", line="CHANNEL-PARTS"))
            msChannelUpdates = GetChannel(channel.guild, datasettings(file="fp-mc/" + mcc[8] + ".txt", method="get",
                                                                          line="CHANNEL-UPDATES"))
            msChannelProgress = GetChannel(channel.guild, datasettings(file="fp-mc/" + mcc[8] + ".txt", method="get",
                                                                           line="CHANNEL-PROGRESS"))
            msChannelFinishedParts = GetChannel(channel.guild,
                                                datasettings(file="fp-mc/" + mcc[8] + ".txt", method="get",
                                                             line="CHANNEL-FINISHEDPARTS"))
            if msChannelParts is not None:
                if channel == msChannelParts: return mcc
            if msChannelUpdates is not None:
                if channel == msChannelUpdates: return mcc
            if msChannelFinishedParts is not None:
                if channel == msChannelFinishedParts: return mcc
            if msChannelProgress is not None:
                if channel == msChannelProgress: return mcc
        return None

def StrToLODU(st,g):
    if st == "[]": return []
    stm = str(st).replace("[","").replace("]","").replace("'",""); stm = stm.split(",")
    if not isinstance(stm,(list,)):
        stm = [stm.replace("[","").replace("]","").replace("'","")]
    for u in stm: stm[stm.index(u)] = GetMember(u,g)
    return stm

def DUToStr(du):
    dus = "None"
    try: dus = du.name
    except: pass
    return dus

def StrToList(st):
    stm = st.replace("[", "").replace("]", "").replace("'","")
    stm = stm.split(",")
    if not isinstance(stm,(list,)):
        stm = [stm.replace("[","").replace("]","").replace("'","")]
    for s in stm:
        if s.startswith(" "): stm[stm.index(s)] = s[1:]
    return stm


def LODUToStr(l):
    if not l: return "None"
    ll = []
    for lt in l: ll.append(lt)
    for du in ll:
        dus = "None"
        try: dus = du.id
        except: pass
        ll[ll.index(du)] = dus
    return str(ll)

def LODUToStrName(l):
    if not l: return "None"
    ll = []
    for lt in l: ll.append(lt)
    for du in ll:
        dus = "None"
        try: dus = du.name
        except: pass
        ll[ll.index(du)] = dus
    return str(ll).replace("[","").replace("]","").replace("'","")

def StrToDatetime(st):
    stm = st
    try: stm = stm.split(" "); stm = stm[0]
    except: pass
    stm = stm.split("-")
    return datetime.datetime(day=int(stm[2]),month=int(stm[1]),year=int(stm[0]))

def DatetimeToStr(dt):
    dtm = str(dt).split(" ")
    return dtm[0]


def IsHost(ctx,mc):
    if mc[6] == ctx.message.author: return True
    return ctx.message.author in mc[4]

def PartsMessage(mcid,pos,s):
    pmCreators = LODUToStrName(StrToLODU(datasettings(file="fp-mc/" + mcid + "/PART" + pos + ".txt",method="get",line="CREATORS"),s))
    pmGroups = datasettings(file="fp-mc/" + mcid + "/PART" + pos + ".txt",method="get",line="GROUPS")
    pmColors = datasettings(file="fp-mc/" + mcid + "/PART" + pos + ".txt",method="get",line="COLORS")
    pmTime = datasettings(file="fp-mc/" + mcid + "/PART" + pos + ".txt",method="get",line="TIME")
    pmStatus = datasettings(file="fp-mc/" + mcid + "/PART" + pos + ".txt",method="get",line="STATUS")
    if pmStatus is None: pmStatus = statusEmoji["empty"]
    else: pmStatus = statusEmoji[pmStatus.lower()]
    pmType = datasettings(file="fp-mc/" + mcid + "/PART" + pos + ".txt",method="get",line="PARTDESC")
    pmNumber = "**Part " + str(pos) + "**"
    if "art" in pmType.lower(): pmNumber += " [" + pmType + "]"
    pm = pmStatus + " " + pmTime + " - " + pmCreators + " - Colors: " + pmColors + " - Groups: " + pmGroups + " - " + pmNumber
    return pm

def CheckIfArtPart(mcid,pos):
    pmType = datasettings(file="fp-mc/" + mcid + "/PART" + pos + ".txt", method="get", line="PARTDESC")
    if "art" in pmType.lower(): return True
    return False

def AllPartsMessage(mc):
    pmf = ""
    for n in range(1, int(mc[3]) + 1): pmf += PartsMessage(mc[8],str(n),mc[7]) + "\n"
    return pmf

async def InitGenerateParts(mc,channel):
    if datasettings(file="fp-mc/" + mc[8] + "/PART1.txt",method="get",line="CREATORS") is None:
        for n in range(1,int(mc[3]) + 1):
            newfile("fp-mc/" + mc[8] + "/PART" + str(n) + ".txt")
            datasettings(file="fp-mc/" + mc[8] + "/PART" + str(n) + ".txt",method="add",newkey="CREATORS",newvalue="[]")
            datasettings(file="fp-mc/" + mc[8] + "/PART" + str(n) + ".txt", method="add", newkey="PARTDESC", newvalue="None")
            datasettings(file="fp-mc/" + mc[8] + "/PART" + str(n) + ".txt",method="add",newkey="GROUPS",newvalue="None")
            datasettings(file="fp-mc/" + mc[8] + "/PART" + str(n) + ".txt",method="add",newkey="COLORS",newvalue="None")
            datasettings(file="fp-mc/" + mc[8] + "/PART" + str(n) + ".txt",method="add",newkey="TIME",newvalue="0:00-0:00")
            datasettings(file="fp-mc/" + mc[8] + "/PART" + str(n) + ".txt", method="add", newkey="VIDEO", newvalue="None")
            datasettings(file="fp-mc/" + mc[8] + "/PART" + str(n) + ".txt", method="add", newkey="STATUS", newvalue="Empty")
            print(mc[0] + ": Initiated Part " + str(n))
        # Assigning Groups & Colors
        if int(mc[3]) < 20:
            # Group sets: 50 - 100 - 150 - 200
            apc = 0
            if int(mc[3]) <= 5: apc = 200
            if 5 <= int(mc[3]) <= 6: apc = 200
            if 6 <= int(mc[3]) <= 10: apc = 100
            if int(mc[3]) >= 10: apc = 50
            apn = 0
            for n in range(1, int(mc[3]) + 1):
                if n == 1:
                    datasettings(file="fp-mc/" + mc[8] + "/PART" + str(n) + ".txt", method="change", line="GROUPS",
                                 newvalue="3-" + str(apc)); apn += apc
                    datasettings(file="fp-mc/" + mc[8] + "/PART" + str(n) + ".txt", method="change", line="COLORS",
                                 newvalue="1-" + str(apc))
                else:
                    datasettings(file="fp-mc/" + mc[8] + "/PART" + str(n) + ".txt", method="change", line="GROUPS",
                                 newvalue=str(int(apn + 1)) + "-" + str(int(apn + apc)))
                    datasettings(file="fp-mc/" + mc[8] + "/PART" + str(n) + ".txt", method="change", line="COLORS",
                                 newvalue=str(int(apn + 1)) + "-" + str(int(apn + apc)))
                    apn += apc
    return await channel.send(AllPartsMessage(mc))

async def RefreshParts(mc):
    for data in alldatakeys("fp-mc/" + mc[8] + ".txt"):
        if data.startswith("MESSAGEPARTS-"):
            partsMessage = datasettings(file="fp-mc/" + mc[8] + ".txt",method="get",line=data)
            partsChannel = GetChannel(mc[7],data[data.index("-") + 1:])
            if partsChannel is None: continue
            partsMessage = await GetMessage(partsChannel,partsMessage)
            if partsMessage is None: continue
            await partsMessage.edit(content=AllPartsMessage(mc))

async def GetPart(ctx,mc,pos):
    mcid = mc[8]
    pmCreators = StrToLODU(datasettings(file="fp-mc/" + mcid + "/PART" + pos + ".txt", method="get", line="CREATORS"),ctx.guild)
    pmGroups = datasettings(file="fp-mc/" + mcid + "/PART" + pos + ".txt", method="get", line="GROUPS")
    pmColors = datasettings(file="fp-mc/" + mcid + "/PART" + pos + ".txt", method="get", line="COLORS")
    pmTime = datasettings(file="fp-mc/" + mcid + "/PART" + pos + ".txt", method="get", line="TIME")
    pmStatus = statusEmoji[datasettings(file="fp-mc/" + mcid + "/PART" + pos + ".txt", method="get", line="STATUS").lower()]
    pmType = datasettings(file="fp-mc/" + mcid + "/PART" + pos + ".txt", method="get", line="PARTDESC")
    pmNumber = "**Part " + str(pos) + "**"
    pmVideo = datasettings(file="fp-mc/" + mcid + "/PART" + pos + ".txt", method="get", line="VIDEO")
    if pmVideo.startswith("http"): pmVideo = "[Video](" + pmVideo + ")"
    else: pmVideo = "No Video"
    pmE = discord.Embed(title=ctx.author.name + "'s part in " + mc[0],description=pmVideo,color=0x5c5c5c)
    pmE.add_field(name="Status", value=pmStatus, inline=False)
    pmE.add_field(name="Creators", value=LODUToStrName(pmCreators), inline=False)
    pmE.add_field(name="Time", value=pmTime, inline=False)
    pmE.add_field(name="Description", value=pmType, inline=False)
    pmE.add_field(name="Position", value=pmNumber, inline=False)
    pmE.add_field(name="Groups", value=pmGroups, inline=False)
    pmE.add_field(name="Colors", value=pmColors, inline=False)
    await ctx.message.channel.send(embed=pmE)


def Portfolio(user):
    pBio = datasettings(file="fp-portfolio/" + str(user.id) + ".txt",method="get",line="BIO")
    if pBio is None: return None
    pVideo1 = datasettings(file="fp-portfolio/" + str(user.id) + ".txt",method="get",line="VIDEO1")
    pVideo2 = datasettings(file="fp-portfolio/" + str(user.id) + ".txt",method="get",line="VIDEO2")
    pServers = ""
    for guild in client.guilds:
        for member in guild.members:
            if str(member.id) == str(user.id): pServers += guild.name + ", "
    if pServers != "": pServers = pServers[:len(pServers) - 2]
    else: pServers = "None that the Bot is in"
    pMCS = ""
    for mcid in alldatakeys("fp-mcdir.txt"):
        mcd = datasettings(file="fp-mcdir.txt",method="get",line=mcid); mcd = mcd.split(";")
        mcpt = datasettings(file="fp-mc/" + mcid + "/PART1.txt",method="get",line="CREATORS")
        if mcpt is None: continue
        for n in range(1, int(mcd[3]) + 1):
            mcCreators = StrToLODU(datasettings(file="fp-mc/" + mcid + "/PART" + str(n) + ".txt",method="get",line="CREATORS"),user.guild)
            if user in mcCreators:
                pMCS += mcd[0] + ", "
                break
    if pMCS != "": pMCS = pMCS[:len(pMCS) - 2]
    else: pMCS = "None that the Bot is hosting"
    pE = discord.Embed(title=user.name,description=pBio,color=0x5c5c5c)
    pVideos = ""
    if pVideo1 != "None": pVideos += "[Video](" + pVideo1 + ") "
    if pVideo2 != "None": pVideos += "[Video](" + pVideo2 + ") "
    if pVideos != "": pE.add_field(name="Video(s) of Work",value=pVideos,inline=False)
    pE.add_field(name="Servers",value=pServers,inline=False)
    pE.add_field(name="Megacollabs",value=pMCS,inline=False)
    pE.add_field(name="Contact",value=user.name + "#" + str(user.discriminator),inline=False)
    return pE

async def FinishPart(user,mc):
    try: await user.send("Finish Part Bot reminds you to Finish your Part in **" + mc[0] + "**!")
    except discord.errors.Forbidden:
        fpH = GetMemberGlobal(mc[6])
        try: await fpH.send(user.name + " has blocked Finish Part Bot when being reminded to finish their part in " + mc[0] + "!")
        except: pass
    fpimage = random.choice(os.listdir("goodstuff/"))
    with open("goodstuff/" + fpimage,"rb") as fpi:
        fpfile = discord.File(fp=fpi)
        try: await user.send(file=fpfile)
        except: pass
    print("Reminded " + user.name + " to finish for " + mc[0])

async def Update(mcc,mes,tag=False):
    uChannel = datasettings(file="fp-mc/" + mcc[8] + ".txt",method="get",line="CHANNEL-UPDATES")
    if uChannel is None: return None
    uChannel = GetChannel(GetGuild(str(mcc[7].id)),uChannel)
    if uChannel is None: return None
    if not tag: await uChannel.send("[" + DatetimeToStr(datetime.datetime.now()) + "] " + mes)
    else:
        uCreatorRole = datasettings(file="fp-mc/" + mcc[8] + ".txt",method="get",line="ROLE-CREATOR")
        if uCreatorRole is None: await uChannel.send("[" + DatetimeToStr(datetime.datetime.now()) + "] " + mes); return
        uCreatorRole = GetRole(GetGuild(str(mcc[7].id)),uCreatorRole)
        if uCreatorRole is None: await uChannel.send("[" + DatetimeToStr(datetime.datetime.now()) + "] " + mes); return
        await uChannel.send("[" + DatetimeToStr(datetime.datetime.now()) + "] " + mes + "\n" + uCreatorRole.mention)


async def MCCount():
    mccount = 0
    for mcid in alldatakeys("fp-mcdir.txt"): mccount += 1
    datasettings(file="fp-vars.txt", method="change", line="MCS", newvalue=str(mccount))
    if mccount > 0: await client.change_presence(
        activity=discord.Game(name="Hosting " + str(mccount) + " Megacollab(s)"))

def MCHoster(user,method,newlimit=0):
    """
    :param method: get,add,subtract,bypasslimit
    """
    if method == "get": return datasettings(file="fp-hosters.txt",method="get",line=str(user.id))
    if method == "add":
        if datasettings(file="fp-hosters.txt",method="get",line=str(user.id)) is None:
            datasettings(file="fp-hosters.txt",method="add",newkey=str(user.id),newvalue="1")
            return "1"
        else:
            mhlimit = datasettings(file="fp-hosters.txt",method="get",line="BYPASS" + str(user.id))
            if mhlimit is None: return None
            mhcurrent = int(datasettings(file="fp-hosters.txt",method="get",line=str(user.id)))
            mhlimit = int(mhlimit)
            if mhcurrent >= mhlimit: return None
            else:
                datasettings(file="fp-hosters.txt",method="change",line=str(user.id),newvalue=str(int(mhcurrent + 1)))
                return str(int(mhcurrent + 1))
    if method == "subtract":
        if datasettings(file="fp-hosters.txt", method="get", line=str(user.id)) is None: return None
        else:
            mhcurrent = int(datasettings(file="fp-hosters.txt",method="get",line=str(user.id))) - 1
            if mhcurrent < 1: datasettings(file="fp-hosters.txt",method="remove",line=str(user.id)); return "0"
            else:
                datasettings(file="fp-hosters.txt",method="change",line=str(user.id),newvalue=str(mhcurrent))
    if method == "bypasslimit":
        if datasettings(file="fp-hosters.txt",method="get",line="BYPASS" + str(user.id)) is None:
            datasettings(file="fp-hosters.txt",method="add",newkey="BYPASS" + str(user.id),newvalue=str(newlimit))
        else:
            datasettings(file="fp-hosters.txt",method="change",line="BYPASS" + str(user.id),newvalue=str(newlimit))

def MCServer(server,method,newlimit=0):
    """
    :param method: generate,check,bypasslimit
    """
    if method == "generate":
        mS = datasettings(file="fp-servers.txt",method="get",line=str(server.id))
        if mS is None: datasettings(file="fp-servers.txt",method="add",newkey=str(server.id),newvalue="3")
    if method == "check":
        mMCC = 0
        for mcid in alldatakeys(file="fp-mcdir.txt"):
            mMC = datasettings(file="fp-mcdir.txt",method="get",line=mcid); mMC = mMC.split(";")
            mMCServer = client.get_guild(mMC[7])
            if mMCServer is not None:
                if server.id == mMCServer.id: mMCC += 1
        mS = datasettings(file="fp-servers.txt", method="get", line=str(server.id))
        if mS is None: datasettings(file="fp-servers.txt",method="add",newkey=str(server.id),newvalue="3")
        if int(datasettings(file="fp-servers.txt",method="get",line=str(server.id))) <= mMCC: return False
        return True
    if method == "bypasslimit": datasettings(file="fp-servers.txt",method="change",line=str(server.id),newvalue=str(newlimit))

def ActivePR(mcc):
    prnumber = datasettings(file="fp-mc/" + mcc[8] + ".txt",method="get",line="UPDATES")
    if prnumber is None: return None
    prduedate = StrToDatetime(datasettings(file="fp-mc/" + mcc[8] + "/ACTIVITYLOG/UPDATE" + prnumber + ".txt",method="get",line="DUEDATE"))
    if datetime.datetime.now() >= prduedate:
        prfinished = datasettings(file="fp-mc/" + mcc[8] + "/ACTIVITYLOG/UPDATE" + prnumber + ".txt",method="get",line="FINISHED")
        if prfinished is not None: return None
        return [prnumber,False]
    return [prnumber,True]

@client.event
async def on_ready():
    print("Bot Ready!")
    print("Name: " + client.user.name + ", ID: " + str(client.user.id))
    sl = ""
    for server in client.guilds:
        if server is not None: sl += server.name + ", "
        MCServer(server=server,method="generate")
    print("Connected Guilds: " + sl[:len(sl) - 2])
    await MCCount()

@client.event
async def on_guild_join(guild):
    asf = False
    for asi in alldatakeys(file="fp-allowedservers.txt"):
        if asi == str(guild.id): asf = True
    if not asf: await guild.leave()

@client.event
async def on_message(message):
    if message.channel is not None:
        mcc = AutoMCContext(message.channel,message.author)
        if mcc is not None:
            mcpr = ActivePR(mcc)
            if mcpr is not None:
                if not mcpr[1]:
                    mcprf = "**Progress Report " + mcpr[0] + " Results**\n"
                    mcprcreators = []
                    for n in range(1, int(mcc[3]) + 1):
                        mcpartcreators = StrToLODU(datasettings(file="fp-mc/" + mcc[8] + "/PART" + str(n) + ".txt",
                                                                method="get", line="CREATORS"), message.guild)
                        for creator in mcpartcreators:
                            if creator is not None: mcprcreators.append({creator:"*Nothing*"})
                    for udata in alldatakeys("fp-mc/" + mcc[8] + "/ACTIVITYLOG/UPDATE" + mcpr[0] + ".txt"):
                        if udata.startswith("VIDEO"):
                            ucreator = GetMember(udata.replace("VIDEO",""),message.guild)
                            for mcpc in mcprcreators:
                                if list(mcpc.keys())[0] == ucreator:
                                    mcpc[ucreator] = "Video"
                        if udata.startswith("MEDIA"):
                            ucreator = GetMember(udata.replace("MEDIA",""),message.guild)
                            for mcpc in mcprcreators:
                                if list(mcpc.keys())[0] == ucreator:
                                    if mcpc[ucreator] == "Video": mcpc[ucreator] = "Video & Photo(s)"
                                    else: mcpc[ucreator] = "Photo(s)"
                    for mcpc in mcprcreators: mcprf += list(mcpc.keys())[0].name + ": " + mcpc[list(mcpc.keys())[0]] + "\n"
                    await Update(mcc,mcprf)
                    datasettings(file="fp-mc/" + mcc[8] + "/ACTIVITYLOG/UPDATE" + mcpr[0] + ".txt",method="add",
                                             newkey="FINISHED",newvalue="FINISHED")
                else:
                    mcdays = datasettings(file="fp-mc/" + mcc[8] + ".txt", method="get", line="CHECKDAYS")
                    if mcdays is not None:
                        if mcdays != "0":
                            if isnumber(mcdays):
                                mcdays = datetime.timedelta(days=int(mcdays))
                                mcn = datasettings(file="fp-mc/" + mcc[8] + "/ACTIVITYLOG/UPDATE" + mcpr[0] + ".txt", method="get", line="NOTIFIED")
                                if mcn is None: mcn = DatetimeToStr(datetime.datetime.now())
                                mcn = StrToDatetime(mcn)
                                if datetime.datetime.now() >= mcn + mcdays:
                                    datasettings(file="fp-mc/" + mcc[8] + "/ACTIVITYLOG/UPDATE" + mcpr[0] + ".txt", method="change",
                                                 line="NOTIFIED",newvalue=DatetimeToStr(datetime.datetime.now()))
                                    mcfcreators = []
                                    for udata in alldatakeys("fp-mc/" + mcc[8] + "/ACTIVITYLOG/UPDATE" + mcpr[0] + ".txt"):
                                        if udata.startswith("VIDEO"): mcfcreators.append(GetMember(udata.replace("VIDEO",""),message.guild))
                                        if udata.startswith("MEDIA"): mcfcreators.append(GetMember(udata.replace("MEDIA",""),message.guild))
                                    mcnfcreators = []
                                    for n in range(1, int(mcc[3]) + 1):
                                        mcpartcreators = StrToLODU(datasettings(file="fp-mc/" + mcc[8] + "/PART" + str(n) + ".txt",
                                                                                method="get", line="CREATORS"),message.guild)
                                        for creator in mcpartcreators:
                                            if creator is not None:
                                                if creator not in mcfcreators: mcnfcreators.append(creator)
                                    for creator in mcnfcreators: await FinishPart(creator,mcc)
    await client.process_commands(message)

GLOBALPRM = None

@client.command(pass_context=True)
async def host(ctx):
    global MCS
    if AuthorHasPermissions(ctx):
        if ctx.guild:
            if BotHasPermissions(ctx):
                hostServer = await ctx.message.channel.send("Ready to host a new Megacollab?\n"
                                                            "**A** - In this Server\n"
                                                            "**B** - Create a new Server")
                hostServerResponse = await ReactionChoiceMessage(ctx,hostServer,2)
                await hostServer.clear_reactions()
                if hostServerResponse == 1:
                    hostMC_NAME = "None"
                    hostMC_SONG = "None"
                    hostMC_DIFFICULTY = "None"
                    hostMC_OTHERHOSTS = []
                    hostMC_PARTS = 4
                    hostMC_VERIFIER = "None"
                    hostMC1R = await ParameterResponseEmbed(ctx,"Start a Megacollab",[["Name","string",hostMC_NAME,True],
                                                                                      ["Song","string",hostMC_SONG,False],
                                                                                      ["Difficulty","string",hostMC_DIFFICULTY,True],
                                                                                      ["Other Hosts","list of discord users",hostMC_OTHERHOSTS,False],
                                                                                      ["Parts","integer",hostMC_PARTS,False],
                                                                                      ["Verifier","discord user",hostMC_VERIFIER,False]])
                    if not hostMC1R: await ResponseMessage(ctx,"","failed","invalidparams")
                    else:
                        if MCServer(server=ctx.guild,method="check"):
                            hostMC_NAME = hostMC1R[0][2]
                            hostMC_SONG = hostMC1R[1][2]
                            hostMC_DIFFICULTY = hostMC1R[2][2]
                            hostMC_OTHERHOSTS = hostMC1R[3][2]
                            mcohid = []
                            for h in hostMC_OTHERHOSTS: mcohid.append(h.id)
                            mcohn = []
                            for h in hostMC_OTHERHOSTS: mcohid.append(h.name)
                            hostMC_PARTS = hostMC1R[4][2]
                            hostMC_VERIFIER = hostMC1R[5][2]
                            mcv = hostMC_VERIFIER; mcvn = hostMC_VERIFIER
                            try: mcv = mcv.id
                            except: mcv = "None"
                            try: mcvn = mcvn.name
                            except: mcvn = "None"
                            hostMC_ID = str(random.randint(10000,99999))
                            for mcid in alldatakeys("fp-mcdir.txt"):
                                if mcid == hostMC_ID: hostMC_ID = str(random.randint(10000,99999))
                            newfile("fp-mc/" + hostMC_ID + ".txt")
                            os.mkdir("fp-mc/" + hostMC_ID)
                            os.mkdir("fp-mc/" + hostMC_ID + "/ACTIVITYLOG")
                            newfile("fp-mc/" + hostMC_ID + "/ACTIVITYLOG/MAIN.txt")
                            datasettings(file="fp-mc/" + hostMC_ID + "/ACTIVITYLOG/MAIN.txt",method="add",newkey=DatetimeToStr(datetime.datetime.now()),newvalue="MC CREATED")
                            mcw = hostMC_NAME + ";" + hostMC_SONG + ";" + hostMC_DIFFICULTY + ";" + \
                                str(hostMC_PARTS) + ";" + str(mcohid) + ";" + str(mcv) + ";" + \
                                  str(ctx.message.author.id) + ";" + str(ctx.message.guild.id)
                            datasettings(file="fp-mcdir.txt",method="add",newkey=hostMC_ID,newvalue=mcw)
                            datasettings(file="fp-mc/" + hostMC_ID + ".txt",method="add",newkey="NAME",newvalue=hostMC_NAME)
                            datasettings(file="fp-mc/" + hostMC_ID + ".txt",method="add",newkey="SONG",newvalue=hostMC_SONG)
                            datasettings(file="fp-mc/" + hostMC_ID + ".txt",method="add",newkey="DIFFICULTY",newvalue=hostMC_DIFFICULTY)
                            datasettings(file="fp-mc/" + hostMC_ID + ".txt", method="add", newkey="PARTS", newvalue=str(hostMC_PARTS))
                            datasettings(file="fp-mc/" + hostMC_ID + ".txt", method="add", newkey="OTHERHOSTS", newvalue=str(mcohid))
                            datasettings(file="fp-mc/" + hostMC_ID + ".txt", method="add", newkey="VERIFIER",newvalue=str(mcv))
                            datasettings(file="fp-mc/" + hostMC_ID + ".txt", method="add", newkey="OWNER", newvalue=str(ctx.message.author.id))
                            datasettings(file="fp-mc/" + hostMC_ID + ".txt", method="add", newkey="SERVER", newvalue=str(ctx.message.guild.id))
                            hostMC_HOSTROLE = await ctx.message.guild.create_role(name=hostMC_NAME + " Host",color=RandomColor(),mentionable=True,hoist=True)
                            await ctx.author.add_roles(hostMC_HOSTROLE)
                            hostMC_COHOSTROLE = "None"
                            if hostMC_OTHERHOSTS:
                                hostMC_COHOSTROLE = await ctx.message.guild.create_role(name=hostMC_NAME + " Co-Host",color=RandomColor(),mentionable=True,hoist=True)
                                for member in hostMC_OTHERHOSTS: await member.add_roles(hostMC_COHOSTROLE)
                            hostMC_FINISHROLE = await ctx.message.guild.create_role(name="Finished " + hostMC_NAME,color=RandomColor(),mentionable=True,hoist=True)
                            hostMC_CREATORROLE = await ctx.message.guild.create_role(name=hostMC_NAME + " Creator",color=RandomColor(), mentionable=True,hoist=True)
                            hostMC_VERIFIERROLE = await ctx.message.guild.create_role(name=hostMC_NAME + " Verifier",color=RandomColor(),mentionable=True,hoist=True)
                            hostMC_CC = await ctx.message.guild.create_category_channel(name=hostMC_NAME)
                            channelhosto = {
                                ctx.message.guild.default_role: discord.PermissionOverwrite(send_messages=False),
                                hostMC_HOSTROLE: discord.PermissionOverwrite(send_messages=True)
                            }
                            hostMC_PARTSCHANNEL = await ctx.message.guild.create_text_channel(name="parts",category=hostMC_CC,overwrites=channelhosto)
                            hostMC_UPDATESCHANNEL = await ctx.message.guild.create_text_channel(name="updates",category=hostMC_CC,overwrites=channelhosto)
                            channelcreatoro = {
                                ctx.message.guild.default_role: discord.PermissionOverwrite(send_messages=False),
                                hostMC_CREATORROLE: discord.PermissionOverwrite(send_messages=True),
                                hostMC_HOSTROLE: discord.PermissionOverwrite(send_messages=True)
                            }
                            hostMC_PROGRESSCHANNEL = await ctx.message.guild.create_text_channel(name="progress",category=hostMC_CC,overwrites=channelcreatoro)
                            hostMC_FINISHEDPARTSCHANNEL = await ctx.message.guild.create_text_channel(name="finished-parts",category=hostMC_CC,overwrites=channelcreatoro)
                            datasettings(file="fp-mc/" + hostMC_ID + ".txt", method="add", newkey="ROLE-HOST", newvalue=str(hostMC_HOSTROLE.id))
                            if hostMC_OTHERHOSTS:
                                datasettings(file="fp-mc/" + hostMC_ID + ".txt", method="add", newkey="ROLE-COHOST", newvalue=str(hostMC_COHOSTROLE.id))
                            datasettings(file="fp-mc/" + hostMC_ID + ".txt", method="add", newkey="ROLE-CREATOR", newvalue=str(hostMC_CREATORROLE.id))
                            datasettings(file="fp-mc/" + hostMC_ID + ".txt", method="add", newkey="ROLE-VERIFIER", newvalue=str(hostMC_VERIFIERROLE.id))
                            datasettings(file="fp-mc/" + hostMC_ID + ".txt", method="add", newkey="ROLE-FINISHED", newvalue=str(hostMC_FINISHROLE.id))
                            datasettings(file="fp-mc/" + hostMC_ID + ".txt", method="add", newkey="CHANNELCATEGORY", newvalue=str(hostMC_CC.id))
                            datasettings(file="fp-mc/" + hostMC_ID + ".txt", method="add", newkey="CHANNEL-PARTS", newvalue=str(hostMC_PARTSCHANNEL.id))
                            datasettings(file="fp-mc/" + hostMC_ID + ".txt", method="add", newkey="CHANNEL-UPDATES",newvalue=str(hostMC_UPDATESCHANNEL.id))
                            datasettings(file="fp-mc/" + hostMC_ID + ".txt", method="add", newkey="CHANNEL-PROGRESS",newvalue=str(hostMC_PROGRESSCHANNEL.id))
                            datasettings(file="fp-mc/" + hostMC_ID + ".txt", method="add", newkey="CHANNEL-FINISHEDPARTS",newvalue=str(hostMC_FINISHEDPARTSCHANNEL.id))

                            datasettings(file="fp-mc/" + hostMC_ID + ".txt", method="add", newkey="SETTINGS-VISIBILITY", newvalue="True")
                            datasettings(file="fp-mc/" + hostMC_ID + ".txt", method="add", newkey="SETTINGS-INVITING", newvalue="True")
                            datasettings(file="fp-mc/" + hostMC_ID + ".txt", method="add", newkey="SETTINGS-NOTIFY", newvalue="True")
                            await MCCount()
                            await ResponseMessage(ctx,"Megacollab Created! (MC ID: " + hostMC_ID + ")\n**Name**: " + hostMC_NAME + \
                                                  "\n**Song**: " + hostMC_SONG +
                                                  "\n**Difficulty**: " + hostMC_DIFFICULTY +
                                                  "\n**Host**: " + ctx.message.author.name +
                                                  "\n**Verifier**: " + mcvn +
                                                  "\n**Parts**: " + str(hostMC_PARTS) +
                                                  "\n**Roles**: " + hostMC_HOSTROLE.mention + " " + hostMC_CREATORROLE.mention +
                                                  " " + hostMC_VERIFIERROLE.mention + " " + hostMC_FINISHROLE.mention +
                                                  "\n**Channels**: " + hostMC_UPDATESCHANNEL.mention + " " + hostMC_PROGRESSCHANNEL.mention +
                                                  " " + hostMC_PARTSCHANNEL.mention + " " + hostMC_FINISHEDPARTSCHANNEL.mention,
                                                  "success")
                        else:
                            await ResponseMessage(ctx, "This Server has reached the Megacollab limit!", "failed")
                elif hostServerResponse == 2:
                    await ResponseMessage(ctx,"Megacollab Server Creation not supported yet!","failed")
            else:
                await ResponseMessage(ctx,"","failed","botlacksperms")
        else:
            await ResponseMessage(ctx,"You need to be in a Server to perform this!","failed")
    else:
        await ResponseMessage(ctx,"","failed","authorlacksperms")

@client.command(pass_context=True)
async def transferhost(ctx,tuser):
    if ctx.guild:
        if BotHasPermissions(ctx):
            mcc = await MCContext(ctx)
            if mcc is not None:
                if IsHost(ctx,mcc):
                    tuser = GetMemberGlobal(tuser)
                    if tuser is not None:
                        thMessage = await ctx.message.channel.send("**" + ctx.message.author.name +
                                                                   "**, are you sure you want to transfer Host to " + tuser.name +
                                                                   "?\n**A** - Yes\n**B** - No")
                        thR = await ReactionChoiceMessage(ctx,thMessage,2)
                        await thMessage.clear_reactions()
                        if thR == 1:
                            thHostRole = GetRole(ctx.message.guild,datasettings(file="fp-mc/" + mcc[8] + ".txt",method="get",line="ROLE-HOST"))
                            await ctx.author.remove_roles(thHostRole)
                            await tuser.add_roles(thHostRole)
                            await ResponseMessage(ctx,tuser.name + " is now the Host of " + mcc[0] + "!","success")
                    else:
                        await ResponseMessage(ctx,"Invalid User!","failed")

                else:
                    await ResponseMessage(ctx,"","failed","nothost")
            else:
                await ResponseMessage(ctx,"","failed","nomc")
        else:
            await ResponseMessage(ctx,"","failed","botlacksperms")
    else:
        await ResponseMessage(ctx,"You need to be in a Server to perform this!","failed")

@client.command(pass_context=True)
async def disbandmc(ctx):
    if ctx.guild:
        if BotHasPermissions(ctx):
            mcc = await MCContext(ctx)
            if mcc is not None:
                if IsHost(ctx,mcc):
                    dmMessage1 = await ctx.message.channel.send("**" + ctx.message.author.name + \
                                 "**, are you absolutely sure you want to Delete This?\n**A** - Yes\n**B** - No")
                    dmR1 = await ReactionChoiceMessage(ctx,dmMessage1,2)
                    await dmMessage1.clear_reactions()
                    if dmR1 == 1:
                        dmMessage2 = await ctx.message.channel.send("**" + ctx.message.author.name + \
                        "**, are you REALLY sure? Don't do this if Creators have already made Parts, that's low.\n**A** - Yes\n**B** - No")
                        dmR2 = await ReactionChoiceMessage(ctx,dmMessage2,2)
                        await dmMessage2.clear_reactions()
                        if dmR2 == 1:
                            dmHOSTROLE = GetRole(ctx.guild,datasettings(file="fp-mc/" + mcc[8] + ".txt",method="get",line="ROLE-HOST"))
                            if dmHOSTROLE is not None: await dmHOSTROLE.delete()
                            dmCREATORROLE = GetRole(ctx.guild, datasettings(file="fp-mc/" + mcc[8] + ".txt", method="get",
                                                                         line="ROLE-CREATOR"))
                            if dmCREATORROLE is not None: await dmCREATORROLE.delete()
                            dmVERIFIERROLE = GetRole(ctx.guild, datasettings(file="fp-mc/" + mcc[8] + ".txt", method="get",
                                                                         line="ROLE-VERIFIER"))
                            if dmVERIFIERROLE is not None: await dmVERIFIERROLE.delete()
                            dmFINISHEDROLE = GetRole(ctx.guild, datasettings(file="fp-mc/" + mcc[8] + ".txt", method="get",
                                                                         line="ROLE-FINISHED"))
                            if dmFINISHEDROLE is not None: await dmFINISHEDROLE.delete()
                            dmCHANNELPARTS = GetChannel(ctx.guild,datasettings(file="fp-mc/" + mcc[8] + ".txt",method="get",line="CHANNEL-PARTS"))
                            if dmCHANNELPARTS is not None: await dmCHANNELPARTS.delete()
                            dmCHANNELUPDATES = GetChannel(ctx.guild,
                                                        datasettings(file="fp-mc/" + mcc[8] + ".txt", method="get",
                                                                     line="CHANNEL-UPDATES"))
                            if dmCHANNELUPDATES is not None: await dmCHANNELUPDATES.delete()
                            dmCHANNELPROGRESS = GetChannel(ctx.guild,
                                                        datasettings(file="fp-mc/" + mcc[8] + ".txt", method="get",
                                                                     line="CHANNEL-PROGRESS"))
                            if dmCHANNELPROGRESS is not None: await dmCHANNELPROGRESS.delete()
                            dmCHANNELFINISHEDPARTS = GetChannel(ctx.guild,
                                                        datasettings(file="fp-mc/" + mcc[8] + ".txt", method="get",
                                                                     line="CHANNEL-FINISHEDPARTS"))
                            if dmCHANNELFINISHEDPARTS is not None: await dmCHANNELFINISHEDPARTS.delete()
                            datasettings(file="fp-mcdir.txt",method="remove",line=mcc[8])
                            os.remove("fp-mc/" + mcc[8] + ".txt")
                            shutil.rmtree("fp-mc/" + mcc[8])
                            MCHoster(user=ctx.author,method="subtract")
                            await MCCount()
                            await ResponseMessage(ctx,"Megacollab disbanded.","success")
                else:
                    await ResponseMessage(ctx,"","failed","nothost")
            else:
                await ResponseMessage(ctx,"","failed","nomc")
        else:
            await ResponseMessage(ctx,"","failed","botlacksperms")
    else:
        await ResponseMessage(ctx,"You need to be in a Server to perform this!","failed")

@client.command(pass_context=True)
async def finishmc(ctx):
    if ctx.guild:
        if BotHasPermissions(ctx):
            mcc = await MCContext(ctx)
            if mcc is not None:
                if IsHost(ctx,mcc):
                    mcAFN = True
                    for n in range(1, int(mcc[3]) + 1):
                        mcPS = datasettings(file="fp-mc/" + mcc[8] + "/PART" + str(n) + ".txt", method="get",
                                            line="STATUS")
                        if mcPS.lower() != "finished": mcAFN = False
                    if mcAFN:
                        mcV = datasettings(file="fp-mc/" + mcc[8] + ".txt",method="get",line="VERIFIER")
                        mcV = GetMember(mcV,ctx.guild)
                        if mcV is not None:
                            mcFR = datasettings(file="fp-mc/" + mcc[8] + ".txt",method="get",line="ROLE-FINISHED")
                            mcFR = ctx.guild.get_role(mcFR)
                            if mcFR is not None: await mcFR.edit(name="Was in " + mcc[0])
                            mcCR = datasettings(file="fp-mc/" + mcc[8] + ".txt",method="get",line="ROLE-CREATOR")
                            mcCR = ctx.guild.get_role(mcCR)
                            if mcCR is not None: await mcCR.delete()
                            await Update(mcc,"The Host has confirmed the Megacollab is finished. It is now up to **" + mcV.name + "** to Verify!")
                            await mcV.send("**" + mcV.name + "**, you are now up to Verify " + mcc[0] + "!")
                        else:
                            await ResponseMessage(ctx,"You have not chosen a Verifier yet!","failed")
                    else:
                        await ResponseMessage(ctx,"Every Part in " + mcc[0] + " is not Finished!","failed")
                else:
                    await ResponseMessage(ctx,"","failed","nothost")
            else:
                await ResponseMessage(ctx,"","failed","nomc")
        else:
            await ResponseMessage(ctx,"","failed","botlacksperms")
    else:
        await ResponseMessage(ctx,"You need to be in a Server to perform this!","failed")

@client.command(pass_context=True)
async def generateparts(ctx):
    if AuthorHasPermissions(ctx):
        if ctx.guild:
            if BotHasPermissions(ctx):
                mcc = await MCContext(ctx)
                if mcc is not None:
                    gpMessage = await InitGenerateParts(mcc,ctx.message.channel)
                    datasettings(file="fp-mc/" + mcc[8] + ".txt",method="add",newkey="MESSAGEPARTS-" + str(ctx.message.channel.id),newvalue=str(gpMessage.id))
                    await ctx.message.delete()
                else:
                    await ResponseMessage(ctx, "", "failed", "nomc")
            else:
                await ResponseMessage(ctx,"","failed","botlacksperms")
        else:
            await ResponseMessage(ctx,"You need to be in a Server to perform this!","failed")
    else:
        await ResponseMessage(ctx,"","failed","authorlacksperms")


@client.command(pass_context=True)
async def configpart(ctx,partnum):
    if ctx.guild:
        if BotHasPermissions(ctx):
            mcc = await MCContext(ctx)
            if mcc is not None:
                if IsHost(ctx,mcc):
                    partStatus = datasettings(file="fp-mc/" + mcc[8] + "/PART" + str(partnum) + ".txt",method="get",line="STATUS")
                    if partStatus is not None:
                        partCreators = StrToList(LODUToStrName(StrToLODU(datasettings(file="fp-mc/" + mcc[8] + "/PART" + str(partnum) + ".txt",method="get",line="CREATORS"),ctx.guild)))
                        partTime = datasettings(file="fp-mc/" + mcc[8] + "/PART" + str(partnum) + ".txt",method="get",line="TIME")
                        partVideo = datasettings(file="fp-mc/" + mcc[8] + "/PART" + str(partnum) + ".txt",method="get",line="VIDEO")
                        partDesc = datasettings(file="fp-mc/" + mcc[8] + "/PART" + str(partnum) + ".txt",method="get",line="PARTDESC")
                        partColors = datasettings(file="fp-mc/" + mcc[8] + "/PART" + str(partnum) + ".txt",method="get",line="COLORS")
                        partGroups = datasettings(file="fp-mc/" + mcc[8] + "/PART" + str(partnum) + ".txt",method="get",line="GROUPS")
                        partR = await ParameterResponseEmbed(ctx,"Edit Part " + str(partnum),[["Creators","list of discord users",partCreators,False],
                                                                                              ["Time","string",partTime,False],
                                                                                              ["Status","string",partStatus,False],
                                                                                              ["Video","string",partVideo,False],
                                                                                              ["Description","string",partDesc,False],
                                                                                              ["Colors","string",partColors,False],
                                                                                              ["Groups","string",partGroups,False]])
                        if not partR: await ResponseMessage(ctx,"","failed","invalidparams")
                        else:
                            dataCreators = partR[0][2]
                            if "None" not in dataCreators:
                                datasettings(file="fp-mc/" + mcc[8] + "/PART" + str(partnum) + ".txt", method="change", line="CREATORS", newvalue=LODUToStr(dataCreators))
                            datasettings(file="fp-mc/" + mcc[8] + "/PART" + str(partnum) + ".txt", method="change", line="TIME", newvalue=partR[1][2])
                            datasettings(file="fp-mc/" + mcc[8] + "/PART" + str(partnum) + ".txt", method="change", line="STATUS", newvalue=partR[2][2])
                            if partR[2][2].lower() == "finished":
                                dCL = LODUToStrName(dataCreators)
                                await Update(mcc,dCL + "'s Part is now Finished!")
                                dmFINISHEDROLE = ctx.guild.get_role(int(datasettings(file="fp-mc/" + mcc[8] + ".txt", method="get",line="ROLE-FINISHED")))
                                if dmFINISHEDROLE is not None:
                                    for c in dataCreators:
                                        await c.add_roles(dmFINISHEDROLE)
                            datasettings(file="fp-mc/" + mcc[8] + "/PART" + str(partnum) + ".txt", method="change", line="VIDEO", newvalue=partR[3][2])
                            datasettings(file="fp-mc/" + mcc[8] + "/PART" + str(partnum) + ".txt", method="change", line="PARTDESC", newvalue=partR[4][2])
                            datasettings(file="fp-mc/" + mcc[8] + "/PART" + str(partnum) + ".txt", method="change", line="COLORS", newvalue=partR[5][2])
                            datasettings(file="fp-mc/" + mcc[8] + "/PART" + str(partnum) + ".txt", method="change", line="GROUPS", newvalue=partR[6][2])
                            await RefreshParts(mcc)
                            await ResponseMessage(ctx,"Part config Updated.","success")
                            mcAFN = True
                            for n in range(1, int(mcc[3]) + 1):
                                mcPS = datasettings(file="fp-mc/" + mcc[8] + "/PART" + str(n) + ".txt", method="get",
                                                    line="STATUS")
                                if mcPS.lower() != "finished": mcAFN = False
                            if mcAFN: await Update(mcc,"All Parts in " + mcc[0] + " are FINISHED!!!",tag=True)
                    else:
                        await ResponseMessage(ctx, "Either this is an Invalid Part, or you have not generated Parts yet!", "failed")
                else:
                    await ResponseMessage(ctx,"","failed","nothost")
            else:
                await ResponseMessage(ctx,"","failed","nomc")
        else:
            await ResponseMessage(ctx,"","failed","botlacksperms")
    else:
        await ResponseMessage(ctx,"You need to be in a Server to perform this!","failed")



@client.command(pass_context=True)
async def mcsettings(ctx):
    if ctx.guild:
        if BotHasPermissions(ctx):
            mcc = await MCContext(ctx)
            if mcc is not None:
                if IsHost(ctx,mcc):
                    msVisibility = datasettings(file="fp-mc/" + mcc[8] + ".txt", method="get", line="SETTINGS-VISIBILITY")
                    msInviting = datasettings(file="fp-mc/" + mcc[8] + ".txt", method="get", line="SETTINGS-INVITING")
                    msNotify = datasettings(file="fp-mc/" + mcc[8] + ".txt", method="get", line="SETTINGS-NOTIFY")
                    msName = datasettings(file="fp-mc/" + mcc[8] + ".txt", method="get", line="NAME")
                    msOH = StrToList(LODUToStrName(StrToLODU(datasettings(file="fp-mc/" + mcc[8] + ".txt",method="get",line="OTHERHOSTS"),ctx.guild)))
                    msVerifier = datasettings(file="fp-mc/" + mcc[8] + ".txt",method="get",line="VERIFIER")
                    msR = await ParameterResponseEmbed(ctx,"Megacollab Settings for " + mcc[0],[["Channels are Visibile to Everyone","boolean",msVisibility,False],
                                                                                                ["Creators can find this MC if Parts are Open","boolean",msInviting,False],
                                                                                                ["Slacking Creators are notified to Finish Parts","boolean",msNotify,False],
                                                                                                ["Name","string",msName,False],
                                                                                                ["Other Hosts","list of discord users",msOH,False],
                                                                                                ["Verifier","discord user",msVerifier,False]])
                    if not msR: await ResponseMessage(ctx, "", "failed", "invalidparams")
                    else:
                        msVisibility = msR[0][2]
                        datasettings(file="fp-mc/" + mcc[8] + ".txt", method="change", line="SETTINGS-VISIBILITY", newvalue=msVisibility)
                        msChannelParts = GetChannel(ctx.message.guild,datasettings(file="fp-mc/" + mcc[8] + ".txt", method="get", line="CHANNEL-PARTS"))
                        msChannelUpdates = GetChannel(ctx.message.guild,datasettings(file="fp-mc/" + mcc[8] + ".txt", method="get", line="CHANNEL-UPDATES"))
                        msChannelProgress = GetChannel(ctx.message.guild,datasettings(file="fp-mc/" + mcc[8] + ".txt", method="get", line="CHANNEL-PROGRESS"))
                        msChannelFinishedParts = GetChannel(ctx.message.guild,datasettings(file="fp-mc/" + mcc[8] + ".txt", method="get", line="CHANNEL-FINISHEDPARTS"))
                        mso = discord.PermissionOverwrite(read_messages=False)
                        if msVisibility.lower() == "true": mso = discord.PermissionOverwrite(read_messages=True)
                        if msChannelParts is not None: await msChannelParts.set_permissions(ctx.message.guild.default_role, overwrite=mso)
                        if msChannelUpdates is not None: await msChannelUpdates.set_permissions(ctx.message.guild.default_role, overwrite=mso)
                        if msChannelProgress is not None: await msChannelProgress.set_permissions(ctx.message.guild.default_role, overwrite=mso)
                        if msChannelFinishedParts is not None: await msChannelFinishedParts.set_permissions(ctx.message.guild.default_role, overwrite=mso)
                        datasettings(file="fp-mc/" + mcc[8] + ".txt", method="change", line="SETTINGS-INVITING", newvalue=msR[1][2])
                        datasettings(file="fp-mc/" + mcc[8] + ".txt", method="change", line="SETTINGS-NOTIFY", newvalue=msR[2][2])
                        msName = msR[3][2]
                        msOldName = datasettings(file="fp-mc/" + mcc[8] + ".txt", method="get", line="NAME")
                        if msOldName.lower() == msName.lower(): msName = msOldName
                        datasettings(file="fp-mc/" + mcc[8] + ".txt", method="change", line="NAME", newvalue=msName)
                        msCC = ctx.guild.get_channel(datasettings(file="fp-mc/" + mcc[8] + ".txt",method="get",line="CHANNELCATEGORY"))
                        if msCC is not None: await msCC.edit(name=msName)
                        msRoleFinished = ctx.guild.get_role(datasettings(file="fp-mc/" + mcc[8] + ".txt",method="get",line="ROLE-FINISHED"))
                        if msRoleFinished is not None: await msRoleFinished.edit(name="Finished " + msName)
                        msRoleCreator = ctx.guild.get_role(datasettings(file="fp-mc/" + mcc[8] + ".txt",method="get",line="ROLE-CREATOR"))
                        if msRoleCreator is not None: await msRoleCreator.edit(name=msName + " Creator")
                        msRoleVerifier = ctx.guild.get_role(datasettings(file="fp-mc/" + mcc[8] + ".txt",method="get",line="ROLE-VERIFIER"))
                        if msRoleVerifier is not None: await msRoleVerifier.edit(name=msName + " Verifier")
                        msRoleHost = ctx.guild.get_role(datasettings(file="fp-mc/" + mcc[8] + ".txt",method="get",line="ROLE-HOST"))
                        if msRoleHost is not None: await msRoleHost.edit(name=msName + " Host")
                        msRoleCohost = datasettings(file="fp-mc/" + mcc[8] + ".txt",method="get",line="ROLE-COHOST")
                        if msRoleCohost is not None:
                            msRoleCohost = ctx.guild.get_role(msRoleCohost)
                            if msRoleCohost is not None: await msRoleCohost.edit(name=msName + " Co-Host")
                        msOH = msR[4][2]
                        if msOH is not None:
                            if str(msOH) != "[]" and str(msOH) != "['None']":
                                datasettings(file="fp-mc/" + mcc[8] + ".txt", method="change", line="OTHERHOSTS",
                                             newvalue=LODUToStr(msOH))
                                if msRoleCohost is not None:
                                    msRoleCohost = ctx.guild.get_role(msRoleCohost)
                                    if msRoleCohost is not None:
                                        for member in ctx.guild.members:
                                            if msRoleCohost in member.roles: await member.remove_roles(msRoleCohost)
                                    for nh in msOH: await nh.add_roles(msRoleCohost)
                        msVerifier = msR[5][2]
                        if msVerifier is not None:
                            try: msVT = msVerifier.id
                            except: msVerifier = GetMember(msVerifier,ctx.guild)
                            datasettings(file="fp-mc/" + mcc[8] + ".txt", method="change", line="VERIFIER",
                                         newvalue=str(msVerifier.id))
                            msOldVerifier = GetMember(datasettings(file="fp-mc/" + mcc[8] + ".txt", method="get", line="VERIFIER"),ctx.guild)
                            if msOldVerifier.id != msVerifier.id:
                                if msRoleVerifier in msOldVerifier.roles: await msOldVerifier.remove_roles(msRoleVerifier)
                                if msRoleVerifier not in msVerifier.roles: await msVerifier.add_roles(msRoleVerifier)
                        await ResponseMessage(ctx,"MC Settings updated.","success")
                else:
                    await ResponseMessage(ctx,"","failed","nothost")
            else:
                await ResponseMessage(ctx,"","failed","nomc")
        else:
            await ResponseMessage(ctx,"","failed","botlacksperms")
    else:
        await ResponseMessage(ctx,"You need to be in a Server to perform this!","failed")


@client.command(pass_context=True)
async def mcinvitesallow(ctx,iaserver):
    if ctx.guild:
        if BotHasPermissions(ctx):
            mcc = await MCContext(ctx)
            if mcc is not None:
                if IsHost(ctx,mcc):
                    iaInvites = datasettings(file="fp-mc/" + mcc[8] + ".txt",method="get",line="SETTINGS-INVITING")
                    if iaInvites.lower() == "true":
                        iag = GetGuild(iaserver)
                        if iag is not None:
                            tia = datasettings(file="fp-mc/" + mcc[8] + ".txt",method="get",line=str(iag.id))
                            if tia is None:
                                datasettings(file="fp-mc/" + mcc[8] + ".txt",method="add",newkey=str(iag.id),newvalue="ALLOWEDSERVER")
                                await ResponseMessage(ctx, "Server added to Allowed list for Invites!","success")
                            else:
                                await ResponseMessage(ctx, "Server already Allowed!", "failed")
                        else:
                            await ResponseMessage(ctx, "Invalid Server!", "failed")
                    else:
                        await ResponseMessage(ctx,"Open MC Invites are not Allowed! *Type ??mcsettings to change this*","failed")
                else:
                    await ResponseMessage(ctx,"","failed","nothost")
            else:
                await ResponseMessage(ctx,"","failed","nomc")
        else:
            await ResponseMessage(ctx,"","failed","botlacksperms")
    else:
        await ResponseMessage(ctx,"You need to be in a Server to perform this!","failed")

@client.command(pass_context=True)
async def mcinvitesunallow(ctx,iaserver):
    if ctx.guild:
        if BotHasPermissions(ctx):
            mcc = await MCContext(ctx)
            if mcc is not None:
                if IsHost(ctx,mcc):
                    iaInvites = datasettings(file="fp-mc/" + mcc[8] + ".txt",method="get",line="SETTINGS-INVITING")
                    if iaInvites.lower() == "true":
                        iag = GetGuild(iaserver)
                        if iag is not None:
                            tia = datasettings(file="fp-mc/" + mcc[8] + ".txt",method="get",line=str(iag.id))
                            if tia is not None:
                                datasettings(file="fp-mc/" + mcc[8] + ".txt",method="remove",line=str(iag.id))
                                await ResponseMessage(ctx, "Server remvoved from Allowed list for Invites!","success")
                            else:
                                await ResponseMessage(ctx, "Server not already ALlowed!", "failed")
                        else:
                            await ResponseMessage(ctx, "Invalid Server!", "failed")
                    else:
                        await ResponseMessage(ctx,"Open MC Invites are not Allowed! *Type ??mcsettings to change this*","failed")
                else:
                    await ResponseMessage(ctx,"","failed","nothost")
            else:
                await ResponseMessage(ctx,"","failed","nomc")
        else:
            await ResponseMessage(ctx,"","failed","botlacksperms")
    else:
        await ResponseMessage(ctx,"You need to be in a Server to perform this!","failed")

BIOLIMIT = 140

@client.command(pass_context=True)
async def editportfolio(ctx):
    global BIOLIMIT
    if datasettings(file="fp-portfolio/" + str(ctx.message.author.id) + ".txt",method="get",line="BIO") is None:
        newfile("fp-portfolio/" + str(ctx.message.author.id) + ".txt")
        datasettings(file="fp-portfolio/" + str(ctx.message.author.id) + ".txt", method="add", newkey="BIO", newvalue="None")
        datasettings(file="fp-portfolio/" + str(ctx.message.author.id) + ".txt", method="add", newkey="VIDEO1", newvalue="None")
        datasettings(file="fp-portfolio/" + str(ctx.message.author.id) + ".txt", method="add", newkey="VIDEO2", newvalue="None")
    pfBio = datasettings(file="fp-portfolio/" + str(ctx.message.author.id) + ".txt", method="get", line="BIO")
    pfVideo1 = datasettings(file="fp-portfolio/" + str(ctx.message.author.id) + ".txt", method="get", line="VIDEO1")
    pfVideo2 = datasettings(file="fp-portfolio/" + str(ctx.message.author.id) + ".txt", method="get", line="VIDEO2")
    pfR = await ParameterResponseEmbed(ctx,ctx.message.author.name + "'s Portfolio",[["Short Bio","string",pfBio,False],
                                                                                     ["Video #1","string",pfVideo1,False],
                                                                                     ["Video #2","string",pfVideo2,False]])
    if pfR is None: await ResponseMessage(ctx, "", "failed", "invalidparams")
    else:
        pfD = True
        try: pfBio = pfR[0][2]
        except: pfD = False
        if pfD:
            if len(pfBio) > BIOLIMIT:
                await ResponseMessage(ctx,"Your \"Short Bio\" is not short at all! Keep your Bio short and concise, under "
                                      + str(BIOLIMIT) + " characters, for the MC Hosts' sakes.","failed")
            else:
                datasettings(file="fp-portfolio/" + str(ctx.message.author.id) + ".txt",method="change",line="BIO",newvalue=pfBio)
                datasettings(file="fp-portfolio/" + str(ctx.message.author.id) + ".txt",method="change",line="VIDEO1",newvalue=pfR[1][2])
                datasettings(file="fp-portfolio/" + str(ctx.message.author.id) + ".txt",method="change",line="VIDEO2",newvalue=pfR[2][2])
                await ResponseMessage(ctx,"Portfolio updated!","success")
                await ctx.message.channel.send(embed=Portfolio(ctx.message.author))

@client.command(pass_context=True)
async def myportfolio(ctx):
    if datasettings(file="fp-portfolio/" + str(ctx.message.author.id) + ".txt", method="get", line="BIO") is None:
        await ResponseMessage(ctx, "You have not made a Portfolio! *Type ??editportfolio*", "failed")
    else: await ctx.message.channel.send(embed=Portfolio(ctx.message.author))

@client.command(pass_context=True)
async def findportfolio(ctx,puser):
    puser = GetMemberGlobal(puser)
    if puser is not None:
        if datasettings(file="fp-portfolio/" + str(puser.id) + ".txt", method="get", line="BIO") is None:
            await ResponseMessage(ctx, "This User has not made a Portfolio!", "failed")
        else: await ctx.message.channel.send(embed=Portfolio(puser))
    else: await ResponseMessage(ctx,"Invalid User!","failed")

@client.command(pass_context=True)
async def openmcs(ctx):
    if BotHasPermissions(ctx):
        if datasettings(file="fp-portfolio/" + str(ctx.message.author.id) + ".txt", method="get", line="BIO") is not None:
            omc = []
            for mcid in alldatakeys("fp-mcdir.txt"):
                mcd = datasettings(file="fp-mcdir.txt",method="get",line=mcid); mcd = mcd.split(";")
                mcInviting = datasettings(file="fp-mc/" + mcid + ".txt",method="get",line="SETTINGS-INVITING")
                if mcInviting.lower() == "false": continue
                mcsRequired = []
                for mcsdata in alldatakeys("fp-mc/" + mcid + ".txt"):
                    if datasettings(file="fp-mc/" + mcid + ".txt",method="get",line=mcsdata) == "ALLOWEDSERVER":
                        mcsServer = GetGuild(mcsdata)
                        if mcsServer is None: continue
                        else: mcsRequired.append(mcsServer)
                mcSRM = False
                if len(mcsRequired) == 0: mcSRM = True
                else:
                    for mcs in mcsRequired:
                        for member in mcs.members:
                            if str(member.id) == str(ctx.message.author.id): mcSRM = True; break
                if mcSRM:
                    mcd.append(mcid)
                    mcpo = 0
                    for n in range(1, int(mcd[3]) + 1):
                        mcpStatus = datasettings(file="fp-mc/" + mcid + "/PART" + str(n) + ".txt",method="get",line="STATUS")
                        if mcpStatus is None: mcpStatus = "empty"
                        if mcpStatus.lower() == "empty": mcpo += 1
                    if mcpo > 0:
                        mcd.append(mcpo)
                        omc.append(mcd)
            if len(omc) > 0:
                if len(omc) > 5:
                    nomc = []
                    for m in range(1,6):
                        while True:
                            smc = omc[random.randint(0,len(omc) - 1)]
                            if smc not in nomc: nomc.append(smc); break
                    omc = nomc
                omm = "Here are some MC(s) with open Parts! Which sounds interesting?\n"
                omll = "A"; omln = 1; omlm = ""; omlk = {1:"A",2:"B",3:"C",4:"D",5:"E",6:"F"}
                for mc in omc:
                    omlm += "**" + omll + "** - " + mc[0] + " by " + GetMemberGlobal(mc[6]).name + " [" + str(mc[9]) + " parts open]\n"
                    omln += 1
                    omll = omlk[omln]
                omMessage = await ctx.message.channel.send(omm + omlm)
                omRR = await ReactionChoiceMessage(ctx,omMessage,len(omc))
                await omMessage.clear_reactions()
                if omRR != 0 and omRR != 7:
                    omCMC = []
                    if len(omc) == 1 and omRR == 6: omCMC = omc[0]
                    else: omCMC = omc[omRR - 1]
                    omHostNote = await ParameterResponseEmbed(ctx,"Send a Message to the Host with your request to join "
                                                              + omCMC[0] + "?",[["Optional Message","string","No Message Set",False]])
                    if omHostNote is None: ResponseMessage(ctx,"","failed","invalidparams")
                    else:
                        omHost = GetMemberGlobal(mc[6])
                        omHostMessage = "**" + omHost.name + "**, " + ctx.message.author.name + \
                                        " would like to join your Megacollab *" + omCMC[0] + "*!\n"
                        omHostNR = omHostNote[0][2]
                        if omHostNR != "No Message Set": omHostMessage += "Message from " + ctx.message.author.name + ": " \
                                                                          + omHostNR + "\n"
                        await omHost.send(omHostMessage)
                        await omHost.send(embed=Portfolio(ctx.message.author))
                        await ResponseMessage(ctx,"Request to Join sent!","success")
            else:
                await ResponseMessage(ctx, "", "failed", "botlacksperms")
        else:
            await ResponseMessage(ctx,"There are no Open MCs for you right now! :(","failed")
    else:
        await ResponseMessage(ctx,"You need to create a Portfolio first! *Type ??editportfolio*","failed")


@client.command(pass_context=True)
async def mypart(ctx):
    if ctx.guild:
        mcc = await MCContext(ctx)
        if mcc is not None:
            for n in range(1, int(mcc[3]) + 1):
                mpCreators = StrToLODU(datasettings(file="fp-mc/" + mcc[8] + "/PART" + str(n) + ".txt",method="get",line="CREATORS"),ctx.guild)
                if ctx.author in mpCreators:
                    await GetPart(ctx,mcc,str(n))
        else:
            await ResponseMessage(ctx, "", "failed", "nomc")
    else:
        await ResponseMessage(ctx,"You need to be in a Server to perform this!","failed")


@client.command(pass_context=True)
async def absolveactivity(ctx):
    if ctx.guild:
        if BotHasPermissions(ctx):
            mcc = await MCContext(ctx)
            if mcc is not None:
                if IsHost(ctx,mcc):
                    for user in ctx.guild.members:
                        if latestdata("fp-mc/" + mcc[8] + "/ACTIVITYLOG/" + str(user.id) + ".txt") is None:
                            newfile("fp-mc/" + mcc[8] + "/ACTIVITYLOG/" + str(user.id) + ".txt")
                            datasettings(file="fp-mc/" + mcc[8] + "/ACTIVITYLOG/" + str(user.id) + ".txt", method="add",
                                         newkey=DatetimeToStr(datetime.datetime.now()), newvalue=str(user.id))
                    await ResponseMessage(ctx,"All Members absolved of activity","success")
                else:
                    await ResponseMessage(ctx,"","failed","nothost")
            else:
                await ResponseMessage(ctx,"","failed","nomc")
        else:
            await ResponseMessage(ctx,"","failed","botlacksperms")
    else:
        await ResponseMessage(ctx,"You need to be in a Server to perform this!","failed")


@client.command(pass_context=True)
async def checkevery(ctx,cdays):
    if ctx.guild:
        if BotHasPermissions(ctx):
            mcc = await MCContext(ctx)
            if mcc is not None:
                if IsHost(ctx,mcc):
                    if isnumber(cdays):
                        cedays = datasettings(file="fp-mc/" + mcc[8] + ".txt",method="get",line="CHECKDAYS")
                        if cedays is None:
                            datasettings(file="fp-mc/" + mcc[8] + ".txt",method="add",newkey="CHECKDAYS",newvalue=str(cdays))
                            await ResponseMessage(ctx,"Part Reminder intervals set to every **" + str(cdays) + "** days!","success")
                        else:
                            datasettings(file="fp-mc/" + mcc[8] + ".txt",method="change",line="CHECKDAYS",newvalue=str(cdays))
                            await ResponseMessage(ctx,
                                                  "Part Reminder intervals changed to every **" + str(cdays) + "** days!","success")
                    else:
                        await ResponseMessage(ctx,"","failed","invalidparams")
                else:
                    await ResponseMessage(ctx,"","failed","nothost")
            else:
                await ResponseMessage(ctx,"","failed","nomc")
        else:
            await ResponseMessage(ctx,"","failed","botlacksperms")
    else:
        await ResponseMessage(ctx,"You need to be in a Server to perform this!","failed")

@client.command(pass_context=True)
async def progressupdate(ctx):
    if ctx.guild:
        if BotHasPermissions(ctx):
            mcc = await MCContext(ctx)
            if mcc is not None:
                if IsHost(ctx,mcc):
                    punumber = datasettings(file="fp-mc/" + mcc[8] + ".txt",method="get",line="UPDATES")
                    if punumber is None: punumber = "1"
                    else: punumber = int(punumber) + 1; punumber = str(punumber)
                    puDAYS = 5
                    puDESCRIPTION = "Finish Gameplay, show Decoration progress, etc"
                    puVIDREQUIRED = False
                    puPHOTOSREQUIRED = True
                    puR = await ParameterResponseEmbed(ctx,"Progress Update " + punumber,parameters=[["Check In (Days)","integer",puDAYS,False],
                                                                                                     ["Description of Progress Needed","string",puDESCRIPTION,True],
                                                                                                     ["Video Required","boolean",puVIDREQUIRED,False],
                                                                                                     ["Photos Required","boolean",puPHOTOSREQUIRED,False]])
                    if not puR: await ResponseMessage(ctx, "", "failed", "invalidparams")
                    else:
                        puDAYS = int(puR[0][2])
                        puDESCRIPTION = puR[1][2]
                        puVIDREQUIRED = puR[2][2]
                        puPHOTOSREQUIRED = puR[3][2]
                        if not puVIDREQUIRED and not puPHOTOSREQUIRED:
                            await ResponseMessage(ctx,"You need to require either Video or Photos for a Progress Report!","failed")
                        else:
                            if puDAYS < 1:
                                await ResponseMessage(ctx,"Invalid days!","failed")
                            else:
                                newfile("fp-mc/" + mcc[8] + "/ACTIVITYLOG/UPDATE" + punumber + ".txt")
                                if datasettings(file="fp-mc/" + mcc[8] + ".txt",method="get",line="UPDATES") is None:
                                    datasettings(file="fp-mc/" + mcc[8] + ".txt",method="add",newkey="UPDATES",newvalue="1")
                                else:
                                    datasettings(file="fp-mc/" + mcc[8] + ".txt", method="change", line="UPDATES",newvalue=str(punumber))
                                datasettings(file="fp-mc/" + mcc[8] + "/ACTIVITYLOG/UPDATE" + punumber + ".txt",method="add",newkey="DESCRIPTION",newvalue=puDESCRIPTION)
                                puDUEDATE = datetime.datetime.now() + datetime.timedelta(days=puDAYS)
                                datasettings(file="fp-mc/" + mcc[8] + "/ACTIVITYLOG/UPDATE" + punumber + ".txt",method="add",newkey="DUEDATE",newvalue=DatetimeToStr(puDUEDATE))
                                datasettings(file="fp-mc/" + mcc[8] + "/ACTIVITYLOG/UPDATE" + punumber + ".txt",method="add",newkey="VIDREQUIRED",newvalue=str(puVIDREQUIRED))
                                datasettings(file="fp-mc/" + mcc[8] + "/ACTIVITYLOG/UPDATE" + punumber + ".txt",method="add",newkey="PHOTOSREQUIRED",newvalue=str(puPHOTOSREQUIRED))
                                await ResponseMessage(ctx,"Progress Update " + punumber + " created!","success")
                                await Update(mcc,"**Progress Update " + punumber + "**\n" \
                                                "Progress Description: " + puDESCRIPTION + "\n" \
                                                "Videos Required: " + str(puVIDREQUIRED) + "\n" \
                                                "Photos Required: " + str(puPHOTOSREQUIRED) + "\n" \
                                                "**Due Date:** " + DatetimeToStr(puDUEDATE) + "\n" \
                                                "*Use ??sendprogress to send progress*",tag=True)
                else:
                    await ResponseMessage(ctx,"","failed","nothost")
            else:
                await ResponseMessage(ctx,"","failed","nomc")
        else:
            await ResponseMessage(ctx,"","failed","botlacksperms")
    else:
        await ResponseMessage(ctx,"You need to be in a Server to perform this!","failed")

@client.command(pass_context=True)
async def sendprogress(ctx):
    if ctx.guild:
        mcc = await MCContext(ctx)
        if mcc is not None:
            spnumber = datasettings(file="fp-mc/" + mcc[8] + ".txt", method="get", line="UPDATES")
            spVIDREQUIRED = datasettings(file="fp-mc/" + mcc[8] + "/ACTIVITYLOG/UPDATE" + spnumber + ".txt",method="get",line="VIDREQUIRED")
            spPHOTOSREQUIRED = datasettings(file="fp-mc/" + mcc[8] + "/ACTIVITYLOG/UPDATE" + spnumber + ".txt",method="get", line="PHOTOSREQUIRED")
            spVIDEO = "None"
            spMEDIA = "None"
            spparams = []
            if spVIDREQUIRED.lower() == "true":
                spparams.append(["Video of Progress","string",spVIDEO,True]); spVIDREQUIRED = True
            else: spVIDREQUIRED = False
            if spPHOTOSREQUIRED.lower() == "true":
                spparams.append(["Photo(s) of Progress","media",spMEDIA,True]); spPHOTOSREQUIRED = True
            else: spPHOTOSREQUIRED = False
            if spparams:
                spR = await ParameterResponseEmbed(ctx,title="Submit Progress for Update " + spnumber,parameters=spparams)
                if not spR: await ResponseMessage(ctx, "", "failed", "invalidparams")
                else:
                    if spVIDREQUIRED and spPHOTOSREQUIRED:
                        spVIDEO = spR[0][2]; spMEDIA = spR[1][2]
                        datasettings(file="fp-mc/" + mcc[8] + "/ACTIVITYLOG/UPDATE" + spnumber + ".txt",method="add",
                                     newkey="VIDEO" + str(ctx.author.id),newvalue=spVIDEO)
                        datasettings(file="fp-mc/" + mcc[8] + "/ACTIVITYLOG/UPDATE" + spnumber + ".txt", method="add",
                                     newkey="MEDIA" + str(ctx.author.id), newvalue=str(spMEDIA))
                    elif spVIDREQUIRED and not spPHOTOSREQUIRED:
                        spVIDEO = spR[0][2]
                        datasettings(file="fp-mc/" + mcc[8] + "/ACTIVITYLOG/UPDATE" + spnumber + ".txt", method="add",
                                     newkey="VIDEO" + str(ctx.author.id), newvalue=spVIDEO)
                    elif not spVIDREQUIRED and spPHOTOSREQUIRED:
                        spMEDIA = spR[0][2]
                        datasettings(file="fp-mc/" + mcc[8] + "/ACTIVITYLOG/UPDATE" + spnumber + ".txt", method="add",
                                     newkey="MEDIA" + str(ctx.author.id), newvalue=str(spMEDIA))
                    await ResponseMessage(ctx,"Progress Sent!","success")
                    await mcc[6].send(mcc[6].name + ", *" + ctx.author.name + "* has submitted progress for Progress Check "
                                      + spnumber + " for **" + mcc[0] + "**!")
        else:
            await ResponseMessage(ctx, "", "failed", "nomc")
    else:
        await ResponseMessage(ctx, "You need to be in a Server to perform this!", "failed")

@client.command(pass_context=True)
async def getprogress(ctx,puser):
    if ctx.guild:
        if BotHasPermissions(ctx):
            mcc = await MCContext(ctx)
            if mcc is not None:
                if IsHost(ctx, mcc):
                    gpuser = GetMember(puser,ctx.guild)
                    if gpuser is not None:
                        gpprogress = ActivePR(mcc)
                        if gpprogress is not None:
                            if gpprogress[1]:
                                gpuserprogress = []
                                for udata in alldatakeys("fp-mc/" + mcc[8] + "/ACTIVITYLOG/UPDATE" + gpprogress[0] + ".txt"):
                                    if udata.startswith("VIDEO"):
                                        ucreator = GetMember(udata.replace("VIDEO",""),ctx.guild)
                                        if ucreator == gpuser: gpuserprogress.append(["video",
                                            datasettings(file="fp-mc/" + mcc[8] + "/ACTIVITYLOG/UPDATE" + gpprogress[0] + ".txt",method="get",line=udata)])
                                    if udata.startswith("MEDIA"):
                                        ucreator = GetMember(udata.replace("MEDIA",""),ctx.guild)
                                        if ucreator == gpuser: gpuserprogress.append(["media",
                                            StrToList(datasettings(file="fp-mc/" + mcc[8] + "/ACTIVITYLOG/UPDATE" + gpprogress[0] + ".txt",method="get",line=udata))])
                                if len(gpuserprogress) == 0:
                                    await ResponseMessage(ctx, "*" + gpuser.name + "* has not submitted progress for **"
                                                          + mcc[0] + "**'s Progress Report " + gpprogress[0] + "!","success")
                                else:
                                    gpm = "*" + gpuser.name + "*'s progress for **" + mcc[0] + "**'s Progress Report " + gpprogress[0] + ":\n"
                                    for gpd in gpuserprogress:
                                        if gpd[0] == "video": gpm += gpd[1] + "\n"
                                    await ResponseMessage(ctx,gpm,"success")
                                    for gpd in gpuserprogress:
                                        if gpd[0] == "media":
                                            for m in gpd[1]: await datamedia(method="send",message=ctx.message,filename=m)
                            else:
                                await ResponseMessage(ctx, "There are no active Progress Reports right now!", "failed")
                        else:
                            await ResponseMessage(ctx,"There are no active Progress Reports right now!","failed")
                    else:
                        await ResponseMessage(ctx, "", "failed", "invalidparams")
                else:
                    await ResponseMessage(ctx,"","failed","nothost")
            else:
                await ResponseMessage(ctx,"","failed","nomc")
        else:
            await ResponseMessage(ctx,"","failed","botlacksperms")
    else:
        await ResponseMessage(ctx,"You need to be in a Server to perform this!","failed")

@client.command(pass_context=True)
async def finishpart(ctx):
    mcc = await MCContext(ctx)
    if mcc is not None: await FinishPart(ctx.author,mcc)


@client.command(pass_context=True)
async def help(ctx):
    hm = "**Finish Part Bot** by GunnerBones#2102\n\n" \
         "**??host** - [Administrator]\n" \
         "Hosts a new Megacollab\n" \
         "**??generateparts** - [Host]\n" \
         "Generates the Parts list. Use this command in #parts of the Megacollab\n" \
         "**??mcsettings** - [Host]\n" \
         "Edits settings of the Megacollab\n" \
         "**??configpart** <Part Position> - [Host]\n" \
         "Edits Part information, like Creators, Status, etc\n" \
         "**??mypart** - [MC Creators]\n" \
         "Shows information about your part\n" \
         "**??mcinvitesallow** <Server Name> - [Host]\n" \
         "If Server Invites are on, users who type ??openmcs will be able to join this Megacollab\n" \
         "**??mcinvitesunallow** <Server Name> - [Host]\n" \
         "Removes a Server from the Server Invites list\n" \
         "**??openmcs** - [Anyone]\n" \
         "Lists available Megacollabs to join\n" \
         "**??checkevery** <Days> - [Host]\n" \
         "Sets the days interval in which the bot will remind unfinished creators to Finish Part\n" \
         "**??transferhost** <User> - [Host]\n" \
         "Transfers Host ownership to someone else\n" \
         "**??disbandmc** - [Host]\n" \
         "Disbands the Megacollab\n" \
         "**??finishmc** - [Host]\n" \
         "When all Parts are finished, this will complete the Megacollab\n" \
         "**??checkevery** <Days> - [Host]\n" \
         "If a Progress Update is active, the Bot will notify all people who haven't made progress every x days\n" \
         "**??progressupdate** - [Host]\n" \
         "Creates a Progress Update for creators to meet a deadline of a certain requirement (deco, gameplay, etc)\n" \
         "**??sendprogress** - [MC Creators]\n" \
         "Sends progress for a Progress Update\n" \
         "**??getprogress** <User> - [Host]\n" \
         "Checks progress from a Creator\n" \
         "**??myportfolio** - [Anyone]\n" \
         "Shows your Portfolio that will be used for Hosts considering Creators\n" \
         "**??editportfolio** - [Anyone]\n" \
         "Edits your Portfolio\n" \
         "**??findportfolio** <User> - [Anyone]\n" \
         "Finds a User's Portfolio"
    await ResponseMessage(ctx,hm,"success")



# GB Only Commands

@client.command(pass_context=True)
async def mcuserlimitbypass(ctx,buser,bypassnum):
    if str(ctx.author.id) == "172861416364179456":
        buser = GetMember(buser,ctx.guild)
        if buser is not None:
            bnv = True
            try: bypassnum = int(bypassnum)
            except: bnv = False
            if bnv:
                MCHoster(user=buser,method="bypasslimit",newlimit=bypassnum)
                await ResponseMessage(ctx,buser.name + " can now host up to " + str(bypassnum) + " Megacollab(s)","success")

@client.command(pass_context=True)
async def mcserverlimitbypass(ctx,bserver,bypassnum):
    if str(ctx.author.id) == "172861416364179456":
        bserver = GetGuild(bserver)
        if bserver is not None:
            bnv = True
            try: bypassnum = int(bypassnum)
            except: bnv = False
            if bnv:
                MCServer(server=bserver,method="bypasslimit",newlimit=bypassnum)
                await ResponseMessage(ctx,bserver.name + " can now hold up to " + str(bypassnum) + " Megacollab(s)","success")

@client.command(pass_context=True)
async def bypasses(ctx):
    if str(ctx.author.id) == "172861416364179456":
        bm = "**Users**\n"
        for bu in alldatakeys(file="fp-hosters.txt"):
            bui = ""
            if bu.startswith("BYPASS"): bui = "BYPASS " + GetMemberGlobal(bu).name
            else: bui = GetMemberGlobal(bu).name
            bun = datasettings(file="fp-hosters.txt",method="get",line=bu)
            bm += bui + ": " + bun + "\n"
        bm += "**Servers**\n"
        for bs in alldatakeys(file="fp-servers.txt"):
            bsi = GetGuild(bs).name
            bsn = datasettings(file="fp-servers.txt",method="get",line=bs)
            bm += bsi + ": " + bsn + "\n"
        await ctx.message.add_reaction(CHAR_SUCCESS)
        await ctx.author.send(bm)

@client.command(pass_context=True)
async def toggleserverallow(ctx,tserver):
    if str(ctx.author.id) == "172861416364179456":
        if isnumber(tserver):
            ts = datasettings(file="fp-allowedservers.txt",method="get",line=tserver)
            if ts is None:
                datasettings(file="fp-allowedservers.txt",method="add",newkey=tserver,newvalue="ALLOWED")
                await ctx.message.add_reaction(CHAR_SUCCESS)
                await ctx.author.send(tserver + " added to Allowed Servers")
            else:
                datasettings(file="fp-allowedservers.txt",method="remove",line=tserver)
                await ctx.message.add_reaction(CHAR_SUCCESS)
                await ctx.author.send(tserver + " removed from Allowed Servers")

@client.command(pass_context=True)
async def ctest(ctx):
    if ctx.author.id == 172861416364179456:
        await SimMCContext(sguild=GetGuild("561985959957233664"),
                           smember=GetMember("235047481451216906",
                                             GetGuild("561985959957233664")),schannel=ctx.message.channel)
@client.command(pass_context=True)
async def ctest2(ctx):
    if str(ctx.author.id) == "172861416364179456":
        dm = await datamedia(method="save",message=ctx.message)
        print(dm)
        await datamedia(method="send",message=ctx.message,filename=dm[0])


client.run(SECRET)