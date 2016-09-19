(function(){
	// notes
	// pixiv eventually throws in a dummy page, named "http://d.pixiv.org/dummy.html" that I used to think would end my script if adblock was enabled. Seems fine now.
	// pixiv checks the http referer header, and if it's not set to the correponding opener page, serves a 403 error. Clever, yet not the most wicked thing they could've done.
	var p = {
		version : 1,
		date : "19 Sep 2016",
		srcA : [],
		pageI : 1,
		userID : "",
		threadOpenC : 0, // inc/dec thread synchronization
		threadOpenHiC : 0, // for debug output
		threadOpenLoC : 0, // for debug output
		el_ad : null,
		ll : function(m){console.log(m);},
		// query selector down
		qd:function(el,m){
			if (typeof m === "undefined"){m = el;el = document.body;} // alternate use
			if (el === null){return null;}
			return el.querySelector(m);},
		// query selector down array [all]
		qdA:function(el,m){
			if (typeof m === "undefined"){m = el;el = document.body;} // alternate use
			if (el === null){return null;}
			var res = [];
			var elA = el.querySelectorAll(m);
			for (var i = 0; i < elA.length; i++){
				res.push(elA[i]);}
			return res;},
		saveTextAsFile : function(fileNameToSaveAs,textToWrite,filetype="text/plain"){
			var textFileAsBlob = new Blob([textToWrite],{type:filetype});
			var downloadLink = document.createElement("a");
			downloadLink.download = fileNameToSaveAs;
			downloadLink.innerHTML = "Download File";
			var url = (filetype === "text/plain") ? window.URL.createObjectURL(textFileAsBlob) : textToWrite; // ???
			if (window.URL != null){
				// Chrome allows the link to be clicked
				// without actually adding it to the DOM.
				downloadLink.href = url;}
			else{
				// Firefox requires the link to be added to the DOM
				// before it can be clicked.
				downloadLink.href = url;
				downloadLink.onclick = function(event){document.body.removeChild(event.target);};
				downloadLink.style.display = "none";
				document.body.appendChild(downloadLink);}
			downloadLink.click();},
		end : function(){this.ll("END");
			var resA = [];
			var resS = "";
			// curl --header "referer: http://www.pixiv.net/member_illust.php?mode=medium&illust_id=########" http://i3.pixiv.net/img-original/img/2016/09/02/23/44/10/########_p0.jpg -o out.jpg
			for (var srcAI = 0,srcAC = this.srcA.length; srcAI < srcAC; srcAI++){src = this.srcA[srcAI]; // src looks like : http://i3.pixiv.net/img-original/img/2016/09/02/23/44/10/########_p0.jpg
				var ID;src.replace(/\/(\d+)_p/,function(match,p1,offset,string){ID = p1;});
				var filename;src.replace(/\/([^\/]+)$/,function(match,p1,offset,string){filename = p1;});
				resA.push("curl --header \"referer: http://www.pixiv.net/member_illust.php?mode=medium&illust_id="+ID+"\" "+src+" -o "+filename);}
			resS = resA.join(";");
			this.ll(resS);
			this.saveTextAsFile("pixivUser"+this.userID+"CurlScript.txt",resS);},
		genIframe : function(body,src){
			var el = document.createElement("iframe");
			el.src = src;
			el.style.visibility = "hidden";
			body.appendChild(el);
			return el;},
		threadChangeFxn : function(){
			this.el_ad.innerHTML = "pages opened : "+this.threadOpenHiC+"<br>pages closed : "+this.threadOpenLoC+"<br>outstanding : "+this.threadOpenC;},
		setup : function(){
			var el = document.createElement("div");
			el.style.position = "fixed";
			el.style.bottom  = "20px";
			el.style.left = "0px";
			el.style.backgroundColor = "hsla(0,0%,100%,0.9)";
			el.style.padding = "20px";
			el.style.border = "1px solid black";
			el.style.zIndex = "9999999";
			var el_aa = document.createElement("div");
			el_aa.innerHTML = "<span style=\"font-weight:bold;font-size:120%;\">Pixiv Media Scraper Version "+this.version+" ["+this.date+"]</span><br>Usage instructions: Make sure you are viewing a user's \"作品\">\"総合\" feed. This has only been tested on artists with only still images, such as .png and .jpg files. As of September 2016, this can be found at \"http://www.pixiv.net/member_illust.php?id=[[[USERID_HERE]]]\". Once you have that feed loaded, click the relevant link/button below to start the scraper, which will look for all image links and take note of them in staggered parallel as soon as they are encountered.<br><br>! This scraper will open potentially hundreds of pages in a very short period of time [though it will happen invisibly to you]. Please be considerate of any people that you may be sharing your internet connection with. Also, please be mindful of either the loaded Pixiv pages or your web browser exploding from trying to open so many pages in parallel. This scraper will not download any images, it will only return[download] to you a list of command prompt commands. This is because Pixiv reads the HTTP referer header, and if it's not properly set, Pixiv won't let you view the image. Manually setting the referer header is made very difficult, if not impossible, through modern browsers, for etiquette-related reasons.<br><br>This page has now been messed up from running this script. If you want to browse another Pixiv page, just go ahead and click away. If you want to use ~this~ page, you should probably reload it so that everything is hooked up correctly.<br><br><a href=\"https://github.com/sliceofcake/PixivMediaScraper\">https://github.com/sliceofcake/PixivMediaScraper</a><br><br>If you know how to use a command prompt, then go ahead and navigate to the folder you want to download to, feed in this script's output to your prompt, read it over to make sure it looks okay, and run it. It uses curl to download all the images. If you aren't familiar with a \"command prompt\", then stop by the GitHub page that I mentioned for help.<br><br>If you want to try out file downloads right now so that there isn't a problem at the end of the script, try clicking the relevant link/button below to download three dummy files.<br><br>";
			var el_ab = document.createElement("button");
			el_ab.style.display = "block";
			el_ab.textContent = "click here to download three dummy files";
			el_ab.addEventListener("click",function(p){return function(){p.saveTextAsFile("dummy1.txt","blahblahblah1");p.saveTextAsFile("dummy2.txt","blahblahblah2");p.saveTextAsFile("dummy3.txt","blahblahblah3");};}(this));
			var el_ac = document.createElement("button");
			el_ac.style.display = "block";
			el_ac.textContent = "click here to find all media links and download one command .txt file [can take several minutes]";
			el_ac.addEventListener("click",function(p){return function(){p.main();};}(this));
			var el_ad = document.createElement("div");
			this.el_ad = el_ad;
			this.threadChangeFxn();
			el.appendChild(el_aa);
			el.appendChild(el_ab);
			el.appendChild(el_ac);
			el.appendChild(el_ad);
			document.body.appendChild(el);},
		main : function(){
			window.location.href.replace(/(?:&|\?)id=(.+?)(?:&|$)/,function(match,p1,offset,string){p.userID = p1;});
			this.cycle1();},
		cycle1 : function(){
//		L> foreach page number from 1 to infinity [will detect the first out-of-bounds page and stop]
//			L> load the given gallery page from url knowledge
			var el = this.genIframe(document.body,"http://www.pixiv.net/member_illust.php?id="+p.userID+"&type=all&p="+this.pageI);
			p.threadOpenC++;p.threadOpenHiC++;p.threadChangeFxn();el.contentWindow.addEventListener("DOMContentLoaded",function(p,elSelfIframe,pageI){return function(){
				p.ll("| "+this.location.href);
//				L> foreach µ.qd(".thumbnail") as opener
				var elThumbnailA = p.qdA(this.document.body,"._thumbnail");
				for (var elThumbnailAI = 0,elThumbnailAC = elThumbnailA.length; elThumbnailAI < elThumbnailAC; elThumbnailAI++){var elThumbnail = elThumbnailA[elThumbnailAI];
//					L> load elThumbnail.parentNode.parentNode.href
					var el = p.genIframe(this.document.body,elThumbnail.parentNode.parentNode.href);
					p.threadOpenC++;p.threadOpenHiC++;p.threadChangeFxn();el.contentWindow.addEventListener("DOMContentLoaded",function(p,elSelfIframe){return function(){
						p.ll("L> "+this.location.href);
//						L> check url for mode=???
						//var mode;this.location.href.replace(/(?:&|\?)mode=(.+?)(?:&|$)/,function(match,p1,offset,string){mode = p1;});
						var mode = p.qd(this.document.body,"._work.multiple")===null?"single":"multi";
						switch (mode){default:;
//							L> if single
							break;case "single":
//								L> dl µ.qd(".original-image").getAttribute("data-src")
								var link = p.qd(this.document.body,".original-image").getAttribute("data-src");
								p.ll("save single "+link);
								p.srcA.push(link);
								this.parent.document.body.removeChild(elSelfIframe); // remove self from parent DOM
//							L> if multi
							break;case "multi":
//								L> load µ.qd("._layout-thumbnail").parentNode.href
								var el = p.genIframe(this.document.body,p.qd(this.document.body,"._layout-thumbnail").parentNode.href);
								p.threadOpenC++;p.threadOpenHiC++;p.threadChangeFxn();el.contentWindow.addEventListener("DOMContentLoaded",function(p,elSelfIframe){return function(){
									var elExpandA = p.qdA(this.document.body,".image");
									for (var elExpandAI = 0,elExpandAC = elExpandA.length; elExpandAI < elExpandAC; elExpandAI++){var elExpand = elExpandA[elExpandAI];
										var src = elExpand.getAttribute("data-src");
										var domain;src.replace(/(https?:\/\/.+?\/)/,function(match,p1,offset,string){domain = p1;});
										var date;src.replace(/(\d{4}\/\d{2}\/\d{2}\/\d{2}\/\d{2}\/\d{2}\/)/,function(match,p1,offset,string){date = p1;});
										var ID;src.replace(/\/(\d+)_p/,function(match,p1,offset,string){ID = p1;});
										var page;src.replace(/\/\d+_p(\d+)/,function(match,p1,offset,string){page = p1;});
										var extension;src.replace(/(\.[^\.]+)$/,function(match,p1,offset,string){extension = p1;});
										var link = domain+"img-original/img/"+date+ID+"_p"+page+extension;
										//p.ll(src+" ... "+domain+" ... "+date+" ... "+ID+" ... "+page+" ... "+extension);
										p.ll("save multi-part "+link);
										p.srcA.push(link);}
									this.parent.document.body.removeChild(elSelfIframe); // remove self from parent DOM
//									L> foreach µ.qdA(".full-size-container").href as tiger
									/*var elExpandA = p.qdA(this.document.body,".full-size-container");
									for (var elExpandAI = 0,elExpandAC = elExpandA.length; elExpandAI < elExpandAC; elExpandAI++){var elExpand = elExpandA[elExpandAI];
//										L> load tiger
										var el = p.genIframe(this.document.body,elExpand.href);
										p.threadOpenC++;p.threadOpenHiC++;p.threadChangeFxn();el.contentWindow.addEventListener("DOMContentLoaded",function(p,elSelfIframe,elExpandAI,elExpandAC){return function(){
											p.ll("L> L> "+this.location.href);
//											L> dl µ.qd("img").src
											var link = p.qd(this.document.body,"img").src;
											p.ll("save multi-part "+link);
											p.srcA.push(link);
											this.parent.document.body.removeChild(elSelfIframe); // remove self from parent DOM
										p.threadOpenC--;p.threadOpenLoC++;p.threadChangeFxn();if (p.threadOpenC === 0){p.end();}};}(p,el,elExpandAI,elExpandAC));
									}*/
								p.threadOpenC--;p.threadOpenLoC++;p.threadChangeFxn();if (p.threadOpenC === 0){p.end();}};}(p,el));
						}
					p.threadOpenC--;p.threadOpenLoC++;p.threadChangeFxn();if (p.threadOpenC === 0){p.end();}};}(p,el));
				}
				if (elThumbnailA.length > 0){
					setTimeout(function(p){return function(){p.pageI++;p.cycle1();};}(p),0);}
			p.threadOpenC--;p.threadOpenLoC++;p.threadChangeFxn();if (p.threadOpenC === 0){p.end();}};}(this,el,this.pageI));
		},
	};
	p.setup();
})();