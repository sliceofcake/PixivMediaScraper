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

class cliColor:
	HEADER    = '\033[95m'
	OKBLUE    = '\033[94m'
	OKGREEN   = '\033[92m'
	WARNING   = '\033[93m'
	FAIL      = '\033[91m'
	END       = '\033[0m'
	BOLD      = '\033[1m'
	UNDERLINE = '\033[4m'
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
def usage():
	global arg_threadC1
	global arg_threadMaxC1
	global arg_threadC2
	global arg_threadMaxC2
	print "usage  : python pixivRoot.py [-t threadcount] [-T threadcount] [--disable-subpage]"
	print "example: python pixivRoot.py --disable-subpage"
	print "example: python pixivRoot.py -t 32 -T 16 --disable-subpage"
	print "-h                : display help information, which is what you're reading right now"
	print "--help            : display help information, which is what you're reading right now"
	print "--disable-page    : for each gallery, if you have the first image downloaded, it will"
	print "                    ignore the rest of the gallery - it will assume that you have those files already"
	print "                    this option is recommended unless you mess with your files manually"
	print "--disable-subpage : for each subgallery, if you have the first subimage downloaded, it will"
	print "                    ignore the rest of the subgallery - it will assume that you have those files already"
	print "                    this option is highly recommended unless you mess with your files manually"
	print "-t threadcount    : number of threads used to scan artist pages"
	print "                    type : integer | minimum : 1 | maximum : "+str(arg_threadMaxC1)+" | default : "+str(arg_threadC1)
	print "                    as you use more threads, your download rate and CPU usage will rise"
	print "                    out of courtesy toward pixiv, I recommend keeping threadcount relatively low"
	print "-T threadcount    : number of threads used to download images"
	print "                    type : integer | minimum : 1 | maximum : "+str(arg_threadMaxC2)+" | default : "+str(arg_threadC2)
	print "                    as you use more threads, your download rate and CPU usage will rise"
	print "                    out of courtesy toward pixiv, I recommend keeping threadcount relatively low"
def printThreadSafe(m,noLineBreakF=False):
	s = str(m)
	sys.stdout.write(s+("" if noLineBreakF else "\n"))
	sys.stdout.flush()




print cliColor.OKBLUE + "START" + cliColor.END
arg_threadC1    = 16
arg_threadMaxC1 = 256
arg_threadC2    = 16
arg_threadMaxC2 = 64
arg_disablePage = False
arg_disableSubpage = False
arg_email = ""
arg_password = ""
try:
	optA,leftoverA = getopt.getopt(sys.argv[1:],'ht:T:',['help','disable-page','disable-subpage'])
except getopt.GetoptError,err:
	print cliColor.FAIL + str(err) + cliColor.END
	usage()
	sys.exit()
for opt,arg in optA:
	if opt in ["-h","--help"]:
		usage()
		sys.exit()
	if opt in ["--disable-subpage"]:
		arg_disableSubpage = True
	if opt in ["--disable-page"]:
		arg_disablePage = True
	if opt in ["-t"]:
		try:
			arg_threadC1 = int(arg)
		except ValueError as err:
			print cliColor.FAIL + "[-t threadcount] argument not integer : "+arg + cliColor.END
			sys.exit()
		if arg_threadC1 < 1:
			print cliColor.FAIL + "[-t threadcount] argument too small (min:1) : "+arg + cliColor.END
			sys.exit()
		if arg_threadC1 > arg_threadMaxC1:
			print cliColor.FAIL + "[-t threadcount] argument too large (max:"+str(arg_threadMaxC1)+") : "+arg + cliColor.END
			sys.exit()
	if opt in ["-T"]:
		try:
			arg_threadC2 = int(arg)
		except ValueError as err:
			print cliColor.FAIL + "[-T threadcount] argument not integer : "+arg + cliColor.END
			sys.exit()
		if arg_threadC2 < 1:
			print cliColor.FAIL + "[-T threadcount] argument too small (min:1) : "+arg + cliColor.END
			sys.exit()
		if arg_threadC2 > arg_threadMaxC2:
			print cliColor.FAIL + "[-T threadcount] argument too large (max:"+str(arg_threadMaxC2)+") : "+arg + cliColor.END
			sys.exit()
