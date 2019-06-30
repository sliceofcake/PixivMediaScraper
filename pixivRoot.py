# coding=utf-8
import threading
import urllib
import urllib2
import re
import os
import glob
import sys
import getopt
import math
import time
import Queue
import json
import inspect

# !!! TODO
# • is {"Connection":"keep-alive"} being properly used? is it needed? is it helping? is it hurting?

#escape a filename [sounds bad, but I really don't have a guarantee that this is enough]
def esc(m):
	s = str(m)
	# dots are only useful for path traversal if nearby slashes, which we get rid of, so they should only be dangerous by themselves
	if s == "." :return "。"
	if s == "..":return "。。"
	s = re.sub('\\\\','＼',s)
	s = re.sub('/','／',s)
	s = re.sub('"','”',s)
	s = re.sub('\'','’',s)
	s = re.sub('\*','＊',s)
	s = re.sub('\$','＄',s)
	s = re.sub(':','：',s) # Apple's handling of this being a special character
	return s
# if folder exists, good. if not, and no similars, make it. if not and similar[s], take first similar and rename it.
def assertFolder(foldername=None,wildname=None):
	if not os.path.isdir(foldername):
		matchA = glob.glob(wildname)
		if len(matchA) == 0:
			os.mkdir(foldername)
		else:
			os.rename(matchA[0],foldername)
def printUsage():
	global p
	sys.stdout.write("usage   : python pixivRoot.py [-t threadcount]"+os.linesep)
	sys.stdout.write("example : python pixivRoot.py"+os.linesep)
	sys.stdout.write("example : python pixivRoot.py -t 32"+os.linesep)
	sys.stdout.write("-h                : display help information, which is what you're reading right now"+os.linesep)
	sys.stdout.write("--help            : display help information, which is what you're reading right now"+os.linesep)
	sys.stdout.write("-t threadcount    : number of threads used"+os.linesep)
	sys.stdout.write("                    type : integer | minimum : 1 | maximum : "+str(p["threadMaxC"])+" | default : "+str(p["threadC"])+os.linesep)
	sys.stdout.write("                    • as you use more threads, your download rate and CPU usage will rise"+os.linesep)
	sys.stdout.write("                    • out of courtesy toward pixiv, I recommend keeping threadcount relatively low"+os.linesep)
	sys.stdout.write("                    • pixiv is implied to have both an account and an IP blocking mechanism - scary stuff"+os.linesep)
	sys.stdout.flush()
def ll(m,colorS="default",noLineBreakF=False):
	global p
	sys.stdout.write(("" if colorS=="default" else p["cliColorO"][colorS])+str(m)+("" if colorS=="default" else p["cliColorO"]["end"])+("" if noLineBreakF else os.linesep))
	sys.stdout.flush()
def warn(m):
	ll(m,"y")
def fail(m):
	ll(m,"r")
	sys.exit()
# warning : not diamond-solid
def readFile(filenameS):
	# os.path.isfile(filenameS)
	try:
		file = open(filenameS,"r")
	except EOError as err:
		return None
	txt = file.read()
	file.close()
	return txt
# warning : not diamond-solid
def assertFile(filenameS):
	if not os.path.isfile(filenameS):
		file = open(filenameS,"w")
		file.write("")
		file.close()
def extractLinkData(linkS,method="GET",dataO={},headerO={},returnFalseOnFailureF=False):
	req = urllib2.Request(linkS,urllib.urlencode(dataO),headerO)
	req.get_method = lambda : method
	try:response = urllib2.urlopen(req)
	except urllib2.HTTPError as err:
		if returnFalseOnFailureF:return False
		else:fail(linkS+" : "+str(err))
	res = {"txt":response.read(),"txtHeader":str(response.info()),}
	response.close()
	return res

def p_extractTxt(linkS,returnFalseOnFailureF=False):
	global PHPSessionID
	reqE = extractLinkData(linkS,"GET",{},{"Cookie":"PHPSESSID="+PHPSessionID,"Connection":"keep-alive",},True)
	if reqE == False:
		if returnFalseOnFailureF:
			return False
		else:
			fail("ERROR : Failed to extract text from "+linkS+" (fetch error)")
	return reqE["txt"]
