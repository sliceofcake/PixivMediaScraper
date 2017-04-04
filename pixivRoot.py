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
	sys.stdout.write("usage   : python pixivRoot.py [-t threadcount] [--complete]"+os.linesep)
	sys.stdout.write("example : python pixivRoot.py"+os.linesep)
	sys.stdout.write("example : python pixivRoot.py --complete"+os.linesep)
	sys.stdout.write("example : python pixivRoot.py -t 32 --complete"+os.linesep)
	sys.stdout.write("-h                : display help information, which is what you're reading right now"+os.linesep)
	sys.stdout.write("--help            : display help information, which is what you're reading right now"+os.linesep)
	sys.stdout.write("--complete        : will scan over all images, even after it recognizes some of them"+os.linesep)
	sys.stdout.write("                    usually, the scanner will stop as soon as it sees a familiar image"+os.linesep)
	sys.stdout.write("                    this option is intended for rarely-done checks of completeness"+os.linesep)
	sys.stdout.write("-t threadcount    : number of threads used"+os.linesep)
	sys.stdout.write("                    type : integer | minimum : 1 | maximum : "+str(p["threadMaxC"])+" | default : "+str(p["threadC"])+os.linesep)
	sys.stdout.write("                    as you use more threads, your download rate and CPU usage will rise"+os.linesep)
	sys.stdout.write("                    out of courtesy toward pixiv, I recommend keeping threadcount relatively low"+os.linesep)
	sys.stdout.flush()
def ll(m,colorS="default",noLineBreakF=False):
	global p
	sys.stdout.write(("" if colorS=="default" else p["cliColorO"][colorS])+str(m)+("" if colorS=="default" else p["cliColorO"]["end"])+("" if noLineBreakF else os.linesep))
	sys.stdout.flush()
def fail(m):
	global p
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
p = {
	"threadC"          : 16,
	"threadMaxC"       : 64,
	"stopOnFoundF"     : True,
	"emailS"           : "",
	"passwordS"        : "",
	"userIDA"          : [],
	"jobEQueue_stage1" : Queue.Queue(),
	"jobEQueue_stage2" : Queue.Queue(),
	"extensionSA"      : [".jpg",".png",".gif"],}
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
try:optA,leftoverA = getopt.getopt(sys.argv[1:],'ht:T:',['help','complete'])
except getopt.GetoptError as err:printUsage();fail("ERROR : "+str(err))
for opt,arg in optA:
	if opt in ["-h","--help"]:printUsage();sys.exit()
	if opt in ["--complete"]:p["stopOnFoundF"] = False
	if opt in ["-t"]:
		try:p["threadC1"] = int(arg)
		except ValueError as err:fail("ERROR : [-t threadcount] argument not integer : "+arg)
		if p["threadC1"] <                1:fail("ERROR : [-t threadcount] argument too small (min:1) : "+arg)
		if p["threadC1"] > p["threadMaxC1"]:fail("ERROR : [-t threadcount] argument too large (max:"+str(p["threadMaxC1"])+") : "+arg)




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
reqE = extractLinkData("https://accounts.pixiv.net/api/login?lang=en","POST",{"pixiv_id":p["emailS"],"password":p["passwordS"],"captcha":"","g_recaptcha_response":"","post_key":postKey,"source":"accounts",},{"Connection":"keep-alive","Cookie":"PHPSESSID="+PHPSessionID,})
ll("pixiv says : "+reqE["txt"],"m")