print cliColor.WARNING+"To stop this program, use Control+Z for Apple Operating Systems."+cliColor.END




#
masterEntryA = [] # domain, date, ID
userIDA = []
if os.path.isfile("userIDA.txt"):
	file = open("userIDA.txt","r")
	txt = file.read()
	file.close()
	# remove comments
	txt = re.sub(re.compile('//.*$',re.MULTILINE),'',txt)
	# parse for ints
	userIDSA = re.split('\\D+',txt)
	for userIDS in userIDSA:
		if userIDS == "":
			continue
		userID = int(userIDS)
		userIDA.append(userID)
else:
	print cliColor.FAIL + "ERROR : Fill in your userIDA.txt file with pixiv userIDs" + cliColor.END
	file = open("userIDA.txt","w")
	file.write("")
	file.close()
	sys.exit()
if os.path.isfile("login.txt"):
	file = open("login.txt","r")
	txt = file.read()
	file.close()
	# remove comments
	txtA = txt.splitlines()
	if len(txtA) < 2:
		print cliColor.FAIL + "ERROR : malformed login.txt, there should be two lines, first is email address, second is password" + cliColor.END
		sys.exit()
	else:
		arg_email = txtA[0]
		arg_password = txtA[1]
else:
	print cliColor.FAIL + "ERROR : Fill in your login.txt file with email on first line, password on second line" + cliColor.END
	file = open("login.txt","w")
	file.write("")
	file.close()
	sys.exit()
print "userID List : "+str(userIDA)




# open the logic page
response = urllib2.urlopen("https://accounts.pixiv.net/login")




# get the callback key, there are two places to find it, I chose the JSON method
#<input type="hidden" name="post_key" value="4d0dc83acbe2f27ba139be1559c4455d">
#"pixivAccount.postKey":"4d0dc83acbe2f27ba139be1559c4455d"
m = re.search('"pixivAccount\.postKey":"(.+?)"',response.read())
if not m:
	print cliColor.FAIL + "ERROR : could not find login callback key [developer's fault - pixiv changed their login page format]" + cliColor.END
	sys.exit()
postKey = m.group(1)
print "postKey GET!! : "+postKey




# get the callback cookie from the header
m = re.search('PHPSESSID=(.+?);',str(response.info()))
if not m:
	print cliColor.FAIL + "ERROR : could not find login callback cookie [developer's fault - pixiv changed their login page format]" + cliColor.END
	sys.exit()
PHPSessionID = m.group(1)
print "PHPSessionID GET!! : "+PHPSessionID
response.close()




# make the signin request
headerL = {
	#"Accept":"application/json, text/javascript, */*; q=0.01",
	#"Accept-Encoding":"gzip, deflate, br",
	#"Accept-Language":"en-US,en;q=0.8,ja;q=0.6",
	"Connection":"keep-alive",
	#"Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
	#"Host":"accounts.pixiv.net",
	#"Origin":"https://accounts.pixiv.net",
	#"Referer":"https://accounts.pixiv.net/login",
	#"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
	#"X-Requested-With":"XMLHttpRequest",
	#"Cookie":"PHPSESSID=edaf093e83141c96c5069320388424fd; p_ab_id=1; __utmt=1; __utma=235335808.1632334662.1477690916.1477690916.1477690916.1; __utmb=235335808.1.10.1477690916; __utmc=235335808; __utmz=235335808.1477690916.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmv=235335808.|2=login%20ever=no=1; _gat=1; _gat_UA-76252338-4=1; _ga=GA1.2.1632334662.1477690916; _ga=GA1.3.1632334662.1477690916",
	"Cookie":"PHPSESSID="+PHPSessionID,}
dataL = urllib.urlencode({
	"pixiv_id":arg_email,
	"password":arg_password,
	"captcha":"",
	"g_recaptcha_response":"",
	"post_key":postKey,
	"source":"accounts",})
req = urllib2.Request("https://accounts.pixiv.net/api/login?lang=en",dataL,headerL)
#req = urllib2.Request("https://feelthebeats.se/575/lab/reflect.php",dataL,headerL)
try:
	response = urllib2.urlopen(req)
except urllib2.HTTPError as err:
	print err.code
	print err
	sys.exit()
print response.read()