def p_extractJson(linkS,returnFalseOnFailureF=False):
	try:
		return json.loads(p_extractTxt(linkS))
	except:
		if returnFalseOnFailureF:
			return False
		else:
			fail("ERROR : Failed to extract JSON from "+linkS+" (decode error)")
def p_extractJsonO(linkS,returnFalseOnFailureF=False):
	res = p_extractJson(linkS,returnFalseOnFailureF)
	if type(res) is not dict:
		if returnFalseOnFailureF:
			return False
		else:
			fail("ERROR : Failed to extract JSON Object from "+linkS+" (root type not Object)")
	return res
def p_regex(patternS,subjectS,returnFalseOnFailureF=False):
	m = re.search(patternS,subjectS)
	if m is None:
		if returnFalseOnFailureF:
			return False
		else:
			fail("regex parser failed to parse : "+subjectS+" with pattern : "+patternS)
	l = []
	l.append(m.group(0))
	return l+list(m.groups())
def p_any(m,fxn):
	paramC = len(inspect.getargspec(fxn).args)
	if type(m) is dict:
		if paramC == 0:
			for k,v in m.items():
				if fxn():
					return True
		if paramC == 1:
			for k,v in m.items():
				if fxn(v):
					return True
		if paramC == 2:
			for k,v in m.items():
				if fxn(v,k):
					return True
		if paramC == 3:
			for k,v in m.items():
				if fxn(v,k,m):
					return True
	elif type(m) is list:
		if paramC == 0:
			for i,v in enumerate(m):
				if fxn():
					return True
		if paramC == 1:
			for i,v in enumerate(m):
				if fxn(v):
					return True
		if paramC == 2:
			for i,v in enumerate(m):
				if fxn(v,i):
					return True
		if paramC == 3:
			for i,v in enumerate(m):
				if fxn(v,i,m):
					return True
	return False
# Source : [https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks]
def p_lChunk(l,n):
	for i in xrange(0,len(l),n):
		yield l[i:i+n]

p = {
	"threadC"          : 16,
	"threadMaxC"       : 64,
	"emailS"           : "",
	"passwordS"        : "",
	"userIDA"          : [],
	"jobEQueue_stage1" : Queue.Queue(),
	"jobEQueue_stage2" : Queue.Queue(),
	"pageTypeSA"       : ["p","ugoira"], # the order here is by probability
	"extensionSA"      : [".jpg",".png",".gif"],} # the order here is by probability
# command-line interface colors, enabled for mac os x where I know it works, disabled everywhere else
# https://docs.python.org/2/library/sys.html#platform
# System              | platform value
# --------------------+---------------
# Linux (2.x and 3.x) | 'linux2'
# Windows             | 'win32'
# Windows/Cygwin      | 'cygwin'
# Mac OS X            | 'darwin'
# OS/2                | 'os2'
# OS/2 EMX            | 'os2emx'
# RiscOS              | 'riscos'
# AtheOS              | 'atheos'
if sys.platform == "darwin":
	p["cliColorO"] = {
		"r"         : "\033[91m",
		"g"         : "\033[92m",
		"b"         : "\033[94m",
		"c"         : "\033[96m",
		"m"         : "\033[95m",
		"y"         : "\033[93m",
		"gray"      : "\033[90m",
		"end"       : "\033[0m",
		# plain color [colored BIU exists, look it up if you want it]
		"bold"      : "\033[1m",
		"underline" : "\033[4m",}
else:
	p["cliColorO"] = {
		"r"         : "",
		"g"         : "",
		"b"         : "",
		"c"         : "",
		"m"         : "",
		"y"         : "",
		"gray"      : "",
		"end"       : "",
		# plain color [colored BIU exists, look it up if you want it]
		"bold"      : "",
		"underline" : "",}



ll("---- START ----","c")
ll("To stop this program, use Control+Z for Apple Operating Systems.","m")




