import discord, asyncio, sys, os, urllib.request, json, math, random, ast, datetime, base64, time, copy, pickle, traceback
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

EMOJI_EMPTY = "<:empty:560341877212315658>"
EMOJI_ASSIGNED = "<:assigned:560341866445537300>"
EMOJI_PROGRESS = "<:progress:560341884992487425>"
EMOJI_FINISHED = "<:finished:560341892881973248>"
statusEmoji = {"empty":EMOJI_EMPTY,"assigned":EMOJI_ASSIGNED,"progress":EMOJI_PROGRESS,"finished":EMOJI_FINISHED}

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
    return ld[len(ld) - 1]

def cleardata(file):
    s = None
    try: s = open(file,"w")
    except: return
    s.truncate(); s.close()

def newfile(file):
    f = open(file,"a")
    f.close()

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

MCS = []

class Megacollab(object):
    def __init__(self,mcid,name="None",song="None",difficulty="None",parts=4,cohosts=None,verifier=None,host=None,server=None):
        (filename, line_number, function_name, text) = traceback.extract_stack()[-2]
        def_name = text[:text.find('=')].strip()
        self.fname = def_name
        self.mcid = mcid

        try: self.load()
        except:
            self.name = name
            self.song = song
            self.difficulty = difficulty
            self.parts = int(parts)
            self.cohosts = cohosts
            self.verifier = GetMemberGlobal(verifier)
            self.host = GetMemberGlobal(host)
            self.server = GetGuild(server)

            self.creators = []
            self.partlist = []
            self.globalpartlist = []
            for p in range(1,self.parts + 1):
                self.partlist.append(Part(mc=self,position=p,ptype=None,ptime=None,creators=[],pgroups=None,pcolors=None,mcid=self.mcid))
            self.save()
    def save(self):
        f = open("fp-mc/" + self.mcid + "/" + self.fname + ".txt","w+")
        f.write(pickle.dumps(self.__dict__))
        f.close()
    def load(self):
        f = open("fp-mc/" + self.mcid + "/" + self.fname + ".txt","r")
        dataPickle = f.read()
        f.close()
        self.__dict__ = pickle.loads(dataPickle)
    def assignparts(self,ptype,custom=None,creators=None,globalcreators=None):
        """
        PART TYPES
        x = self.parts (number of parts)
        *****For demonstration, let's make x = 7. Replace 7 and multiples of 7 with x.*****

        A SLOT is a space a user can take to either Layout [L], Decorate [D], or Create (both) [C]. A PART is a section
        of the level that fulfills the Layout and Decoration requirements for that range. A PART can have different
        combinations of SLOTS (one slot user creates the entire part, 2 slots where 1 decorates and 1 layouts, etc)
        To avoid confusion, the difference between a CREATOR [C] slot and a LAYOUT and DECORATOR [LD] slot pair is
        a Creator is a single user decorating/layouting a part while a LD pair is 2 separate users where one does Layout
        and one does Decoration.

        -7L7D: 7 Parts, 14 user slots. Each part consists of a Layout slot and a Decoration slot by separate users.
        -7C: 7 Parts, 7 user slots. Each part is Created by a slot user.
        -1L7D: 7 parts, 8 user slots. The Layout for the entire level is made by a single slot user while each part
        only has 1 slot for decorating.
        -CUSTOM: Custom combination of L, D, and C.

        INDIVIDUAL PART SLOT TYPES (used for making CUSTOM part combinations)
        -C: 1 Creator slot
        -LD: 1 Layout and 1 Decorator slot
        -LDD: 1 Layout and 2 Decorator slots (this does happen sometimes where 2 decorators decorate one part)
        -D: 1 Decorator slot (if a Layout was made for the entire level)
        -L: 1 Layout slot where layout is used for entire level
        -A: 1 Art slot

        *****Again, part types are not limited to 7, I used x = 7 in the notes above for demonstration of how it
        would look, as x is displayed as your megacollab's part number when viewing part types.*****
        """
        # creators & globalcreators: [[user1,user2],[user1,user2]...]

        # Assigning Slots
        if ptype != "CUSTOM":
            if ptype == "1LXD":
                globalpart = GlobalPart(mc=self,mcid=self.mcid)
                globalpartslot = Slot(mc=self,part=globalpart,stype="L",sid=1,creator=globalcreators[0],mcid=self.mcid)
                globalpart.slot = globalpartslot
                self.globalpartlist.append(globalpart)
            for part in self.partlist: part.generateslots_normal(ptype=ptype,creators=creators[part.position - 1])
        elif ptype == "CUSTOM":
            for part in self.partlist: part.generateslots_custom(custom=custom)

        # Assigning Colors
        apin = True
        for part in self.partlist:
            if apin: part.pcolors = "1-100"; apin = False
            if not apin: part.pcolors = "101-200"; apin = True

        # Assigning Groups
        if self.parts < 20:
            # Group sets: 50 - 100 - 150 - 200
            apd = int(999.0 / float(self.parts)); apc = 0
            if apd <= 50: apc = 50
            elif 100 >= apd >= 50:
                if 100 - apd > 50 - apd: apc = 100
                else: apc = 50
            elif 150 >= apd >= 100:
                if 150 - apd > 100 - apd: apc = 150
                else: apc = 100
            elif 200 >= apd >= 150:
                if 200 - apd > 150 - apd: apc = 200
                else: apc = 150
            apn = 0
            for part in self.partlist:
                if part.position == 1: part.pgroups = "3-" + str(apc); apn += apc
                else: part.pgroups = str(int(apn + 1)) + "-" + str(apc); apn += apc

