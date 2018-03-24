var startTime = new Date();
var phase_actuelle = "off";
var start = new Date();;
var end = 0;
var diff = 0;
var tDiff = 0;
var timerID = 0;

function chrono(){
    end = new Date();
    diff = end - start;
    diff = new Date(diff);

    var sec = diff.getSeconds();
    var min = diff.getMinutes();
    var hr = diff.getHours()-1;

    if (min < 10) min = "0" + min;
    if (sec < 10) sec = "0" + sec;

    //TOTAL
    tDiff = new Date(end-startTime);
    var tSec = tDiff.getSeconds();
    var tMin = tDiff.getMinutes();
    var tHr = tDiff.getHours()-1;

    if (tMin < 10) tMin = "0" + tMin;
    if (tSec < 10) tSec = "0" + tSec;

    document.getElementById("chronotime").innerHTML = hr + ":" + min + ":" + sec;
    document.getElementById("total").innerText = tHr + ":" + tMin + ":" + tSec;
    timerID = setTimeout("chrono()", 1000)
}

function setOn() {
    if(phase_actuelle!="on") {
        phase_actuelle = "on";
        document.getElementById("phase").innerText = "ON";
        document.body.className = "on";
        chronoReset();

        $("#cOn").html(((parseInt($("#cOn").html()))+1));
    }
}

function setOff() {
    if(phase_actuelle!="off") {
        phase_actuelle = "off";
        document.getElementById("phase").innerText = "OFF";
        document.body.className = "off";
        chronoReset();

        $("#cOff").html(((parseInt($("#cOff").html()))+1));
    }
}

function setNormale() {
    if(phase_actuelle!="normale") {
        phase_actuelle = "normale";
        document.getElementById("phase").innerText = "NORMALE";
        document.body.className = "normale";
        chronoReset();

        $("#cNormale").html(((parseInt($("#cNormale").html()))+1));
    }
}

function chronoReset() {
    start = new Date();
    chrono();
}