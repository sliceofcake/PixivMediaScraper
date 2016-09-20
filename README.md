# PixivMediaScraper  
For downloading all of a particular Pixiv user's media, specifically static images.  
  
Required:  
L> Web browser  
L> Access to [pixiv.net](pixiv.net)  
L> A pixiv account  
L> One of the following:  
L> L> Apple OS and ability to use the command-line [link to instructions provided]  
L> L> [PENDING] Windows and ability to use the command-line [link to instructions provided]  
  
Downloading the images  
(1) Navigate to the pixiv user's 作品 > 総合 feed, such as http://www.pixiv.net/member_illust.php?id=[[[USERID_HERE]]]  
(2) Open your browser's JavaScript Console for that page.  
(3) Paste in the text from pixivScrape.js and run it. You will see a large description box placed at the bottom of the page. Read through it, and eventually click the relevant link/button to run the scraper, once you're ready.  
(4 [Apple OS command-line]) After the scraper is done, it will download a .txt file that has a bunch of command-line commands in it. I recommend moving this file to the folder you want the images to go, then navigating to that folder from the command-line and running  
sh pixivUser######CurlScript.txt  
after you've replaced that dummy filename with the actual name of the file that downloaded. Doing this will run those commands in the folder that you want the images to go into. Now just wait and watch the script progress. When it's done, all your images should be in that folder.  
(4 [Windows command-line]) [PENDING\]  
(5) I recommend that, after all your images have downloaded, you delete the script that was downloaded through the pixiv page. That script will only be for the exact set of images that you just downloaded. If the pixiv user uploads or deletes any of their images, the script file will not reflect that change. You should always run the scraper immediately before downloading the images, and preferably, only partially joking, when the artist is asleep and not making changes to their page.  
  
[see the JavaScript Console Help section of [https://github.com/sliceofcake/TechnicalHelp](https://github.com/sliceofcake/TechnicalHelp)]  
[see the Command-Line Help section of [https://github.com/sliceofcake/TechnicalHelp](https://github.com/sliceofcake/TechnicalHelp)]  
  
Use case  
There are some artists that I follow on Twitter. It seems like those artists upload about the same set of images to pixiv at roughly the same time [though sometimes one platform will be missing certain works, whether by the artist's intention or accident]. Pixiv images tend to be of higher quality. Pixiv requires even more clicks to reach the "original"-resolution images to download, and has a strange system that won't let you just hop to the final link to download it directly [they look at the HTTP referer header, which is spoofable]. I like these artists, I like their art, but I don't want to sit there for hours jumping through Pixiv's interface hoops to get the artist's images. I made this scraper to automate the difficult part of the "download all images by this artist" process.  
  
Everything that could go wrong, within reason  
• The scraper never finishes : There's a chance that pixiv will change their interface enough to break the scraper. I expect something like this eventually, and if you post an "Issue" about it here on GitHub, we can work together to try to fix this scraper.  
• The files won't download : It's possible that pixiv changed their link format. Post an "Issue" about it here on GitHub and we can work together to try to fix this scraper.  