# get the newest cookie before we proceed
m = re.search('PHPSESSID=(.+?);',str(response.info()))
if not m:
	print cliColor.FAIL + "ERROR : could not find login response cookie [either -> your fault - invalid signin information OR developer's fault - pixiv changed their login page format]" + cliColor.END
	sys.exit()
PHPSessionID = m.group(1)
print "PHPSessionID GET!! : "+PHPSessionID
response.close()




# !!! HERE - alter the multithreaded functions to be more input-output rigid. (1) fill masterEntryA (2) download all from masterEntryA
maxThreadC_ArtistThread = arg_threadC1
threadLimiter_ArtistThread = threading.BoundedSemaphore(maxThreadC_ArtistThread)
class ArtistThread(threading.Thread):
	def __init__(self,userID=0):
		super(ArtistThread,self).__init__()
		self.userID = userID
		self.foldername = None
	def run(self):
		global masterEntryA
		global esc
		global arg_disablePage
		global arg_disableSubpage
		threadLimiter_ArtistThread.acquire()
		try:
			userIDS = str(self.userID)
			printThreadSafe(cliColor.OKBLUE + userIDS.rjust(9," ")+" userID" + cliColor.END)
			pageI = 0 # initially incremented to 1
			while True:
				pageI += 1
				
				printThreadSafe(userIDS.rjust(9," ")+" userID | "+str(pageI).rjust(3," ")+" page")
				
				# make the page request
				req = urllib2.Request("http://www.pixiv.net/member_illust.php?id="+userIDS+"&type=all&p="+str(pageI),None,{"Cookie":"PHPSESSID="+PHPSessionID,"Connection":"keep-alive",})
				try:
					# success, proceed
					response = urllib2.urlopen(req)
					txt = response.read()
					response.close()
				except urllib2.HTTPError as err:
					# failure, stop here, not this page nor further pages
					printThreadSafe(err.code)
					printThreadSafe(err)
					printThreadSafe(cliColor.FAIL + "ERROR : HTTP errorcode encountered" + cliColor.END)
					sys.exit()
				
				# ensure we're looking at a valid, signed-in page, if not, stop the entire program
				m = re.search('Welcome to pixiv',txt)
				if m:
					printThreadSafe(cliColor.FAIL + "ERROR : the signin failed [developer's fault - pixiv changed their artist page format]" + cliColor.END)
					sys.exit()
				
				# get the username on the first round
				if self.foldername == None:
					m = re.search('<h1 class="user">(.+?)</h1>',txt);
					if m:
						username = m.group(1)
						compoundUsername = username+"#"+userIDS
					else:
						printThreadSafe("WARNING : could not find username on page - falling back to solely userID [developer's fault - pixiv changed their artist page format]")
						compoundUsername = "#"+userIDS
					self.foldername = esc(compoundUsername)
					wildname = "*"+esc("#"+userIDS) # wildcard not escaped, used explicitly as wildcard
					assertFolder(foldername=self.foldername,wildname=wildname)
				
				# get image links on this page
				# "referer: http://www.pixiv.net/member_illust.php?mode=medium&illust_id=56278541" "http://i2.pixiv.net/img-original/img/2016/04/10/00/00/04/56278541_p0.jpg" -o "USERNAME#299299/56278541_p0.jpg"
				#function(match,domain,date,ID,page,extension,offset,string){link = domain+"img-original/img/"+date+ID+"_p"+page+extension;}
				#<img src="http://i4.pixiv.net/c/150x150/img-master/img/2016/10/17/00/00/07/59506543_p0_master1200.jpg" class="_thumbnail">
				m = re.findall('<img src="(https?:\/\/.+?\/).+?(\d{4}\/\d{2}\/\d{2}\/\d{2}\/\d{2}\/\d{2}\/)(\d+)_p(\d+).+?(\.[^\.]+)" class="_thumbnail">',txt)
				# if we have image matches
				if m:
					# for each image match
					for tuple in m:
						domain    = tuple[0]
						date      = tuple[1]
						ID        = tuple[2]
						# for each page that could be covered [within a subgallery]
						pageSubI = -1 # initially incremented to 0
						while True:
							pageSubI += 1
							
							# try each file extension, on the first [and, should be, only] match, set fileFoundRemoteF to True and proceed
							fileFoundRemoteF = False
							for extension in [".jpg",".png",".gif"]: # this order is intentional, it's the frequency ranking for file extensions, starting with most common
								url = domain+"img-original/img/"+date+ID+"_p"+str(pageSubI)+extension # used later, so stored here in a variable
								referer = "http://www.pixiv.net/member_illust.php?mode=medium&illust_id="+userIDS # used later, so stored here in a variable
								req = urllib2.Request(url,None,{"Referer":referer,"Connection":"keep-alive",})
								req.get_method = lambda : "HEAD"
								try:
									response = urllib2.urlopen(req)
									if (ID+"_p"+str(pageSubI)+extension) != esc(ID+"_p"+str(pageSubI)+extension):
										printThreadSafe(cliColor.FAIL + "ERROR : filename changed after being cleansed [developer's fault - pixiv changed their url scheme]" + cliColor.END)
										sys.exit()
									filename = esc(ID+"_p"+str(pageSubI)+extension)
									fileFoundRemoteF = True
									response.close()
									break
								except urllib2.HTTPError as err:
									continue
							
							# if page not found, we must have reached the end of the sub gallery [or unhandled filetype, in which case breaking here isn't great, but it's okay]
							if not fileFoundRemoteF:
								break
							
							# check if we already have this file on disk
							fileFoundLocalF = os.path.isfile(self.foldername+"/"+filename) # filename comes from the previous loop block dealing with remoteF HEAD requests
							
							printThreadSafe(("" if fileFoundLocalF else cliColor.OKGREEN)+userIDS.rjust(9," ")+" userID | "+str(pageI).rjust(3," ")+" page | "+str(ID).rjust(9," ")+" illustID | "+str(pageSubI).rjust(3," ")+" subpage | "+("✕ download?" if fileFoundLocalF else "◯ download?")+" | "+self.foldername+"/"+filename+("" if fileFoundLocalF else cliColor.END))
							
							if fileFoundLocalF:
								if pageI == 1 and pageSubI == 0 and arg_disablePage:
									# assume that we have this entire gallery
									return # the finally block will take up our work after this point [not an actual return, just a break-all construct]
								elif pageSubI == 0 and arg_disableSubpage:
									# assume that we have this entire subgallery
									break
								else:
									# normal-mode, check remaining subgallery images
									pass
							else:
								masterEntryA.append({"url":url,"referer":referer,"filename":self.foldername+"/"+filename})
				else:
					break
		finally:
			threadLimiter_ArtistThread.release()

