# PixivMediaScraper  
Keeps a local folder tree of your favorite pixiv artists' works, quickly gets newly posted works. [Python2] [Mac OS X]  
  
Required:  
L> A pixiv account  
L> One of the following:  
L> L> Apple OS [comes with python installed] and ability to use the command-line [link to instructions provided]  
L> L> [PENDING] Windows and ability to use the command-line [link to instructions provided]  
  
tl;dr How To Use  
(1) Make sure you have Python2 installed.  
(2) Make a folder that you'll use with this program (to store pixiv images)  
(3) Place pixivRoot.py in that folder  
(4) Execute pixivRoot.py from the command line (`python pixivRoot.py`). You'll be prompted to fill out the generated login.txt. Do that (follow the instructions that displayed).  
(5) Execute pixivRoot.py again (`python pixivRoot.py`). You'll be prompted to fill out the generated userIDA.txt. Do that (follow the instructions that displayed).  
(6) Execute pixivRoot.py once more. It should start scanning then eventually downloading images posted by your specified artists. The images get placed in the same folder as pixivRoot.py.  
(*) At any point in the future, execute pixivRoot.py to update your folders. Only new, undownloaded images will be downloaded.  
  
Personal walkthrough  
First of all, you will find more information by running this python script with the help flag (`python pixivRoot.py --help`).  
  
On my computer, I have the following folder/file structure:  
```  
pixivRoot  
L> login.txt  
L> userIDA.txt  
L> pixivRoot.py  
L> 杏仁無双#161519  
   L> 53185824_p0.jpg  
   L> 58784374_p0.jpg  
   L> ...  
L> 上倉エク#299299  
   L> 50025227_p0.jpg  
   L> 50832311_p0.jpg  
   L> ...  
```  
  
login.txt looks like this:  
```  
sliceofcake@example.com  
secretstrawberrycake  
```  
This software needs your pixiv account login information because you can't scrape pixiv without an account. If you don't feel comfortable putting your email and password in a text file like this (you shouldn't feel comfortable doing such a thing!), just make a new account that you use only with this software.  
  
userIDA.txt looks like this:  
```  
161519  
299299  
  
// found on twitter, but can't find on pixiv  
// supermusou1110  
```  
Those are the pixiv userIDs of those two artists, one per line [everything after a double-slash, include the slashes, will be ignored by this software, so you can use that to write notes for yourself if you want]. I keep them in order to make it easy for me to add to and remove from the list. Finding pixiv userIDs for artists is easy: it's the number in the URL of their profile/works page, such as `http://www.pixiv.net/member_illust.php?id=161519` being a pixiv userID of `161519`.  
  
Every day, I'll open up Terminal, navigate to my pixivRoot folder and run pixivRoot.py there to keep my pixiv folder updated. I can then look at the "Date Modified" dates for the folders and files to see which artists have posted new works.  
  
[for the next section, you may want to look at the Command-Line Help section of [https://github.com/sliceofcake/TechnicalHelp](https://github.com/sliceofcake/TechnicalHelp)]  
  
Notes  
• This script will never delete images. You may accumulate images that the artist has deleted, in which case you will have more images on your computer than are available on pixiv for that artist. This is intended behavior.  
• This software throttles network requests for two reasons: your network connection may not perform well under high stress and pixiv may not appreciate you making such requests. Everyone has different circumstances though, so I let you decide, within some boundaries, how many simultaneous request-threads you want to support [through command-line option flags].  
• Remember to unlock all age restrictions on your account in order to ensure that you're downloading everything - by default when you make a new account, R18 works may be hidden.  
• These pixiv artists just seem to love throwing all sorts of characters into their usernames. It turns out that the shell environment is rather hostile to user input sanitization. To keep everyone happy, the following replacements are executed on usernames:  
\ -> ＼ [path character in Windows]  
/ -> ／ [path character in UNIX]  
" -> ” [string scoping]  
' -> ’ [string scoping]  
\* -> ＊ [wildcard]  
$ -> ＄ [variable reference]  
: -> ： [special filename character in Apple OSs]  
. -> 。 (only in cases of lone "." and lone "..") [path navigation]  
I have a bad feeling this may not cover every case. I hope that this is a good attempt at preventing pixiv usernames from doing anything unexpected.  
• Wherever you have two forward slashes together in your userID text file, those slashes and everything after them until the end of the line will be ignored by the parser. For example, the following lines can be in your userIDA.txt file:  
```  
299299 // @ekureea on twitter  
// !!! HERE check if @ekureea has posted any twitter-exclusive artwork  
```  
and you won't have to worry about the parser accidentally extracting an unintended userID from the part that you intended to just be a note/comment for yourself.  
  
----  
  
Everything that could go wrong, within reason  
• The scraper never finishes : There's a chance that pixiv will change their interface enough to break the scraper. I expect something like this eventually, and if you post an "Issue" about it here on GitHub, we can work together to try to fix this scraper.  
• The files won't download : It's possible that pixiv changed their link format. Post an "Issue" about it here on GitHub and we can work together to try to fix this scraper.  
• The script slows down at the end : This should be expected. It's slowing down because you aren't using all of the specified threads at the end. Imagine you have a work queue of 100 jobs and you process 10 at a time [and the jobs finish at different times]. At the end, you will have 10 then 9 then 8 then 7 ... then 1 job remaining, so it'll feel slower.  
• The script never proceeds beyond the sign-in steps : Pixiv may have changed their sign-in details. There may be another problem though, try signing in your account with a web browser to make sure there aren't any captchas or anything that you need to fill out for some reason.  