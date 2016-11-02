# coding=utf-8
import threading
import urllib
import urllib2
import re
import os
import glob
import sys
import getopt

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
	sys.stdout.write("usage   : python pixivRoot.py [-t threadcount] [-T threadcount] [--disable-page] [--disable-subpage]"+os.linesep)
	sys.stdout.write("example : python pixivRoot.py --disable-page --disable-subpage"+os.linesep)
	sys.stdout.write("example : python pixivRoot.py -t 32 -T 16 --disable-subpage"+os.linesep)
	sys.stdout.write("-h                : display help information, which is what you're reading right now"+os.linesep)
	sys.stdout.write("--help            : display help information, which is what you're reading right now"+os.linesep)
	sys.stdout.write("--disable-page    : for each gallery, if you have the first subimage downloaded, it will"+os.linesep)
	sys.stdout.write("                    ignore the rest of the gallery - it will assume that you have those files already"+os.linesep)
	sys.stdout.write("                    this option is recommended unless you mess with your files manually"+os.linesep)
	sys.stdout.write("--disable-subpage : for each subgallery, if you have the first subimage downloaded, it will"+os.linesep)
	sys.stdout.write("                    ignore the rest of the subgallery - it will assume that you have those files already"+os.linesep)
	sys.stdout.write("                    this option is highly recommended unless you mess with your files manually"+os.linesep)
	sys.stdout.write("-t threadcount    : number of threads used to scan artist pages"+os.linesep)
	sys.stdout.write("                    type : integer | minimum : 1 | maximum : "+str(p["threadMaxC1"])+" | default : "+str(p["threadC1"])+os.linesep)
	sys.stdout.write("                    as you use more threads, your download rate and CPU usage will rise"+os.linesep)
	sys.stdout.write("                    out of courtesy toward pixiv, I recommend keeping threadcount relatively low"+os.linesep)
	sys.stdout.write("-T threadcount    : number of threads used to download images"+os.linesep)
	sys.stdout.write("                    type : integer | minimum : 1 | maximum : "+str(p["threadMaxC2"])+" | default : "+str(p["threadC2"])+os.linesep)
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
		else:fail(err)
	res = {"txt":response.read(),"txtHeader":str(response.info()),}
	response.close()
	return res
p = {
	"threadC1"        : 16,
	"threadMaxC1"     : 64,
	"threadC2"        : 8,
	"threadMaxC2"     : 64,
	"disablePageF"    : False,
	"disableSubpageF" : False,
	"emailS"          : "",
	"passwordS"       : "",
	"masterEntryA"    : [], # [{domain,date,ID},...]
	"userIDA"         : [],}
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
try:optA,leftoverA = getopt.getopt(sys.argv[1:],'ht:T:',['help','disable-page','disable-subpage'])
except getopt.GetoptError as err:printUsage();fail("ERROR : "+str(err))
for opt,arg in optA:
	if opt in ["-h","--help"]:printUsage();sys.exit()
	if opt in ["--disable-subpage"]:p["disableSubpageF"] = True
	if opt in ["--disable-page"   ]:p["disablePageF"   ] = True
	if opt in ["-t"]:
		try:p["threadC1"] = int(arg)
		except ValueError as err:fail("ERROR : [-t threadcount] argument not integer : "+arg)
		if p["threadC1"] <                1:fail("ERROR : [-t threadcount] argument too small (min:1) : "+arg)
		if p["threadC1"] > p["threadMaxC1"]:fail("ERROR : [-t threadcount] argument too large (max:"+str(p["threadMaxC1"])+") : "+arg)
	if opt in ["-T"]:
		try:p["threadC2"] = int(arg)
		except ValueError as err:fail("ERROR : [-T threadcount] argument not integer : "+arg)
		if p["threadC2"] <                1:fail("ERROR : [-T threadcount] argument too small (min:1) : "+arg)
		if p["threadC2"] > p["threadMaxC2"]:fail("ERROR : [-T threadcount] argument too large (max:"+str(p["threadMaxC2"])+") : "+arg)