class GlobalPart(object):
    def __init__(self,mc,mcid,slot=None,pgroups=None,pcolors=None,status=None,video=None):
        (filename, line_number, function_name, text) = traceback.extract_stack()[-2]
        def_name = text[:text.find('=')].strip()
        self.fname = def_name
        self.mcid = mcid

        try: self.load()
        except:
            self.mc = mc
            self.slot = slot
            self.pgroups = pgroups
            self.pcolors = pcolors
            self.status = status
            self.video = video
    def save(self):
        f = open("fp-mc/" + self.mcid + "/" + self.fname + ".txt","w+")
        f.write(pickle.dumps(self.__dict__))
        f.close()
    def load(self):
        f = open("fp-mc/" + self.mcid + "/" + self.fname + ".txt","r")
        dataPickle = f.read()
        f.close()
        self.__dict__ = pickle.loads(dataPickle)


class Part(object):
    def __init__(self,mc,mcid,position,ptype=None,ptime=None,creators=None,pgroups=None,pcolors=None,status=None,video=None):
        (filename, line_number, function_name, text) = traceback.extract_stack()[-2]
        def_name = text[:text.find('=')].strip()
        self.fname = def_name
        self.mcid = mcid

        try: self.load()
        except:
            self.ptype = ptype
            self.ptime = ptime
            self.pgroups = pgroups
            self.pcolors = pcolors
            self.creators = creators
            self.mc = mc
            self.position = position
            self.status = status
            self.video = video
            self.slots = []
    def generateslots_normal(self,ptype,creators):
        # Order matters for list: creators
        # If 1LXD: creators[0] will always be the Layouter slot
        if ptype == "XLXD":
            self.slots.append(Slot(mc=self.mc, part=self, stype="L", sid=self.position, creator=creators[0],mcid=self.mcid))
            self.slots.append(Slot(mc=self.mc, part=self, stype="D", sid=self.position, creator=creators[1],mcid=self.mcid))
        if ptype == "XC":
            self.slots.append(Slot(mc=self.mc, part=self, stype="C", sid=self.position, creator=creators[0],mcid=self.mcid))
        if ptype == "1LXD":
            self.slots.append(Slot(mc=self.mc, part=self, stype="D", sid=self.position, creator=creators[1],mcid=self.mcid))
    def generateslots_custom(self,custom):
        """
        :param custom: List of Dictionaries containing part structure
        A single part can have max 4 slots
        Example:
        [{
            'partpos': 1,
            'slots': [
            {
                'stype': 'L1'
                'creator': discord user obj
            },
            {
                'stype': 'D1'
                'creator': discord user obj
            }
            ]
        },
        {
            'partpos': 2
            'slots': [
            {
                'stype': 'L2'
                'creator': discord user obj
            },
            {
                'stype': 'D2'
                'creator': discord user obj
            }
            ]
        },...]
        """
        for part in custom:
            if part is not None:
                if part['partpos'] == self.position:
                    for slot in part['slots']:
                        self.slots.append(Slot(mc=self.mc, mcid=self.mcid,part=self, stype=slot['stype'][0], sid=int(slot['stype'][1]),
                                               creator=slot['creator']))
                    break
    def save(self):
        f = open("fp-mc/" + self.mcid + "/" + self.fname + ".txt","w+")
        f.write(pickle.dumps(self.__dict__))
        f.close()
    def load(self):
        f = open("fp-mc/" + self.mcid + "/" + self.fname + ".txt","r")
        dataPickle = f.read()
        f.close()
        self.__dict__ = pickle.loads(dataPickle)
    def __str__(self):
        psstatus = EMOJI_EMPTY
        if self.status == "assigned": psstatus = EMOJI_ASSIGNED
        if self.status == "progress": psstatus = EMOJI_PROGRESS
        if self.status == "finished": psstatus = EMOJI_FINISHED
        pstime = "`No Time Range assigned`"
        if self.ptime is not None: pstime = self.ptime
        pscreators = "UNASSIGNED"
        if len(self.creators) >= 1:
            pscreators = ""
            for creator in self.creators: pscreators += creator.name + " "
        pscolors = "`No Colors generated`"
        if self.pcolors is not None: pscolors = self.pcolors
        psgroups = "`No Groups generated`"
        if self.pgroups is not None: psgroups = self.pgroups
        return psstatus + " " + pstime + " - " + pscreators + " - Colors: " + pscolors + " - Groups: " + psgroups

