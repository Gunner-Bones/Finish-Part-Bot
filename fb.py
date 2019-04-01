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
              "nomc":"You are not hosting a Megacollab here!"}
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
    # param types: string, integer, list, discord user, list of discord users
    if len(parameters) == 0: return []
    newparameters = copy.deepcopy(parameters)
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
                    responseembed.set_field_at(p[4],name=p[0],value=str(paramq[1]))
                    if p[1] == "discord user": responseembed.set_field_at(p[4],name=p[0],value=paramq[1].name)
                    if p[1] == "list of discord users":
                        newparameters[newparameters.index(p)][2] = paramql
                        paramq[1] = []
                        for q in paramql: paramq[1].append(q)
                        for pq in paramq[1]: paramq[1][paramq[1].index(pq)] = pq.name
                        responseembed.set_field_at(p[4], name=p[0], value=str(paramq[1]))
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
    mcsfound = []
    for mcid in alldatakeys("fp-mcdir.txt"):
        mcd = datasettings(file="fp-mcdir.txt",method="get",line=mcid); mcd = mcd.split(";"); mcd.append(mcid)
        mchost = GetMemberGlobal(mcd[6]); mcserver = GetGuild(mcd[7])
        if mchost is None: continue
        if mcserver is None: continue
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

                        hostMC = Megacollab(name=hostMC_NAME,mcid=hostMC_ID,song=hostMC_SONG,difficulty=hostMC_DIFFICULTY,parts=hostMC_PARTS,cohosts=hostMC_OTHERHOSTS,
                                            verifier=hostMC_VERIFIER,host=ctx.message.author,server=ctx.message.guild)
                        MCS.append(hostMC)
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
async def assignparts(ctx):
    if AuthorHasPermissions(ctx):
        if ctx.guild:
            if BotHasPermissions(ctx):
                if await MCContext(ctx) is not None:
                    pass
                else:
                    await ResponseMessage(ctx, "", "failed", "nomc")
            else:
                await ResponseMessage(ctx,"","failed","botlacksperms")
        else:
            await ResponseMessage(ctx,"You need to be in a Server to perform this!","failed")
    else:
        await ResponseMessage(ctx,"","failed","authorlacksperms")

@client.command(pass_context=True)
async def ctest(ctx):
    mcc = await MCContext(ctx)
    print(mcc)
    hostMC = Megacollab(name=mcc[0], mcid=mcc[8], song=mcc[1], difficulty=mcc[2],
                        parts=mcc[3], cohosts=mcc[4],
                        verifier=mcc[5], host=mcc[6], server=mcc[7])
    MCS.append(hostMC)

client.run(SECRET)