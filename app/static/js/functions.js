/*!
 * functions.js - common functions to 1tool
 * Author: A. Ryding
 * Updated: May 2021
 * Copyright: n/a
 */

//////////////////////////////
/* ALERTING */
//////////////////////////////
function addAlert(alertType, alertMessage) {
    emptyDiv("alertbar")
    let alertBar = emptyDiv("alertbar");
    let alertClass = "alert alert-"+alertType;
    let iClass = 'fas';
    let div = document.createElement("div");
    let i = document.createElement("i");
    if ( alertType == "danger" ) {
        iClass = "fas fa-skull-crossbones";
    }
    if ( alertType == "info" ) {
        iClass = "fas fa-info-circle";
    }
    if ( alertType == "warning" ) {
        iClass = "fas fa-exclamation-triangle";
    }
    if ( alertType == "success" ) {
        iClass = "fas fa-thumbs-up";
    }
    i.setAttribute("class", iClass);
    div.appendChild(i);
    div.setAttribute("class", alertClass);
    div.setAttribute("role", "alert");
    div.appendChild(document.createTextNode(" " + alertMessage));
    alertBar.appendChild(div);
}

function addIncidentAlert(alertType, alertMessage) {
    emptyDiv("listalertbar")
    let alertBar = emptyDiv("listalertbar");
    let alertClass = "alert alert-"+alertType;
    let iClass = 'fas';
    let div = document.createElement("div");
    let i = document.createElement("i");
    if ( alertType == "danger" ) {
        iClass = "fas fa-skull-crossbones";
    }
    if ( alertType == "info" ) {
        iClass = "fas fa-info-circle";
    }
    if ( alertType == "warning" ) {
        iClass = "fas fa-exclamation-triangle";
    }
    if ( alertType == "success" ) {
        iClass = "fas fa-thumbs-up";
    }
    i.setAttribute("class", iClass);
    div.appendChild(i);
    div.setAttribute("class", alertClass);
    div.setAttribute("role", "alert");
    div.appendChild(document.createTextNode(" " + alertMessage));
    alertBar.appendChild(div);
}

//////////////////////////////
/* visibility functions */
//////////////////////////////
function buttonToggleTwoDivs(buttonid, onclass, offclass, on, off) {
	$('#'+buttonid)
	      .toggleClass(onclass)
	      .toggleClass(offclass);
    toggleDiv(on);
    toggleDiv(off);
    //toggleDisplayNoneStyle(on);
    //toggleDisplayNoneStyle(off);
}

function toggleTwoDivs(on, off) {
    toggleDiv(on);
    toggleDiv(off);
}

function toggleDisplayNoneStyle(elemid){
    let input_element = document.getElementById(elemid);
    if (input_element.style.display.search("none") >-1 ){
        //toggle on
        input_element.style.display = "inline";
    } else {
        input_element.style.display = "none";
    }
}

function toggleDiv(id) {
    var div = document.getElementById(id);
    if (div.className.search("invisible") > -1){
        div.style.display = "";
    } else {
        div.style.display = "none";
    }
    div.className = div.className == "invisible" ? "visible" : "invisible";

}

function toggleEdit(on, off) {
    document.getElementById(on).setAttribute("class", "d-block");
    document.getElementById(off).setAttribute("class", "d-none");
}

function toggleOn(eid) {
    document.getElementById(eid).setAttribute("class", "d-block");
}

function toggleOff(eid) {
    document.getElementById(eid).setAttribute("class", "d-none");
}

function compare_string(check_str, other_str){
    if (check_str == other_str){
        return true;
    } else{
        return false;
    }
}
/////////////////////////////
/* common dom interactions */
function element_exists(elemlocator) {
	return document.querySelector(elemlocator);
}

//////////////////////////////
/* update stuff */
//////////////////////////////
function emptyDiv(divid) {
    let x = document.getElementById(divid);
    $( "#"+divid ).empty();
    return x;
}