class Slot(object):
    def __init__(self,mc,mcid,part,stype,sid,creator):
        (filename, line_number, function_name, text) = traceback.extract_stack()[-2]
        def_name = text[:text.find('=')].strip()
        self.fname = def_name
        self.mcid = mcid

        try: self.load()
        except:
            self.mc = mc
            self.part = part
            self.stype = stype
            self.sid = sid
            self.creator = creator
    def save(self):
        f = open("fp-mc/" + self.mcid + "/" + self.fname + ".txt","w+")
        f.write(pickle.dumps(self.__dict__))
        f.close()
    def load(self):
        f = open("fp-mc/" + self.mcid + "/" + self.fname + ".txt","r")
        dataPickle = f.read()
        f.close()
        self.__dict__ = pickle.loads(dataPickle)

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
    return None

def GetRole(s,rn):
    try:
        rid = int(rn)
        return discord.utils.find(lambda r: str(rid) in str(r.id), s.roles)
    except: return discord.utils.find(lambda r: rn.lower() in r.name.lower(), s.roles)

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
    return None

async def GetMessage(channel,mid):
    async for message in channel.history(limit=200):
        if str(message.id) == str(mid): return message

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
              "invalidparams":"Invalid parameters!",
              "nomc":"You are not hosting a Megacollab here!",
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