# handle userIDA.txt
# ----------------------------------------------------------------------------------------------------------------------
assertFile("userIDA.txt")
txt = readFile("userIDA.txt")
# remove comments
txt = re.sub(re.compile('//.*$',re.MULTILINE),'',txt)
# parse for ints
userIDSA = re.split('\\D+',txt)
if len(userIDSA) == 0:fail("ERROR : Fill in your userIDA.txt file with pixiv userIDs")
for userIDS in userIDSA:
	if userIDS != "": # because of how the regex split that I wrote works, blanks may show up at the front and back
		p["userIDA"].append(int(userIDS))




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
threadLimiter_ArtistThread = threading.BoundedSemaphore(p["threadC1"])
class ArtistThread(threading.Thread):
	def __init__(self,userID=0):
		super(ArtistThread,self).__init__()
		self.userID = userID
		self.foldername = None
	def run(self):
		global p
		threadLimiter_ArtistThread.acquire()
		try:
			userIDS = str(self.userID)
			ll(userIDS.rjust(9," ")+" userID","m")
			pageI = 0 # initially incremented to 1
			while True:
				pageI += 1
				
				ll(userIDS.rjust(9," ")+" userID | "+str(pageI).rjust(3," ")+" page")
				
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
				m = re.findall('<img src="(https?:\/\/.+?\/).+?(\d{4}\/\d{2}\/\d{2}\/\d{2}\/\d{2}\/\d{2}\/)(\d+)_p(\d+).+?(\.[^\.]+)" class="_thumbnail">',reqE["txt"])
				# if we have image matches
				if m:
					tupleI = -1 # initially incremented to 0
					# for each image match
					for tuple in m:
						tupleI += 1
						domain    = tuple[0]
						date      = tuple[1]
						ID        = tuple[2]
						# for each page that could be covered [within a subgallery]
						pageSubI = -1 # initially incremented to 0
						while True:
							pageSubI += 1
							
							# try each file extension, on the first [and, should be, only] match, set fileFoundRemoteF to True and proceed
							# multithreaded, so there will be some unneeded work done, but the time savings make it worth doing this way
							# multithreaded execute
							passbackA = []
							tA = []
							for extension in [".jpg",".png",".gif"]:
								t = ExtensionScannerThread(url=domain+"img-original/img/"+date+ID+"_p"+str(pageSubI)+extension,referer="http://www.pixiv.net/member_illust.php?mode=medium&illust_id="+userIDS,extension=extension,passbackA=passbackA)
								t.start()
								tA.append(t)
							for t in tA:
								t.join()
							fileFoundRemoteF = len(passbackA) >= 1
							
							# if page not found, we must have reached the end of the sub gallery [or unhandled filetype, in which case breaking here isn't great, but it's okay]
							if not fileFoundRemoteF:break
							
							url       = passbackA[0]["url"]
							referer   = passbackA[0]["referer"]
							extension = passbackA[0]["extension"]
							filename  = esc(ID+"_p"+str(pageSubI)+extension)
							if (filename != ID+"_p"+str(pageSubI)+extension):fail("ERROR : filename changed after being cleansed [developer's fault - pixiv changed their url scheme]")
							
							# check if we already have this file on disk
							fileFoundLocalF = os.path.isfile(self.foldername+"/"+filename) # filename comes from the previous loop block dealing with remoteF HEAD requests
							
							ll(userIDS.rjust(9," ")+" userID | "+str(pageI).rjust(3," ")+" page | "+str(ID).rjust(9," ")+" illustID | "+str(pageSubI).rjust(3," ")+" subpage | "+("✕ download?" if fileFoundLocalF else "◯ download?")+" | "+self.foldername+"/"+filename,("default" if fileFoundLocalF else "g"))
							
							if fileFoundLocalF:
								# if we're on the first page, first image, first subimage, and --disable-page, and we already have this image downloaded,
								if pageI == 1 and tupleI == 0 and pageSubI == 0 and p["disablePageF"]:
									# assume that we have this entire gallery
									return # stop scanning this artist - the finally block will take up our work after this point [not an actual return, just a break-all construct]
								# if we're on the first subimage of any subgallery, and --disable-subpage, and we already have this image downloaded,
								elif pageSubI == 0 and p["disableSubpageF"]:
									# assume that we have this entire subgallery
									break # stop scanning this subgallery
								else:
									pass # normal-mode, check remaining subgallery images
							else:
								p["masterEntryA"].append({"url":url,"referer":referer,"filename":self.foldername+"/"+filename})
				else:
					break
		finally:
			threadLimiter_ArtistThread.release()

class ExtensionScannerThread(threading.Thread):
	def __init__(self,url="",referer="",extension="",passbackA=None):
		super(ExtensionScannerThread,self).__init__()
		self.url       = url
		self.referer   = referer
		self.extension = extension
		self.passbackA = passbackA
	def run(self):
		try:
			reqE = extractLinkData(self.url,"HEAD",{},{"Referer":self.referer,"Connection":"keep-alive",},returnFalseOnFailureF=True)
			if reqE != False:
				self.passbackA.append({"url":self.url,"referer":self.referer,"extension":self.extension,})
		finally:
			pass

# multithreaded execute
tA = []
for userID in p["userIDA"]:
	t = ArtistThread(userID=userID)
	t.start()
	tA.append(t)
for t in tA:
	t.join()




# download each image
# ----------------------------------------------------------------------------------------------------------------------
threadLimiter_MasterEntryThread = threading.BoundedSemaphore(p["threadC2"])
class MasterEntryThread(threading.Thread):
	def __init__(self,url="",referer="",filename=""):
		super(MasterEntryThread,self).__init__()
		self.url      = url
		self.referer  = referer
		self.filename = filename
	def run(self):
		threadLimiter_MasterEntryThread.acquire()
		try:
			ll("△","gray",noLineBreakF=True)
			reqE = extractLinkData(self.url,"GET",{},{"Referer":self.referer,"Connection":"keep-alive",})
			text_file = open(self.filename,"w")
			text_file.write(reqE["txt"])
			text_file.close()
		finally:
			ll("◯","g",noLineBreakF=True)
			threadLimiter_MasterEntryThread.release()

ll("Downloading "+str(len(p["masterEntryA"]))+" images...","m")

# multithreaded execute
tA = []
for masterEntry in reversed(p["masterEntryA"]): # go in reverse, if the script gets interrupted, then when it's next executed, it won't improperly trigger the --disable flags
	t = MasterEntryThread(url=masterEntry["url"],referer=masterEntry["referer"],filename=masterEntry["filename"])
	t.start()
	tA.append(t)
for t in tA:
	t.join()




ll(os.linesep+"END","c")
