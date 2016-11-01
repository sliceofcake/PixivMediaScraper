# PixivMediaScraper  
Keeps a local folder tree of your favorite pixiv artists' works, quickly gets newly posted works. It's a Python script.  
  
Required:  
L> A pixiv account  
L> One of the following:  
L> L> Apple OS [comes with python installed] and ability to use the command-line [link to instructions provided]  
L> L> [PENDING] Windows and ability to use the command-line [link to instructions provided]  
  
Recommended:  
L> A web browser - in case you need to resolve any login issues [pixiv may occasionally ask you to complete a captcha, which you can only do on their actual login page through a web browser]  
  
Personal walkthrough  
First of all, you will find more information by running this python script with the help flag. That's `python pixivRoot.py --help`.  
  
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
This software needs your pixiv account login information because you can't scrape pixiv without an account. If you don't feel comfortable putting your email and password in a text file like this, just make a new account that you use only with this software [that's what I even do, and I wrote this software!].  
  
userIDA.txt looks like this:  
```  
161519  
299299  
  
// found on twitter, but can't find on pixiv  
// supermusou1110  
```  
Those are the pixiv userIDs of those two artists, one per line. I keep them in order to make it easy for me to add to and remove from the list. Finding pixiv userIDs for artists is easy: it's the number in the URL of their profile/works page, such as `http://www.pixiv.net/member_illust.php?id=161519` being a pixiv userID of `161519`.  
  
Every day, I'll open up Terminal, navigate to my pixivRoot folder and run pixivRoot.py there to keep my pixiv folder updated. I can then look at the "Date Modified" dates for the folders and files to see which artists have posted new works. Occasionally, I'll use my pixivRoot folder with an image viewing application to randomly view images that I've downloaded.  
  
[for the next section, you may want to look at the Command-Line Help section of [https://github.com/sliceofcake/TechnicalHelp](https://github.com/sliceofcake/TechnicalHelp)]  
  
Downloading the images  
(1) Open your command line interface application [called Terminal in Apple OSs].  
(2) Navigate to your pixivRoot folder [you don't have to name it that].  
(3 [Apple command-line]) Run pixivRoot.py. The recommended configuration is `python pixivRoot.py --disable-page --disable-subpage`. Now just wait and watch the script progress [or walk away and do other things while it runs]. When it's done, all your images should be in that pixivRoot folder. If you already have most of the images downloaded from previous runs, the download process should be quick. The first time you run it, it could take a very long time, since it'll have to download all the images. Also, the first time you run it, you probably won't have a userIDA.txt or login.txt unless you made one ahead of time after reading this readme file. If you run pixivRoot.py without those file, the script will automatically make them for you. They'll be blank and the script will print a message asking you to fill them in.  
(3 [Windows command-line]) [PENDING\]  
  
Use case  
I enjoy seeing the art of many pixiv artists, but I'd like their images on my computer, so I can view them quickly and feed them into fancy image viewer software [and also view them even when I don't have an internet connection]. I can download pixiv art on my own with my web browser, but it's an extremely slow process, and keeping my folders updated manually would take way too much time out of my days.  
  
Notes  
• This script will never delete images. You may accumulate images that the artist has deleted, in which case you will have more images on your computer than are available on pixiv for that artist. This is intended behavior.  
• This software throttles network requests for two reasons: your network connection may not perform well under high stress and pixiv may not appreciate you making such requests. Everyone has different circumstances though, so I let you decide, within some boundaries, how many simultaneous request-threads you want to support [through command-line option flags].  
• These pixiv artist just seem to love throwing all sorts of characters into their usernames. It turns out that the shell environment is rather hostile to user input sanitization. To keep everyone happy, the following replacements are executed on usernames:  
\ -> ＼ [path character in Windows]  
/ -> ／ [path character in UNIX]  
" -> ” [string scoping]  
' -> ’ [string scoping]  
\* -> ＊ [wildcard]  
$ -> ＄ [variable reference]  
. -> 。 (only in cases of lone "." and lone "..") [path navigation]  
I have a bad feeling this may not cover every case. I hope that this is a good attempt at preventing pixiv usernames from doing anything unexpected.  
• Wherever you have two forward slashes together in your userID text file, those slashes and everything after them until the end of the line will be ignored by the parser. For example, the following line can be in your userID text file:  
```  
299299 // @ekureea on twitter  
// !!! HERE check if @ekureea has posted any twitter-exclusive artwork  
```  
and you won't have to worry about the parser accidentally extracting an unintended userID from the part that you intended to just be a note/comment for yourself.  
  
----  
  
Informal Benchmark Testing The Impact Of Performance Flags On Completion Time  
  
The setup  
29 October 2016  
86 Artists  
15119 images  
All downloaded ahead of time [only the scanner will run, and it will always result in no changes - if you run this script daily, this is a near-typical use case, since you'll already have most of the images downloaded].  
  
The results  
[00m:10s] : python pixivRoot.py -t 16 -T 16 --disable-page --disable-subpage  
[00m:10s] : python pixivRoot.py -t 16 -T 16 --disable-page  
[04m:31s] : python pixivRoot.py -t 16 -T 16 --disable-subpage  
[20m:30s] : python pixivRoot.py -t 16 -T 16  
  
Using the results to inform your decisions  
Unless you are going around deleting and moving files in your pixivRoot [which I don't recommend that you do], you should definitely be using the --disable-subpage flag every time. You should probably also use the --disable-page flag.  
Infrequently, you should run this software without either of those flags, to make absolutely certain that you've downloaded everything. For me, I run this lightly once per day, so I might be running this without any flags once per month, or maybe once per week to see how well I wrote this software [and fix any issues if I see any]. For you, "infrequently" may mean a different time range. "Why would I ever have to run this without those flags?" -> if the script is ever interrupted, it may have only downloaded some of the images, but enough to trip up the script the next time you run it : it may be erroneously gated because it's assumptions have been violated, mainly the assumption that each time it runs, it completes successfully.  
  
----  
  
Everything that could go wrong, within reason  
• The scraper never finishes : There's a chance that pixiv will change their interface enough to break the scraper. I expect something like this eventually, and if you post an "Issue" about it here on GitHub, we can work together to try to fix this scraper.  
• The files won't download : It's possible that pixiv changed their link format. Post an "Issue" about it here on GitHub and we can work together to try to fix this scraper.  
• The script slows down at the end : This should be expected. It's slowing down because you aren't using all of the specified threads at the end. Imagine you have a work queue of 100 jobs and you process 10 at a time [and the jobs finish at different times]. At the end, you will likely have fewer than 10 jobs running, so it'll feel slower.  