async def ParameterResponseEmbed(ctx,title,parameters: list):
    global newparameters; global responsedonecalled
    # parameters: [['name','string',"",True],['parts','integer',0,True],['creators','list',[],False]]
    # param types: string, integer, list, discord user, list of discord users, boolean
    if len(parameters) == 0: return []
    newparameters = copy.deepcopy(parameters)
    responseembed = discord.Embed(title=title,description=
    "*Type >>param \"parameter\" \"new value(s)\" to change conditions, and >>done when done*",color=0x5c5c5c)
    for param in newparameters:
        paramr = " "
        if param[3]: paramr = " *"
        paramvalue = ""
        if param[1] == "string": paramvalue = param[2]
        if param[1] == "boolean": paramvalue = param[2]
        if param[1] == "integer": paramvalue = str(param[2])
        if param[1] == "list":
            if not param[2]: paramvalue = "None"
            else: paramvalue = str(param[2]).replace("[","").replace("]","")
        if param[1] == "discord user":
            paramvalue = GetMemberGlobal(param[2])
            if paramvalue is None: paramvalue = "None"
            else: paramvalue = paramvalue.name
        if param[1] == "list of discord users":
            if not param[2]: paramvalue = "None"
            else:
                paramvalue = param[2]
                for p in paramvalue:
                    tp = GetMemberGlobal(p)
                    if tp is None: paramvalue[paramvalue.index(p)] = "None"
                    else: paramvalue[paramvalue.index(p)] = tp.name
                paramvalue = str(paramvalue).replace("[","").replace("]","")
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
                    paramql = []
                    if p[1] == "boolean":
                        if paramq[1].lower() != "false" and paramq[1].lower() != "true": return False
                    if p[1] == "list": paramq[1] = paramlistlist(paramresponse,1)
                    if p[1] == "discord user":
                        paramq[1] = GetMemberGlobal(paramq[1])
                        if paramq[1] is None: return False
                    if p[1] == "list of discord users":
                        paramq[1] = paramlistlist(paramresponse, 1)
                        paramql = paramq[1]
                        for pq in paramql:
                            pqt = GetMemberGlobal(pq)
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
                        for pq in paramq[1]: paramq[1][paramq[1].index(pq)] = pq.name
                        responseembed.set_field_at(p[4], name=p[0], value=str(paramq[1]),inline=False)
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
        mcd[4] = GetMemberGlobal(mcd[4]); mcd[5] = StrToLODU(mcd[5])
        if mchost == ctx.author and mcserver == ctx.message.guild: mcsfound.append(mcd)
    if not mcsfound: return None
    if len(mcsfound) == 1: return mcsfound[0]
    else:
        iin = 1; mcfmcs = ""
        for mc in mcsfound:
            iil = "**A** - "
            if iin == 2: iil = "**B* - "
            if iin == 3: iil = "**C* - "
            if iin == 4: iil = "**D* - "
            if iin == 5: iil = "**E* - "
            mcfmcs += iil + mc[0] + "\n"
            iil += 1
        mcfm = await ctx.message.channel.send("**" + ctx.author.name + "**, which megacollab are you referring to?\n" + mcfmcs)
        mcmresponse = await ReactionChoiceMessage(ctx,mcfm,iin)
        if 1 <= mcmresponse <= 5: return mcsfound[mcmresponse - 1]
        else: return None

async def AutoMCContext(message):
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
        mcd[4] = GetMemberGlobal(mcd[4]); mcd[5] = StrToLODU(mcd[5])
        if mchost == message.author and mcserver == message.guild: mcsfound.append(mcd)
    if not mcsfound: return None
    if len(mcsfound) == 1: return mcsfound[0]
    else:
        for mcc in mcsfound:
            msChannelParts = GetChannel(message.guild,
                                        datasettings(file="fp-mc/" + mcc[8] + ".txt", method="get", line="CHANNEL-PARTS"))
            msChannelUpdates = GetChannel(message.guild, datasettings(file="fp-mc/" + mcc[8] + ".txt", method="get",
                                                                          line="CHANNEL-UPDATES"))
            msChannelProgress = GetChannel(message.guild, datasettings(file="fp-mc/" + mcc[8] + ".txt", method="get",
                                                                           line="CHANNEL-PROGRESS"))
            msChannelFinishedParts = GetChannel(message.guild,
                                                datasettings(file="fp-mc/" + mcc[8] + ".txt", method="get",
                                                             line="CHANNEL-FINISHEDPARTS"))
            if msChannelParts is not None:
                if message.channel == msChannelParts: return mcc
            if msChannelUpdates is not None:
                if message.channel == msChannelUpdates: return mcc
            if msChannelFinishedParts is not None:
                if message.channel == msChannelFinishedParts: return mcc
            if msChannelProgress is not None:
                if message.channel == msChannelProgress: return mcc
        return None