# get the newest cookie before we proceed
m = re.search('PHPSESSID=(.+?);',reqE["txtHeader"])
if not m:fail("ERROR : could not find login response cookie [either -> your fault - invalid signin information OR developer's fault - pixiv changed their login page format]")
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
		#ll(userIDS.rjust(9," ")+" userID","m")
		imageEA = []
		pageI = 0 # initially incremented to 1
		try: # try-except-finally misused here so that "return" takes it to the finally block, where we can wrap up
			while True:
				pageI += 1
				
				#ll(userIDS.rjust(9," ")+" userID | "+str(pageI).rjust(3," ")+" page")
				
				# make the page request
				reqE = extractLinkData("http://www.pixiv.net/member_illust.php?id="+userIDS+"&type=all&p="+str(pageI),"GET",{},{"Cookie":"PHPSESSID="+PHPSessionID,"Connection":"keep-alive",})
				
				# ensure we're looking at a valid, signed-in page, if not, stop the entire program
				if re.search('Welcome to pixiv',reqE["txt"]):fail("ERROR : the signin failed [developer's fault - pixiv changed their artist page format]")
				
				# get the username on the first round
				if self.foldername == None:
					m = re.search('<h1 class="user">(.+?)</h1>',reqE["txt"]);
					if m:
						username = m.group(1)
						compoundUsername = username+"#"+userIDS
					else:
						ll("WARNING : could not find username on page - falling back to solely userID [developer's fault - pixiv changed their artist page format]","y")
						compoundUsername = "#"+userIDS
					self.foldername = esc(compoundUsername)
					assertFolder(foldername=self.foldername,wildname="*"+esc("#"+userIDS))
				
				# get image links on this page
				# "referer: http://www.pixiv.net/member_illust.php?mode=medium&illust_id=56278541" "http://i2.pixiv.net/img-original/img/2016/04/10/00/00/04/56278541_p0.jpg" -o "USERNAME#299299/56278541_p0.jpg"
				#function(match,domain,date,ID,page,extension,offset,string){link = domain+"img-original/img/"+date+ID+"_p"+page+extension;}
				#<img src="http://i4.pixiv.net/c/150x150/img-master/img/2016/10/17/00/00/07/59506543_p0_master1200.jpg" class="_thumbnail">
				
				# read from bottom to top
				#----
				# 29 Dec 2016
				# • pixiv has placeholder links before it asynchronously loads images
				m = re.findall('data-src="(https?:\/\/[^<>\s]+?\/)[^<>\s]+?(\d{4}\/\d{2}\/\d{2}\/\d{2}\/\d{2}\/\d{2}\/)(\d+)_p(\d+)[^<>\s]+?(\.[^\."]+)"',reqE["txt"])
				#....
				# 19 Dec 2016
				# • pixiv changed their HTML by moving the class:thumbnail portion
				# • the regex dot finder was encountering catastrophic backtracking, so changed them all to [^<>] to stay within the confines of the local HTML tag
				#m = re.findall('<img src="(https?:\/\/[^<>]+?\/)[^<>]+?(\d{4}\/\d{2}\/\d{2}\/\d{2}\/\d{2}\/\d{2}\/)(\d+)_p(\d+)[^<>]+?(\.[^\."]+)"',reqE["txt"])
				#....
				# original [unknown date]
				#m = re.findall('<img src="(https?:\/\/.+?\/).+?(\d{4}\/\d{2}\/\d{2}\/\d{2}\/\d{2}\/\d{2}\/)(\d+)_p(\d+).+?(\.[^\.]+)" class="_thumbnail">',reqE["txt"])
				#----
				
				# if we have image matches
				if len(m) == 0:
					break
				
				# ----------------------------------------
				# for each main image
				tupleI = -1 # initially incremented to 0
				for domain,date,ID,trash0,trash1 in m:
					tupleI += 1
					
					# ----------------------------------------
					# for each individual image
					pageSubI = -1 # initially incremented to 0
					while True:
						pageSubI += 1
						
						foundO = {
							"referer"   : "http://www.pixiv.net/member_illust.php?mode=medium&illust_id="+userIDS,
							"pathLocal" : "",
							"extension" : "",
							"url"       : "",}
						
						# check if we already have this file on disk
						fileFoundLocalF = False
						for extensionS in p["extensionSA"]:
							foundO["pathLocal"] = self.foldername+"/"+esc(ID+"_p"+str(pageSubI)+extensionS)
							if os.path.isfile(foundO["pathLocal"]):
								fileFoundLocalF = True
								break
						
						# stopOnFoundF stop condition
						if fileFoundLocalF and p["stopOnFoundF"]:
							ll(        userIDS      .rjust(9," ")+" userID"
								+" | "+str(pageI   ).rjust(3," ")+" page"
								+" | "+str(ID      ).rjust(9," ")+" illustID"
								+" | "+str(pageSubI).rjust(3," ")+" subpage"
								+" | "+("✕ download?" if fileFoundLocalF else "◯ download?")+""
								+" | "+foundO["pathLocal"].ljust(17," ")+""
								,("default" if fileFoundLocalF else "g"))
							# the finally block will take up our work after this point [not an actual return, just a break-all construct]
							return
						
						# try each file extension, on the first [and, should be, only] match, set fileFoundRemoteF to True and proceed
						fileFoundRemoteF = False
						for extensionS in p["extensionSA"]:
							foundO["extension"] = extensionS
							foundO["url"] = domain+"img-original/img/"+date+ID+"_p"+str(pageSubI)+extensionS
							foundO["pathLocal"] = self.foldername+"/"+esc(ID+"_p"+str(pageSubI)+extensionS)
							reqE = extractLinkData(foundO["url"],"HEAD",{},{"Referer":foundO["referer"],"Connection":"keep-alive",},returnFalseOnFailureF=True)
							if reqE != False:
								fileFoundRemoteF = True
								break
						# if page not found, we must have reached the end of the sub gallery [or unhandled filetype, in which case breaking here isn't great, but it's okay]
						if not fileFoundRemoteF:
							break
						
						ll(        userIDS      .rjust(9," ")+" userID"
							+" | "+str(pageI   ).rjust(3," ")+" page"
							+" | "+str(ID      ).rjust(9," ")+" illustID"
							+" | "+str(pageSubI).rjust(3," ")+" subpage"
							+" | "+("✕ download?" if fileFoundLocalF else "◯ download?")+""
							+" | "+foundO["pathLocal"].ljust(17," ")+""
							+" | "+foundO["url"]
							,("default" if fileFoundLocalF else "g"))
						
						if not fileFoundLocalF:
							imageEA.append({"url":foundO["url"],"referer":foundO["referer"],"pathLocal":foundO["pathLocal"]})
					# done with individual image
				# done with head images on current page
			# done with pages
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
# go in reverse, if the script gets interrupted, then when it's next executed, it won't [as-often] improperly trigger the stopOnFoundF flag
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