//////////////////////////////
/* SORTING AND FILTERING */
//////////////////////////////
function filterText(colclassa, colclassb, tableid, inputid) {
    let input, filter, table, tr, td, i;
    let tda = "";
    let tdb = "";
    input = document.getElementById(inputid);
    filter = input.value.toUpperCase();
    table = document.getElementById(tableid);
    tr = table.getElementsByTagName("tr");
    for (i = 0; i < tr.length; i++) {
        tda = tr[i].getElementsByClassName(colclassa)[0];
        tdb = tr[i].getElementsByClassName(colclassb)[0];
        if (tda || tdb ) {
            if (tda.innerHTML.toUpperCase().indexOf(filter) > -1 || tdb.innerHTML.toUpperCase().indexOf(filter) > -1) {
                tr[i].style.display = "";
            } else {
                tr[i].style.display = "none";
            }
        }
    }
}

$('th').click(function(){
  var table = $(this).parents('table').eq(0)
  var rows = table.find('tr:gt(0)').toArray().sort(comparer($(this).index()))
  this.asc = !this.asc
  if (!this.asc){rows = rows.reverse()}
  for (var i = 0; i < rows.length; i++){table.append(rows[i])}
})

function comparer(index) {
  return function(a, b) {
      var valA = getCellValue(a, index), valB = getCellValue(b, index)
      return $.isNumeric(valA) && $.isNumeric(valB) ? valA - valB : valA.toString().localeCompare(valB)
  }
}

function getCellValue(row, index){ return $(row).children('td').eq(index).text() }

//AJAX/PROMISE/FETCHES REQUESTS
var do_json_request = function(action, url) {
    let msg = { "status": "error", "status_code": 0, "message": "Did not do or complete call", "data":[] };
	let status = false;
	return fetch(url,
      {
        method: action,
        headers: {
        'Content-Type': 'application/json'
      }
      })
    .then(function(response) {
        console.info(response);
        let contentType = response.headers.get("content-type");
        if(contentType && contentType.includes("application/json")) {
            msg.status = "success";
            msg.status_code = response.status;
            msg.message = response.status+": "+action+" to "+url+"!";
            return true;

        } else {
            console.error("data is not JSON");
            msg.status = "warning";
	        msg.status_code = 422;
	        msg.message = "422: Oops, we haven't got JSON!";
           // throw new TypeError("Oops, we haven't got JSON!");
           return false;
        }
    })
    .catch(function(error) {
        console.error(error);
        msg.status = "danger";
        msg.status_code = 400;
        msg.message = "400: "+error;
        return false;
        }
     )
     .finally(function(){
        addAlert(msg.status, msg.message);
     })
}


var do_json_body_request = function(action, url, request_body) {
    let msg = { "status": "error", "status_code": 0, "message": "Did not do or complete call", "data":[] };
	let did_call = false;
	return fetch(url,
      {
        method: action,
        headers: {
        'Content-Type': 'application/json'
      },
      body: request_body,
      })
    .then(function(response) {
        console.info(response);
        let contentType = response.headers.get("content-type");
        if(contentType && contentType.includes("application/json")) {
            let response_json = response.json();
            msg.status = "success";
            msg.status_code = response_json.code;
            msg.message = response_json.message;
            did_call = true;
        } else {
            console.error("data is not JSON");
            throw new TypeError("Oops, we haven't got JSON!");
        }
    })
    .catch(function(error) {
        console.error(error);
        msg.status = "danger";
        msg.status_code = 400;
        msg.message = error;
        }
     )
     .finally(function(){
        addAlert(msg.status, msg.message);
        return did_call;
     })
}


//////////////////////////////
/* CSV TO nested lists */
//////////////////////////////
var result_list = [];
function readTextFile(delimiter){
    var rawFile = new XMLHttpRequest();
    rawFile.open("GET", "goals.csv", true);
    rawFile.onreadystatechange = function ()
    {
        if(rawFile.readyState === 4)
        {
            if(rawFile.status === 200 || rawFile.status == 0)
            {
                var allText = rawFile.responseText;
                return processData(allText, delimiter);
            }
        }
    }
    rawFile.send(null);
}

function processData(data, delimiter){
  result_list = []
  var allTextLines = data.split(/\r\n|\n/);
  //console.log(allTextLines[0])
  var header_row = allTextLines[0];
  allTextLines.forEach(function(row) {
    var obj = {};
    var rowData = row.split(delimiter);
    header_row.split(delimiter).forEach(function(val, idx) {
      obj[val] = rowData[idx];
    });
    result_list.push(obj);
    //return obj;
  })
  return True
}
//let dat = readTextFile(',');
//console.log(result_list);