def StrToLODU(st):
    if st == "[]": return []
    stm = st.replace("[","").replace("]",""); stm = stm.split(",")
    for u in stm: stm[stm.index(u)] = GetMemberGlobal(u)
    return stm

def DUToStr(du):
    dus = "None"
    try: dus = du.name
    except: pass
    return dus

def StrToList(st):
    stm = st.replace("[", "").replace("]", "").replace("'","")
    stm = stm.split(",")
    for s in stm:
        if s.startswith(" "): stm[stm.index(s)] = s[1:]
    return stm

def LODUToStr(l):
    if not l: return "None"
    for du in l:
        dus = "None"
        try: dus = du.id
        except: pass
        l[l.index(du)] = dus
    return str(l)

def LODUToStrName(l):
    if not l: return "None"
    for du in l:
        dus = "None"
        try: dus = du.name
        except: pass
        l[l.index(du)] = dus
    return str(l).replace("[","").replace("]","").replace("'","")

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

def PartsMessage(mcid,pos):
    pmCreators = LODUToStrName(StrToLODU(datasettings(file="fp-mc/" + mcid + "/PART" + pos + ".txt",method="get",line="CREATORS")))
    pmGroups = datasettings(file="fp-mc/" + mcid + "/PART" + pos + ".txt",method="get",line="GROUPS")
    pmColors = datasettings(file="fp-mc/" + mcid + "/PART" + pos + ".txt",method="get",line="COLORS")
    pmTime = datasettings(file="fp-mc/" + mcid + "/PART" + pos + ".txt",method="get",line="TIME")
    pmStatus = statusEmoji[datasettings(file="fp-mc/" + mcid + "/PART" + pos + ".txt",method="get",line="STATUS").lower()]
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
    for n in range(1, int(mc[3]) + 1): pmf += PartsMessage(mc[8],str(n)) + "\n"
    return pmf

async def InitGenerateParts(mc,channel):
    for n in range(1,int(mc[3]) + 1):
        newfile("fp-mc/" + mc[8] + "/PART" + str(n) + ".txt")
        datasettings(file="fp-mc/" + mc[8] + "/PART" + str(n) + ".txt",method="add",newkey="CREATORS",newvalue="[]")
        datasettings(file="fp-mc/" + mc[8] + "/PART" + str(n) + ".txt", method="add", newkey="PARTDESC", newvalue="None")
        datasettings(file="fp-mc/" + mc[8] + "/PART" + str(n) + ".txt",method="add",newkey="GROUPS",newvalue="None")
        datasettings(file="fp-mc/" + mc[8] + "/PART" + str(n) + ".txt",method="add",newkey="COLORS",newvalue="None")
        datasettings(file="fp-mc/" + mc[8] + "/PART" + str(n) + ".txt",method="add",newkey="TIME",newvalue="0:00-0:00")
        datasettings(file="fp-mc/" + mc[8] + "/PART" + str(n) + ".txt", method="add", newkey="VIDEO", newvalue="None")
        datasettings(file="fp-mc/" + mc[8] + "/PART" + str(n) + ".txt", method="add", newkey="STATUS", newvalue="Empty")
    # Assigning Colors
    apin = True
    for n in range(1, int(mc[3]) + 1):
        if apin:
            datasettings(file="fp-mc/" + mc[8] + "/PART" + str(n) + ".txt",method="change",line="COLORS",newvalue="1-100")
            apin = False
        else:
            datasettings(file="fp-mc/" + mc[8] + "/PART" + str(n) + ".txt",method="change",line="COLORS",newvalue="101-200")
            apin = True
    # Assigning Groups
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
            else:
                datasettings(file="fp-mc/" + mc[8] + "/PART" + str(n) + ".txt", method="change", line="GROUPS",
                             newvalue=str(int(apn + 1)) + "-" + str(int(apn + apc))); apn += apc
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
    pmCreators = StrToLODU(datasettings(file="fp-mc/" + mcid + "/PART" + pos + ".txt", method="get", line="CREATORS"))
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
            mcCreators = StrToLODU(datasettings(file="fp-mc/" + mcid + "/PART" + str(n) + ".txt",method="get",line="CREATORS"))
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
    await user.send("Finish Part Bot reminds you to Finish your Part in **" + mc[0] + "**!")


