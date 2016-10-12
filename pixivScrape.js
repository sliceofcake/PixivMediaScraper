(function(){
	// notes
	// pixiv eventually throws in a dummy page, named "http://d.pixiv.org/dummy.html" that I used to think would end my script if adblock was enabled. Seems fine now.
	// pixiv checks the http referer header, and if it's not set to the correponding opener page, serves a 403 error. Clever, yet not the most wicked thing they could've done.
	var p = {
		version    :             3,
		date       :  "6 Oct 2016",
		dlFilename : "pixivDownloadUpdateScript.txt",
		el_ad      : null         ,
		el_ae      : null         ,
		userIDA    : []           ,
		userIDAI   :            -1,
		outFinalS  : ""           ,
		outCmdSA   : []           ,
		outMsgSA   : []           ,
		ll : function(m){console.log(m);},
		// escape a filename [sounds bad, but I really don't have a guarantee that this is enough]
		escFil : function(m){
			if (typeof m !== "string"){m = m.toString();}
			var s = m;
			return s.replace(/\\/g,"＼").replace(/\//g,"／").replace(/"/g,"”").replace(/'/g,"’").replace(/\*/g,"＊").replace(/\$/g,"＄").replace(/\./g,"。");},
		// escape a pathname [sounds bad, but I really don't have a guarantee that this is enough]
		escPth : function(m){
			if (typeof m !== "string"){m = m.toString();}
			var s = m;
			return s.replace(/\"/g,"\"");},
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
		loadFileAsText : function(fileToLoad,fxn){
			if (fileToLoad === null){fxn("");return;}
			var fileReader = new FileReader();
			fileReader.onload = (fileLoadedEvent)=>{
				var textFromFileLoaded = fileLoadedEvent.target.result;
				fxn(textFromFileLoaded);};
			fileReader.readAsText(fileToLoad,"UTF-8");},
		genIframe : function(body,src){
			var el = document.createElement("iframe");
			el.src = src;
			el.style.visibility = "hidden";
			el.className = "sliceofstrawberrycake";
			body.appendChild(el);
			return el;},
		removeIframeAll : function(){
			// remove all iframes for this user
			var elA = this.qdA(".sliceofstrawberrycake");
			for (var elAI = 0,elAC = elA.length;elAI < elAC; elAI++){el = elA[elAI];
				el.parentNode.removeChild(el);}},
		//----
		end : function(){this.ll("END");
			var dirnameBase = "#"+p.userID;
			var dirname = p.username+dirnameBase; // remember to escape double quotes for the final string, should be currently handled for p.username
			var resA = [];
			// ! currently, we guess what the original links will be to save a lot of execution time. unfortunately, that will always return ".jpg". most of these images ~are~ ".jpg", but some are .png
			// curl --header "referer: http://www.pixiv.net/member_illust.php?mode=medium&illust_id=########" http://i3.pixiv.net/img-original/img/2016/09/02/23/44/10/########_p0.jpg -o out.jpg
			for (var srcAI = 0,srcAC = this.srcA.length; srcAI < srcAC; srcAI++){src = this.srcA[srcAI]; // src looks like : http://i3.pixiv.net/img-original/img/2016/09/02/23/44/10/########_p0.jpg
				/*error:cannot read replace of undefined*/var ID;src.replace(/\/(\d+)_p/,function(match,p1,offset,string){ID = p1;});
				var filename;src.replace(/\/([^\/]+)$/,function(match,p1,offset,string){filename = p1;});
				var fileID;src.replace(/\/([^\/]+)\.(?:[^\/]+)$/,function(match,p1,offset,string){fileID = p1;});
				resA.push(""
					+"if test -z \"$(find \""+p.escFil(dirname)+"\" -name \""+p.escFil(fileID)+".*\" -maxdepth 1 | head -c 1)\";then\n"
						+"if curl -s --header \"referer: "+p.escPth("http://www.pixiv.net/member_illust.php?mode=medium&illust_id="+ID)+"\" -I \""+p.escPth(src)+"\" | grep -q \""+p.escFil("404 Not Found")+"\"\n"
							+"then curl -s --header \"referer: "+p.escPth("http://www.pixiv.net/member_illust.php?mode=medium&illust_id="+ID)+"\" \""+p.escPth(src.replace(".jpg",".png"))+"\" -o \""+p.escFil(dirname)+"/"+p.escFil(filename.replace(".jpg",".png"))+"\"\n"
							+"else curl -s --header \"referer: "+p.escPth("http://www.pixiv.net/member_illust.php?mode=medium&illust_id="+ID)+"\" \""+p.escPth(src)+"\" -o \""+p.escFil(dirname)+"/"+p.escFil(filename)+"\"\n"
					+"fi;fi");
				//resA.push("curl --header \"referer: http://www.pixiv.net/member_illust.php?mode=medium&illust_id="+ID+"\" "+src+" -o "+filename);
				}
			var resAlterA = [];
			for (var resAI = 0,resAC = resA.length; resAI < resAC; resAI++){var res = resA[resAI];
				resAlterA.push("("+res+") &");
				if (resAI%8 === (8-1) || resAI === resAC-1){resAlterA.push("wait\necho \"artist #"+p.escFil(p.userID)+" "+p.escFil(p.username)+" -> "+p.escFil(resAI+1)+"/"+p.escFil(this.srcA.length)+"\"");}}
			this.outCmdSA.push(""
				// if we can't find the exact directoryname, then create it
				+"if ! test -d \""+p.escFil(dirname)+"\";then\n"
					+"mkdir \""+p.escFil(dirname)+"\"\n"
				+"fi\n"
				// merge any incorrectly named directories
				// previous used: [[[-not -name \""+p.escFil(dirname)+"\"]]] in the dirname find line, but it doesn't seem to handle encodings as well as [[[test -ef]]]
				+"find . -name \"*"+p.escFil(dirnameBase)+"\" -maxdepth 1 | while read dirname;do\n"
					+"if ! test \"$dirname\" -ef \""+p.escFil(dirname)+"/\";then\n"
						+"find \"$dirname\" -type f | while read filname;do\n"
							+"mv \"$filname\" \""+p.escFil(dirname)+"/\"\n"
						+"done\n"
						+"rmdir \"$dirname\"\n" // this is safe -> rmdir used like this will only remove an already-empty directory
					+"fi\n"
				+"done\n"
				+resAlterA.join("\n")); // \n for Unix
			this.outMsgSA.push("echo \"pixiv userID #"+p.escFil(p.userID)+" -> Success. Please verify the existence of exactly "+p.escFil(this.srcA.length)+" images.\"");
			p.removeIframeAll();
			this.main();},
		threadChangeFxn : function(){
			this.el_ad.innerHTML = p.threadOpenA.join("<br>")+"<br>[artist #"+p.userID+(p.username===null?"":" "+p.username)+"] processing/about-to-process page # "+this.pageI+"<br>pages opened : "+this.threadOpenHiC+"<br>pages closed : "+this.threadOpenLoC+"<br>outstanding : "+this.threadOpenC;},
		threadEvent : function(type,el){
			switch (type){default:;
				break;case "hi":p.threadOpenC++;p.threadOpenHiC++;p.threadOpenA.push(el.src);p.threadChangeFxn();
				break;case "lo":p.threadOpenC--;p.threadOpenLoC++;var i=p.threadOpenA.indexOf(el.src);if (i===-1){console.log("!!! OH NO "+el.src);}p.threadOpenA.splice(i,1);p.threadChangeFxn();}},
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
			el_aa.innerHTML = "<span style=\"font-weight:bold;font-size:120%;\">Pixiv Media Scraper Version "+this.version+" ["+this.date+"]</span><br>(1) Drag&amp;Drop or Browse-Select for userID file below. You'll see an output of the text. Make sure it looks correct -> one pixiv userID per line.<br>(2) Click the download button. Wait for the process to complete, and one file will download.<br>(3) Place that file in your pixiv top-level folder and run that file with \"sh\", like \"sh "+this.dlFilename+"\". Delete<br><br>";
			
			var el_af = document.createElement("input");
			el_af.setAttribute("type","file");
			el_af.addEventListener("change",(function(p){return function(){
				p.loadFileAsText(this.files[0],function(txt){
					p.el_ae.value = txt;
					p.el_ae.KERN.onchangeFxn.call(p.el_ae);
				});
			};})(this));
			
			var el_ae = document.createElement("textarea");
			el_ae.style.display = "block";
			el_ae.style.height = "100px";
			el_ae.KERN = {};
			el_ae.KERN.onchangeFxn = (function(p){return function(){
				p.userIDA = [];
				var a = this.value.replace(/\/\/.*$/gm,function(match,offset,string){return "";});
				var a = a.split(/\D+/);
				for (var i = 0; i < a.length; i++){var v = a[i];
					if (v === ""){continue;}
					var vInt = parseInt(v);
					if (isNaN(vInt)){continue;}
					p.userIDA.push(vInt);}
				this.value = p.userIDA.join("\n");
			};})(this);
			el_ae.addEventListener("input",el_ae.KERN.onchangeFxn);
			this.el_ae = el_ae;
			
			var el_ac = document.createElement("button");
			el_ac.style.display = "block";
			el_ac.style.height = "50px";
			el_ac.textContent = "generate and download "+this.dlFilename;
			el_ac.addEventListener("click",function(p){return function(){p.main();};}(this));
			
			var el_ad = document.createElement("div");
			this.el_ad = el_ad;
			
			var el_ab = document.createElement("button");
			el_ab.style.display = "block";
			el_ab.textContent = "click here to download three dummy files to test your browser's downloading configuration";
			el_ab.addEventListener("click",function(p){return function(){p.saveTextAsFile("dummy1.txt","blahblahblah1");p.saveTextAsFile("dummy2.txt","blahblahblah2");p.saveTextAsFile("dummy3.txt","blahblahblah3");};}(this));
			
			el.appendChild(el_aa);
			el.appendChild(el_af);
			el.appendChild(el_ae);
			el.appendChild(el_ac);
			el.appendChild(el_ad);
			el.appendChild(el_ab);
			document.body.appendChild(el);},
		main : function(){
			this.userIDAI++;
			// if [obvious] then done
			if (this.userIDAI >= this.userIDA.length){
				this.outFinalS = this.outCmdSA.join("\n")+"\n"+this.outMsgSA.join("\n")+"\n"+"rm "+this.dlFilename;
				this.saveTextAsFile(this.dlFilename,this.outFinalS);
				return;}
			this.srcA          = []   ;
			this.pageI         =     1;
			this.userID        = this.userIDA[this.userIDAI];
			this.username      = null ;
			this.threadOpenA   = []   ;
			this.threadOpenC   =     0; // inc/dec thread synchronization
			this.threadOpenHiC =     0; // for debug output
			this.threadOpenLoC =     0; // for debug output
			this.allPageDoneF  = false;
			this.cycle1();},
		// each run of cycle processes one page
		cycle1 : function(){
			// delay the next page until the previous page has completed
			if (p.threadOpenC > 0){
				setTimeout(function(p){return function(){p.cycle1();};}(p),100);return;}
			p.removeIframeAll();
			// foreach page, load based off pre-known link format
			var el = this.genIframe(document.body,"http://www.pixiv.net/member_illust.php?id="+p.userID+"&type=all&p="+this.pageI);
			p.threadEvent("hi",el);el.contentWindow.addEventListener("DOMContentLoaded",function(p,elSelfIframe,pageI){return function(){
				// get username
				if (p.username === null){p.username = this.document.body.querySelector(".user").textContent;} // ! test : p.username = "@\"*$file";
				// foreach µ.qd(".thumbnail")
				var elThumbnailA = p.qdA(this.document.body,"._thumbnail");
				for (var elThumbnailAI = 0,elThumbnailAC = elThumbnailA.length; elThumbnailAI < elThumbnailAC; elThumbnailAI++){var elThumbnail = elThumbnailA[elThumbnailAI];
					// this thumbnail is a multi
					if (elThumbnail.parentNode.parentNode.classList.contains("multiple")){
						// convert the link to manga format based off pre-known link format
						var mangaLink = elThumbnail.parentNode.parentNode.href.replace("medium","manga");
						var el = p.genIframe(this.document.body,mangaLink);
						p.threadEvent("hi",el);el.contentWindow.addEventListener("DOMContentLoaded",function(p,elSelfIframe){return function(){
							var elExpandA = p.qdA(this.document.body,".image");
							for (var elExpandAI = 0,elExpandAC = elExpandA.length; elExpandAI < elExpandAC; elExpandAI++){var elExpand = elExpandA[elExpandAI];
								var link = null;elExpand.getAttribute("data-src").replace(/(https?:\/\/.+?\/).+(\d{4}\/\d{2}\/\d{2}\/\d{2}\/\d{2}\/\d{2}\/)(\d+)_p(\d+).+(\.[^\.]+)$/,function(match,domain,date,ID,page,extension,offset,string){link = domain+"img-original/img/"+date+ID+"_p"+page+extension;});
								//p.ll("save multi-part "+link);
								if (link !== null){p.srcA.push(link);}} // .gif gate
							this.parent.document.body.removeChild(elSelfIframe); // remove self from parent DOM, special case here since this is always a dead-end iframe
						p.threadEvent("lo",elSelfIframe);if (p.allPageDoneF && p.threadOpenC === 0){p.end();}};}(p,el));}
					// this thumbnail is a single
					else{
						//http://i4.pixiv.net/c/150x150/img-master/img/2016/03/29/21/33/59/56079447_master1200.jpg
						var link = null;elThumbnail.src.replace(/(https?:\/\/.+?\/).+(\d{4}\/\d{2}\/\d{2}\/\d{2}\/\d{2}\/\d{2}\/)(\d+)_p(\d+).+(\.[^\.]+)$/,function(match,domain,date,ID,page,extension,offset,string){link = domain+"img-original/img/"+date+ID+"_p"+page+extension;});
						//p.ll("save single "+link);
						if (link !== null){p.srcA.push(link);}}} // .gif gate
				if (elThumbnailA.length === 0){
					p.allPageDoneF = true;}
				else{
					setTimeout(function(p){return function(){p.pageI++;p.cycle1();};}(p),0);} // put some delay on the next page, so that the browser isn't multitasking too much
			p.threadEvent("lo",elSelfIframe);if (p.allPageDoneF && p.threadOpenC === 0){p.end();}};}(this,el,this.pageI));
		},
	};
	p.setup();
})();