# handle command-line arguments
# ----------------------------------------------------------------------------------------------------------------------
try:optA,leftoverA = getopt.getopt(sys.argv[1:],'ht:T:',['help'])
except getopt.GetoptError as err:printUsage();fail("ERROR : "+str(err))
for opt,arg in optA:
	if opt in ["-h","--help"]:printUsage();sys.exit()
	if opt in ["-t"]:
		try:p["threadC"] = int(arg)
		except ValueError as err:fail("ERROR : [-t threadcount] argument not integer : "+arg)
		if p["threadC"] <               1:fail("ERROR : [-t threadcount] argument too small (min:1) : "+arg)
		if p["threadC"] > p["threadMaxC"]:fail("ERROR : [-t threadcount] argument too large (max:"+str(p["threadMaxC"])+") : "+arg)




# handle userIDA.txt
# ----------------------------------------------------------------------------------------------------------------------
assertFile("userIDA.txt")
txt = readFile("userIDA.txt")
# remove comments
txt = re.sub(re.compile('//.*$',re.MULTILINE),'',txt)
# parse for ints
userIDSA = re.split('\\D+',txt)
for userIDS in userIDSA:
	if userIDS != "": # because of how the regex split that I wrote works, blanks may show up at the front and back
		p["userIDA"].append(int(userIDS))
		p["jobEQueue_stage1"].put({"classnameS":"Stage1Job","argO":{"userID":int(userIDS)}},False)
if len(p["userIDA"]) == 0:fail("ERROR : Fill in your userIDA.txt file with pixiv userIDs (the number found in the URL bar for a profile page), one per line")




# handle login.txt
# ----------------------------------------------------------------------------------------------------------------------
assertFile("login.txt")
txt = readFile("login.txt")
# remove comments
txtA = txt.splitlines()
if len(txtA) < 2:fail("ERROR : Fill in your login.txt file with email on first line, password on second line")
p["emailS"]    = txtA[0]
p["passwordS"] = txtA[1]
ll("userID List : "+str(p["userIDA"]))




# pixiv login to obtain PHPSESSID cookie
# ----------------------------------------------------------------------------------------------------------------------
# open the login page
reqE = extractLinkData("https://accounts.pixiv.net/login","GET")

# get the form callback key, there are two places to find it, I chose the JSON location
# L> <input type="hidden" name="post_key" value="4d0dc83acbe2f27ba139be1559c4455d">
# L> "pixivAccount.postKey":"4d0dc83acbe2f27ba139be1559c4455d"
m = re.search('"pixivAccount\.postKey":"(.+?)"',reqE["txt"])
if not m:fail("ERROR : could not find login callback key [developer's fault - pixiv changed their login page format]")
postKey = m.group(1)
ll("postKey GET!! : "+postKey,"m")

# get the callback cookie from the header
m = re.search('PHPSESSID=(.+?);',reqE["txtHeader"])
if not m:fail("ERROR : could not find login callback cookie [developer's fault - pixiv changed their login page format]")
PHPSessionID = m.group(1)
ll("PHPSessionID GET!! : "+PHPSessionID,"m")

# make the signin request
ll("attempting to sign in as user:"+p["emailS"])
reqE = extractLinkData("https://accounts.pixiv.net/api/login?lang=en","POST",{"pixiv_id":p["emailS"],"password":p["passwordS"],"captcha":"","g_recaptcha_response":"","post_key":postKey,"source":"accounts",},{"Connection":"keep-alive","Cookie":"PHPSESSID="+PHPSessionID,})
ll("pixiv says : "+reqE["txt"],"m")

# get the newest cookie before we proceed
m = re.search('PHPSESSID=(.+?);',reqE["txtHeader"])
if not m:fail("ERROR : could not find login response cookie [either -> your fault - invalid signin information, temporarily captcha-gated account, unexplainably temporarily locked account OR developer's fault - pixiv changed their login page format]. Try visiting pixiv in a web browser and logging in manually with your designated account to see if the login page says anything interesting. In the worst case, try making a new account (and update your authentication text file accordingly).")
PHPSessionID = m.group(1)
ll("PHPSessionID GET!! : "+PHPSessionID,"m")