@client.event
async def on_ready():
    print("Bot Ready!")
    print("Name: " + client.user.name + ", ID: " + str(client.user.id))
    sl = ""
    for server in client.guilds:
        if server is not None: sl += server.name + ", "
    print("Connected Guilds: " + sl[:len(sl) - 2])

@client.event
async def on_message(message):
    mcc = AutoMCContext(message)
    if mcc is not None:
        mdt = datasettings(file="fp-mc/" + mcc[8] + "/ACTIVITYLOG/" + str(message.author.id) + ".txt",method="get",line="TEST")
        if mdt is None:
            newfile("fp-mc/" + mcc[8] + "/ACTIVITYLOG/" + str(message.author.id) + ".txt")
            datasettings(file="fp-mc/" + mcc[8] + "/ACTIVITYLOG/" + str(message.author.id) + ".txt",method="add",newkey="TEST",newvalue=str(message.author.id))
        mdl = latestdata("fp-mc/" + mcc[8] + "/ACTIVITYLOG/" + str(message.author.id) + ".txt")
        if mdl != "TEST":
            mdlt = StrToDatetime(mdl); mdt = StrToDatetime(DatetimeToStr(datetime.datetime.now()))
            if mdt > mdlt:
                datasettings(file="fp-mc/" + mcc[8] + "/ACTIVITYLOG/" + str(message.author.id) + ".txt",method="remove",line=mdl)
                datasettings(file="fp-mc/" + mcc[8] + "/ACTIVITYLOG/" + str(message.author.id) + ".txt",method="add",
                             newkey=DatetimeToStr(mdlt),newvalue=str(message.id))


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
                                                                                      ["Song","string",hostMC_SONG,True],
                                                                                      ["Difficulty","string",hostMC_DIFFICULTY,True],
                                                                                      ["Other Hosts","list of discord users",hostMC_OTHERHOSTS,False],
                                                                                      ["Parts","integer",hostMC_PARTS,False],
                                                                                      ["Verifier","discord user",hostMC_VERIFIER,False]])
                    if not hostMC1R: await ResponseMessage(ctx,"","failed","invalidparams")
                    else:
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
                            str(hostMC_PARTS) + ";" + str(mcohid) + ";" + mcv + ";" + \
                              str(ctx.message.author.id) + ";" + str(ctx.message.guild.id)
                        datasettings(file="fp-mcdir.txt",method="add",newkey=hostMC_ID,newvalue=mcw)
                        datasettings(file="fp-mc/" + hostMC_ID + ".txt",method="add",newkey="NAME",newvalue=hostMC_NAME)
                        datasettings(file="fp-mc/" + hostMC_ID + ".txt",method="add",newkey="SONG",newvalue=hostMC_SONG)
                        datasettings(file="fp-mc/" + hostMC_ID + ".txt",method="add",newkey="DIFFICULTY",newvalue=hostMC_DIFFICULTY)
                        datasettings(file="fp-mc/" + hostMC_ID + ".txt", method="add", newkey="PARTS", newvalue=str(hostMC_PARTS))
                        datasettings(file="fp-mc/" + hostMC_ID + ".txt", method="add", newkey="OTHERHOSTS", newvalue=str(mcohid))
                        datasettings(file="fp-mc/" + hostMC_ID + ".txt", method="add", newkey="VERIFIER",newvalue=mcv)
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
                        if hostMC_VERIFIER != "None": await hostMC_VERIFIER.add_roles(hostMC_VERIFIERROLE)
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
                        datasettings(file="fp-mc/" + hostMC_ID, method="add", newkey="ROLE-HOST", newvalue=str(hostMC_HOSTROLE.id))
                        if hostMC_OTHERHOSTS:
                            datasettings(file="fp-mc/" + hostMC_ID, method="add", newkey="ROLE-COHOST", newvalue=str(hostMC_COHOSTROLE.id))
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
                elif hostServerResponse == 2:
                    await ResponseMessage(ctx,"Megacollab Server Creation not supported yet!","failed")
            else:
                await ResponseMessage(ctx,"","failed","botlacksperms")
        else:
            await ResponseMessage(ctx,"You need to be in a Server to perform this!","failed")
    else:
        await ResponseMessage(ctx,"","failed","authorlacksperms")

