function toggleRolling(div) {
  var className = div.getAttribute("class");
  if(className=="rolled") {
    div.className = "unrolled";
  }
  else{
    div.className = "rolled";
  }
}

function toggleRollingByName(name) {
  // XXX: name has been deprecated in HTML5
  var elems = document.getElementsByName(name);
  for (i = 0; i < elems.length; i++) {
  	toggleRolling(elems[i]);
  }
}



function changeSettings(obj) {
    var key = encodeURIComponent(obj.name);
    var value = encodeURIComponent(obj.value);

    var kvp = document.location.search.substr(1).split('&');
    var new_search = "";

    var i = kvp.length;
    var new_search="";
    while (i--) {
        var x = kvp[i].split('=');
        if (x == '') {
            continue;
        }
        if (x[0] != key) {
            new_search += "&" + kvp[i];
        }
    }

    new_search += "&" + key + "=" + value;
    document.location.search = new_search;
}


function toggleSettings(obj) {
    var key = encodeURIComponent(obj.name);
    var value = encodeURIComponent(obj.value);

    var kvp = document.location.search.substr(1).split('&');
    var new_search = "";
    var found = false;

    var i = kvp.length;
    var new_search="";
    while (i--) {
        var x = kvp[i].split('=');
        if (x == '') {
            continue;
        }
        if (x[0] == key) {
            // remove the key from url
            found = true;
            continue;
        } else {
            new_search += "&" + kvp[i];
        }
    }

    if (!found) {
        document.location.search += "&" + key + "=" + value;
    } else {
        document.location.search = new_search;
    }
}

function updateFilters(filtName = 'filter') {
    // gather all filters
	var form = document.getElementById("settingsform");
    var filters = []
    var elements = form.elements;
    for (i=0; i < elements.length; ++i) {
            if (elements[i].name == filtName
            && elements[i].value != "") {
            filters.push(filtName+"="+elements[i].value);
        }
    }

    // filter out old filters
    var kvp = document.location.search.substr(1).split('&');
    var new_search = "";
    var i = kvp.length;
    var new_search="";
    while (i--) {
        var x = kvp[i].split('=');
        if (x == '' || x[0] == filtName) {
            continue;
        } else {
            new_search += "&" + kvp[i];
        }
    }

    // set new URI
    for (i=0; i < filters.length; ++i) {
        new_search += "&" + filters[i];
    }
    //alert('Updating loc to: ' + new_search);
    document.location.search = new_search;
}

function addFilter(filt, filtName = 'filter') {
    document.location.search += "&" + filtName + "=" + filt;
}

function updateFiltersOnEnter(event, filtName='filter') {
    if (event.keyCode == 13) {
        updateFilters(filtName);
        event.preventDefault();
    }
}

function hideTool(tool_id) {
    var kvp = document.location.search.substr(1).split('&');
    var new_search = "";
    var i = kvp.length;

    while (i--) {
        var x = kvp[i].split('=');
        if (x == '') {
            continue;
        }
        if (x[0] == 'run' && x[1] == tool_id) {
            continue;
        } else {
            new_search += "&" + kvp[i];
        }
    }

    document.location.search = new_search;

    // do not continue in following the link
	return false;
}

function httpGetAsync(theUrl, callback = null)
{
    var xmlHttp = new XMLHttpRequest();
    if (callback) {
   	xmlHttp.onreadystatechange = function() {
   	    if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
   	        callback(xmlHttp.responseText);
   	}
    }
    xmlHttp.open("GET", theUrl, true); // true for asynchronous 
    xmlHttp.send(null);
}

function showStatusBar(text, in_progress = true) {
	var bar = document.getElementById("status-bar");
	bar.innerHTML = "<p>";
	if (in_progress) {
		bar.innerHTML += "<img alt=\"In Progress... \" src=\"../img/loader.gif\" height=\"24\">";
	}
	bar.innerHTML += text+"</p>";
	bar.setAttribute("class", "status-bar");
}

function hideStatusBar() {
	var bar = document.getElementById("status-bar");
	bar.innerHTML = "";
	bar.setAttribute("class", "status-bar-hidden");
}