# scan each artist for image download links
# ----------------------------------------------------------------------------------------------------------------------
class Stage1Job():
	def __init__(self,userID=0):
		self.userID = userID
		self.foldername = None
	def run(self):
		global p
		userIDS = str(self.userID)
		imageEA = []
		try: # try-except-finally misused here so that "return" takes it to the finally block, where we can wrap up
			
			# GET USERNAME
			#-------------
			txtS = p_extractTxt("https://www.pixiv.net/member.php?id="+userIDS,True)
			if txtS is False:
				warn("WARNING : User:"+str(userIDS)+"'s page is not viewable [probably a closed account].")
				return
			
			# Ensure we're looking at a valid, signed-in page. If not, stop the entire program.
			# !!! Of squishy use in this particular spot. Preferably in a more global-ish one-time place.
			if p_regex('class\s*?=\s*?["\']([^"\']+?\s)*?welcome["\'\s]',txtS,True):
				fail("ERROR : The signin failed [developer's fault - pixiv changed their artist page format].")
			
			if p_regex('class\s*?=\s*?["\']([^"\']+?\s)*?error\-title["\'\s]',txtS,True): # Don't rely on Japanese/English message.
				warn("WARNING : User:"+str(userIDS)+"'s page is not viewable [probably a closed account].")
				return
			
			usernameS = p_regex('<title>「(.+?)」',txtS)[1]
			self.foldername = esc(usernameS+"#"+userIDS)
			assertFolder(foldername=self.foldername,wildname="*"+esc("#"+userIDS))
			
			# read from bottom to top
			#----
			# 28 Sep 2018
			# [officially reported [17 Sep 2018] by AshtonHarding on GitHub]
			# • pixiv has a new look for works - unfortunately only rolled out to some users randomly
			# • they really went all-in with their async API -ness ; whole Stage1Job class needed a makeover
			# • thankfully, they're using their own API, and now it's all API-based
			# • thankfully, we now have a way to almost instantly glean all work information (except for file extensions)
			# • thankfully, this new version of pixivRoot works for both old and new UI types
			#----
			# 29 Dec 2016
			# • pixiv has placeholder links before it asynchronously loads images
			#m = re.findall('data-src="(https?:\/\/[^<>\s]+?\/)[^<>\s]+?(\d{4}\/\d{2}\/\d{2}\/\d{2}\/\d{2}\/\d{2}\/)(\d+)_p(\d+)[^<>\s]+?(\.[^\."]+)"',reqE["txt"])
			#....
			# 19 Dec 2016
			# • pixiv changed their HTML by moving the class:thumbnail portion
			# • the regex dot finder was encountering catastrophic backtracking, so changed them all to [^<>] to stay within the confines of the local HTML tag
			#m = re.findall('<img src="(https?:\/\/[^<>]+?\/)[^<>]+?(\d{4}\/\d{2}\/\d{2}\/\d{2}\/\d{2}\/\d{2}\/)(\d+)_p(\d+)[^<>]+?(\.[^\."]+)"',reqE["txt"])
			#....
			# original [unknown date]
			#m = re.findall('<img src="(https?:\/\/.+?\/).+?(\d{4}\/\d{2}\/\d{2}\/\d{2}\/\d{2}\/\d{2}\/)(\d+)_p(\d+).+?(\.[^\.]+)" class="_thumbnail">',reqE["txt"])
			#----
			
			# GET ALL ILLUST ID
			#------------------
			datO = p_extractJsonO("https://www.pixiv.net/ajax/user/"+userIDS+"/profile/all")
			illustIDNA = map(int,list(set((datO["body"]["illusts"].keys() if type(datO["body"]["illusts"]) is dict else []) + (datO["body"]["manga"].keys() if type(datO["body"]["manga"]) is dict else []))));illustIDNA.sort() # The label "manga" seems to be a misnomer. These works to appear in the old theme's illust pages.
			ll(      userIDS             .rjust( 9," ")+" user"
			+  " | "+str(len(illustIDNA)).rjust(27," ")+" gallery count"
			+  " | "+usernameS                         +" name"
			,"c")
			if len(illustIDNA) == 0:
				return
			#ll(illustIDNA)
			
			# COMPILE ROLODEX0 (GALLERY LIST)
			#--------------------------------
			# [!] This API page is limited to 100 entries at a time.
			rolodex0 = []
			for illustIDNChunkA in p_lChunk(illustIDNA,100):
				datO = p_extractJsonO("https://www.pixiv.net/ajax/user/5607168/profile/illusts?"+("&".join(map(lambda illustIDN:"ids%5B%5D="+str(illustIDN),illustIDNChunkA)))+"&is_manga_top=0")
				rolodex0 += map(lambda tuple:{
					"illustS"   : str(tuple[1]["id"       ]), # [!] Crucial str() calls to convert unicode type to str type.
					"pageC"     :     tuple[1]["pageCount"] ,
					"urlNotS"   : str(tuple[1]["url"      ]),
					"userS"     : str(tuple[1]["userId"   ]),},datO["body"]["works"].iteritems())
			rolodex0 = sorted(rolodex0,key=lambda k:int(k["illustS"]))
			#ll("rolodex0.keys()"+str(map(lambda o:o["illustS"],rolodex0)))
			
			# COMPILE ROLODEX1 (WORK LIST)
			#-----------------------------
			rolodex1 = []
			for row in rolodex0:
				for pageN in range(0,row["pageC"]):
					rolodex1.append({
						"illustS"    : row["illustS"],
						"pageS"      : str(pageN)    ,
						"urlNotS"    : row["urlNotS"],
						"userS"      : row["userS"  ],})
			ll(      userIDS           .rjust( 9," ")+" user"
			+  " | "+str(len(rolodex1)).rjust(30," ")+" work count"
			+  " | "+usernameS                       +" name"
			,"b")
			#ll("rolodex1.keys()"+str(map(lambda o:o["illustS"],rolodex1)))
			
			# COMPILE DOWNLOAD JOBS
			#----------------------
			for row1 in rolodex1:
				
				row2 = {
					"illustS"  : row1["illustS"],
					"pageS"    : row1["pageS"  ],
					"refererS" : "http://www.pixiv.net/member_illust.php?mode=medium&illust_id="+row1["userS"],
					"userS"    : row1["userS"  ],}
				
				localF = False
				for extensionS in p["extensionSA"]:
					pathS = self.foldername+"/"+esc(row2["illustS"]+"_p"+str(row2["pageS"])+extensionS)
					if os.path.isfile(pathS):
						localF = True
						break
				if localF:
					# [21 Oct 2018] Seeing this text was getting annoying since it doesn't matter much.
					#ll(      row2["userS"  ].rjust(9," ")+" user"
					#+  " | "+row2["illustS"].rjust(9," ")+" illust"
					#+  " | "+row2["pageS"  ].rjust(3," ")+" page"
					#+  " | "+("✕ DL" if localF else "◯ DL")
					#+  " | "+usernameS                   +" name"
					#+  " | "+pathS
					#,"default")
					continue
				
				row2["dateS"  ] = p_regex('\d{4}\/\d{2}\/\d{2}\/\d{2}\/\d{2}\/\d{2}\/',row1["urlNotS"])[0]
				row2["domainS"] = p_regex('https?:\/\/[^<>\s]+?\/'                    ,row1["urlNotS"])[0]
				
				breakN = 0
				remoteF = False
				for pageTypeS in p["pageTypeSA"]:
					breakN = 0
					for extensionS in p["extensionSA"]:
						breakN = 0
						urlS  = row2["domainS"]+"img-original/img/"+row2["dateS"]+row2["illustS"]+"_"+pageTypeS+str(row2["pageS"])+extensionS
						pathS = self.foldername                          +"/"+esc(row2["illustS"]+"_"+pageTypeS+str(row2["pageS"])+extensionS)
						reqE  = extractLinkData(urlS,"HEAD",{},{"Referer":row2["refererS"],"Connection":"keep-alive",},returnFalseOnFailureF=True)
						if reqE != False:
							if pageTypeS == "ugoira":
								ll(      row2["userS"  ].rjust(9," ")+" user"
								+  " | "+row2["illustS"].rjust(9," ")+" illust"
								+  " | "+row2["pageS"  ].rjust(3," ")+" page"
								+  " | "+"✕ DL"
								+  " | "+usernameS                   +" name"
								+  " | "+pathS
								+  " | "+"[!] ugoira not yet supported."
								,"y")
								breakN = 3
								break
							remoteF = True
							breakN = 2
							break
					if breakN >= 2:
						break
				if breakN >= 3:
					continue # SURPRISE
				if not remoteF:
					fail("Could not find extension of illust:"+row2["illustS"])
				
				ll(      row2["userS"  ].rjust(9," ")+" user"
				+  " | "+row2["illustS"].rjust(9," ")+" illust"
				+  " | "+row2["pageS"  ].rjust(3," ")+" page"
				+  " | "+("✕ DL" if localF else "◯ DL")
				+  " | "+usernameS                   +" name"
				+  " | "+pathS
				+  " | "+urlS
				,"g")
				
				imageEA.append({"url":urlS,"referer":row2["refererS"],"pathLocal":pathS})
		finally:
			if len(imageEA) >= 1:
				imageEQueue = Queue.Queue()
				for imageE in reversed(imageEA):
					imageEQueue.put(imageE)
				p["jobEQueue_stage2"].put({"classnameS":"Stage2Job","argO":{"imageEQueue":imageEQueue}})