@client.command(pass_context=True)
async def generateparts(ctx):
    if AuthorHasPermissions(ctx):
        if ctx.guild:
            if BotHasPermissions(ctx):
                mcc = await MCContext(ctx)
                if mcc is not None:
                    if not datasettings(file="fp-mc/" + mcc[8] + "/PART1.txt",method="get",line="CREATORS"):
                        gpMessage = await InitGenerateParts(mcc,ctx.message.channel)
                        datasettings(file="fp-mc/" + mcc[8] + ".txt",method="add",newkey="MESSAGEPARTS-" + str(ctx.message.channel.id),newvalue=str(gpMessage.id))
                        await ctx.message.delete()
                    else:
                        await ResponseMessage(ctx,"You've already generated Parts!","failed")
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
                        partCreators = StrToList(LODUToStrName(StrToLODU(datasettings(file="fp-mc/" + mcc[8] + "/PART" + str(partnum) + ".txt",method="get",line="CREATORS"))))
                        partTime = datasettings(file="fp-mc/" + mcc[8] + "/PART" + str(partnum) + ".txt",method="get",line="TIME")
                        partVideo = datasettings(file="fp-mc/" + mcc[8] + "/PART" + str(partnum) + ".txt",method="get",line="VIDEO")
                        partDesc = datasettings(file="fp-mc/" + mcc[8] + "/PART" + str(partnum) + ".txt",method="get",line="PARTDESC")
                        partR = await ParameterResponseEmbed(ctx,"Edit Part " + str(partnum),[["Creators","list of discord users",partCreators,False],
                                                                                              ["Time","string",partTime,False],
                                                                                              ["Status","string",partStatus,False],
                                                                                              ["Video","string",partVideo,False],
                                                                                              ["Description","string",partDesc,False]])
                        if not partR: await ResponseMessage(ctx,"","failed","invalidparams")
                        else:
                            dataCreators = LODUToStr(partR[0][2])
                            if "None" not in dataCreators:
                                datasettings(file="fp-mc/" + mcc[8] + "/PART" + str(partnum) + ".txt", method="change", line="CREATORS", newvalue=dataCreators)
                            datasettings(file="fp-mc/" + mcc[8] + "/PART" + str(partnum) + ".txt", method="change", line="TIME", newvalue=partR[1][2])
                            datasettings(file="fp-mc/" + mcc[8] + "/PART" + str(partnum) + ".txt", method="change", line="STATUS", newvalue=partR[2][2])
                            datasettings(file="fp-mc/" + mcc[8] + "/PART" + str(partnum) + ".txt", method="change", line="VIDEO", newvalue=partR[3][2])
                            datasettings(file="fp-mc/" + mcc[8] + "/PART" + str(partnum) + ".txt", method="change", line="PARTDESC", newvalue=partR[4][2])
                            await RefreshParts(mcc)
                            await ResponseMessage(ctx,"Part config Updated.","success")
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
                    msR = await ParameterResponseEmbed(ctx,"Megacollab Settings for " + mcc[0],[["Channels are Visibile to Everyone","boolean",msVisibility,False],
                                                                                                ["Creators can find this MC if Parts are Open","boolean",msInviting,False],
                                                                                                ["Slacking Creators are notified to Finish Parts","boolean",msNotify,False]])
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
                        if msChannelParts is not None: await msChannelParts.set_permissions(ctx.message.guild.default_role, mso)
                        if msChannelUpdates is not None: await msChannelUpdates.set_permissions(ctx.message.guild.default_role, mso)
                        if msChannelProgress is not None: await msChannelProgress.set_permissions(ctx.message.guild.default_role, mso)
                        if msChannelFinishedParts is not None: await msChannelFinishedParts.set_permissions(ctx.message.guild.default_role, mso)
                        datasettings(file="fp-mc/" + mcc[8] + ".txt", method="change", line="SETTINGS-INVITING", newvalue=msR[1][2])
                        datasettings(file="fp-mc/" + mcc[8] + ".txt", method="change", line="SETTINGS-NOTIFY", newvalue=msR[2][2])
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
                        iaserver = GetGuild(iaserver)
                        if iaserver is not None:
                            tia = datasettings(file="fp-mc/" + mcc[8] + ".txt",method="get",line=str(iaserver.id))
                            if tia is None:
                                datasettings(file="fp-mc/" + mcc[8] + ".txt",method="add",newkey=str(iaserver.id),newvalue="ALLOWEDSERVER")
                                await ResponseMessage(ctx, "Server added to Allowed list for Invites!","success")
                            else:
                                await ResponseMessage(ctx, "Server already Allowed!", "failed")
                        else:
                            await ResponseMessage(ctx, "Invalid Server!", "failed")
                    else:
                        await ResponseMessage(ctx,"Open MC Invites are not Allowed! *Type ??mcsettings to change this*")
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
                        iaserver = GetGuild(iaserver)
                        if iaserver is not None:
                            tia = datasettings(file="fp-mc/" + mcc[8] + ".txt",method="get",line=str(iaserver.id))
                            if tia is not None:
                                datasettings(file="fp-mc/" + mcc[8] + ".txt",method="remove",line=str(iaserver.id))
                                await ResponseMessage(ctx, "Server remvoved from Allowed list for Invites!","success")
                            else:
                                await ResponseMessage(ctx, "Server not already ALlowed!", "failed")
                        else:
                            await ResponseMessage(ctx, "Invalid Server!", "failed")
                    else:
                        await ResponseMessage(ctx,"Open MC Invites are not Allowed! *Type ??mcsettings to change this*")
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
        pfBio = pfR[0][2]
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
async def portfolio(ctx):
    if datasettings(file="fp-portfolio/" + str(ctx.message.author.id) + ".txt", method="get", line="BIO") is None:
        await ResponseMessage(ctx, "You have not made a Portfolio! *Type ??portfolio*", "failed")
    else: await ctx.message.channel.send(embed=Portfolio(ctx.message.author))

