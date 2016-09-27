# PixivMediaScraper  
Keeps a local folder tree of your favorite pixiv artists' works, quickly gets newly posted works [with a little manual labor].
  
Required:  
L> Web browser  
L> Access to [pixiv.net](pixiv.net)  
L> A pixiv account  
L> One of the following:  
L> L> Apple OS and ability to use the command-line [link to instructions provided]  
L> L> [PENDING] Windows and ability to use the command-line [link to instructions provided]  
  
Personal walkthrough  
On my computer, I have a folder named "pixivRoot". Inside are two folders and one text file. The folders are named "杏仁無双#161519" and "上倉エク#299299", and they contain all of those artists' works that they've posted to pixiv. The text file has two lines and looks like this:  
"  
161519  
299299  
"  
Those are the pixiv userIDs of those two artists. If I find a new artist that I like, I'll add their pixiv userID to this list on another line. Finding pixiv userIDs is easy, it's the number in the URL of their profile/works page, such as "http://www.pixiv.net/member_illust.php?id=161519" being a pixiv userID of 161519. Every day or so, I'll open pixiv, load up my JavaScript script, run it, and use the generated command script to keep my pixiv folder updated. I can then look at the "Date Modified" dates for the folders and files to see which artists have posted new works.  
  
Downloading the images  
(1) Navigate anywhere on pixiv.net and be signed in.  
(2) Open your browser's JavaScript Console for that page.  
(3) Paste in the text from pixivScrape.js and run it. You will see a large description box placed at the bottom of the page. Follow the instructions written there, which go something like "drag&drop your pixiv userID file on the Choose File button, verify that the contents are correct, then hit the download button".  
(4 [Apple OS command-line w/sh]) After the scraper is done, it will download a .txt file that has a bunch of command-line commands in it. Move this file to your pixiv root/home folder, which is the folder that will contain all the subfolders for each artist. Navigate to that folder from the command-line and run  
sh pixivDownloadUpdateScript.txt  
Doing this will run those commands in that pixiv root/home folder that you should be in. Now just wait and watch the script progress. When it's done, all your images should be in that folder. If you already have most of the images downloaded from previous runs, the download process should be quick.  
(4 [Windows command-line]) [PENDING\]  
(5) Notice that the script that you downloaded deleted itself when it finished. That script only corresponds to a file list at the time of running. When you update your pixiv folder in the future, you'll need to re-run the JavaScript code each time.  
  
[see the JavaScript Console Help section of [https://github.com/sliceofcake/TechnicalHelp](https://github.com/sliceofcake/TechnicalHelp)]  
[see the Command-Line Help section of [https://github.com/sliceofcake/TechnicalHelp](https://github.com/sliceofcake/TechnicalHelp)]  
  
Use case  
There are some artists that I follow on Twitter. It seems like those artists upload about the same set of images to pixiv at roughly the same time [though sometimes one platform will be missing certain works, whether by the artist's intention or accident]. Pixiv images tend to be of higher quality than ones on Twitter. Pixiv, however, requires even more clicks than Twitter does to reach the "original"-resolution images to download, and has a strange system that won't let you just hop to the final link to download it directly [they look at the HTTP referer header, which is spoofable]. I like these artists, I like their art, but I don't want to sit there for hours jumping through Pixiv's interface hoops to get the artist's images. I made this scraper to automate the difficult part of the "download all images by this artist" process.  
  
Notes  
• This script will never delete images. You may accumulate images that the artist has deleted, in which case you will have more images on your computer than are available on pixiv for that artist. This is intended behavior.  
• The command-line script throttles downloads to four-at-a-time, in stop-go parallel. The stop-go parallel part is just because I don't know how to have rolling parallel, but the four-at-a-time part is out of some bizarre notion of courtesy toward pixiv staff. I may raise the limit in the future, but for now, four-at-a-time seems good enough, while not potentially being a bandwidth hog toward pixiv. There's a chance that pixiv is large enough that a usual at-home person would never be a bother bandwidth-wise, but I don't feel comfortable upping the limiter yet.  
• A username with forward slashes "/" or backslashes "\" in it will have them all replaced with a pipe "|". A username with double straight quotes will have them all replaced with two single straight quotes in succession. This is to follow cross- Operating System naming conventions.  
  
Everything that could go wrong, within reason  
• The scraper never finishes : There's a chance that pixiv will change their interface enough to break the scraper. I expect something like this eventually, and if you post an "Issue" about it here on GitHub, we can work together to try to fix this scraper.  
• The files won't download : It's possible that pixiv changed their link format. Post an "Issue" about it here on GitHub and we can work together to try to fix this scraper.  