class Stage2Job():
	def __init__(self,imageEQueue):
		self.imageEQueue = imageEQueue
	def run(self):
		while True:
			try:
				imageE = self.imageEQueue.get(False)
			except Queue.Empty:
				return
			#ll("△ "+imageE["pathLocal"],"gray")
			reqE = extractLinkData(imageE["url"],"GET",{},{"Referer":imageE["referer"],"Connection":"keep-alive",})
			text_file = open(imageE["pathLocal"],"w")
			text_file.write(reqE["txt"])
			text_file.close()
			ll("◯ "+imageE["pathLocal"],"g")

class Proc(threading.Thread):
	def __init__(self,getFxn):
		super(Proc,self).__init__()
		self.getFxn = getFxn
	def run(self):
		global p
		while True:
			jobE = self.getFxn()
			if jobE == None:
				return
			job = globals()[jobE["classnameS"]](**jobE["argO"])
			job.run()




# scan for each image
# ----------------------------------------------------------------------------------------------------------------------
# multithreaded execute
tA = []
def stage1Fxn():
	global p
	try:
		return p["jobEQueue_stage1"].get(False)
	except Queue.Empty:
		return None
for i in xrange(p["threadC"]):
	t = Proc(getFxn=stage1Fxn)
	t.daemon = True
	tA.append(t)
	t.start()
for t in tA:
	t.join()
tA = []

# read through the queue (without, in the end, modifying it) to count the number of images to download
tempQueue = Queue.Queue()
imageN = 0
while True:
	try:
		jobE = p["jobEQueue_stage2"].get(False)
	except Queue.Empty:
		break
	imageN += jobE["argO"]["imageEQueue"].qsize()
	tempQueue.put(jobE)
while True:
	try:
		jobE = tempQueue.get(False)
	except Queue.Empty:
		break
	p["jobEQueue_stage2"].put(jobE)


# download each image
# ----------------------------------------------------------------------------------------------------------------------
# multithreaded execute
# go in reverse, for historical reason:
#   if the script gets interrupted, then when it's next executed, it won't [as-often] improperly trigger the stopOnFoundF flag
# this is no long necessary, but it seems like good form
ll("Downloading "+str(imageN)+" images...","m")
tA = []
def stage2Fxn():
	global p
	try:
		return p["jobEQueue_stage2"].get(False)
	except Queue.Empty:
		return None
for i in xrange(p["threadC"]):
	t = Proc(getFxn=stage2Fxn)
	t.daemon = True
	tA.append(t)
	t.start()
for t in tA:
	t.join()
tA = []


ll(os.linesep+"END","c")