@client.command(pass_context=True)
async def openmcs(ctx):
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
                    mcpStatus = datasettings(file="fp-mc/" + mcid + "/PART" + str(n) + ".txt",method="get",line="Status")
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
            omll = "A"; omln = 1; omlm = ""; omlk = {1:"A",2:"B",3:"C",4:"D",5:"E"}
            for mc in omc:
                omlm += "**" + omll + "** - " + mc[0] + " by " + GetMemberGlobal(mc[6]).name + "\n"
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
            await ResponseMessage(ctx,"There are no Open MCs for you right now! :(","failed")
    else:
        await ResponseMessage(ctx,"You need to create a Portfolio first! *Type ??portfolio*","failed")


@client.command(pass_context=True)
async def mypart(ctx):
    if ctx.guild:
        mcc = await MCContext(ctx)
        if mcc is not None:
            for n in range(1, int(mcc[3]) + 1):
                mpCreators = StrToLODU(datasettings(file="fp-mc/" + mcc[8] + "/PART" + str(n) + ".txt",method="get",line="CREATORS"))
                if ctx.author in mpCreators:
                    await GetPart(ctx,mcc,str(n))
        else:
            await ResponseMessage(ctx, "", "failed", "nomc")
    else:
        await ResponseMessage(ctx,"You need to be in a Server to perform this!","failed")



@client.command(pass_context=True)
async def ctest(ctx):
    mcc = await MCContext(ctx)
    print(mcc)


client.run(SECRET)