maxThreadC_MasterEntryThread = arg_threadC2
threadLimiter_MasterEntryThread = threading.BoundedSemaphore(maxThreadC_MasterEntryThread)
class MasterEntryThread(threading.Thread):
	def __init__(self,url="",referer="",filename=""):
		super(MasterEntryThread,self).__init__()
		self.url      = url
		self.referer  = referer
		self.filename = filename
	def run(self):
		threadLimiter_MasterEntryThread.acquire()
		try:
			printThreadSafe("△",True)
			req = urllib2.Request(self.url,None,{"Referer":self.referer,"Connection":"keep-alive",})
			try:
				response = urllib2.urlopen(req)
			except urllib2.HTTPError as err:
				printThreadSafe(err.code)
				printThreadSafe(err)
				printThreadSafe(cliColor.FAIL + "ERROR : HTTP errorcode encountered" + cliColor.END)
				sys.exit()
			text_file = open(self.filename,"w")
			text_file.write(response.read())
			text_file.close()
		finally:
			printThreadSafe(cliColor.OKGREEN+"◯"+cliColor.END,True)
			threadLimiter_MasterEntryThread.release()

# multithreaded load each artist
tA = []
for userID in userIDA:
	t = ArtistThread(userID=userID)
	t.start()
	tA.append(t)
for t in tA:
	t.join()

printThreadSafe("Downloading "+str(len(masterEntryA))+" images...")

# multithreaded save each image
tA = []
for masterEntry in masterEntryA:
	t = MasterEntryThread(url=masterEntry["url"],referer=masterEntry["referer"],filename=masterEntry["filename"])
	t.start()
	tA.append(t)
for t in tA:
	t.join()



print "\n" + cliColor.OKBLUE + "END" + cliColor.END
