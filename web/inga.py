import urllib.parse
from pathlib import Path
from flask import request, send_from_directory
from markupsafe import Markup

from flask import Blueprint, render_template
from flask import current_app as app

from core import api
from plugins.inga.models import inga

pluginPages = Blueprint('ingaPages', __name__, template_folder="templates")

@pluginPages.app_template_filter('urlencode')
def urlencode_filter(s):
    if type(s) == 'Markup':
        s = s.unescape()
    s = s.encode('utf8')
    s = urllib.parse.quote_plus(s)
    return Markup(s)

@pluginPages.route('/inga/includes/<file>')
def custom_static(file):
    return send_from_directory(str(Path("plugins/inga/web/includes")), file)

@pluginPages.route("/inga/")
def mainPage():
    scans = inga._inga()._dbCollection.distinct("scanName")
    results = []
    for scan in scans:
        totalCount = inga._inga().count(api.g.sessionData,query={ "scanName" : scan })["results"][0]["count"]
        upCount = inga._inga().count(api.g.sessionData,query={ "scanName" : scan, "up" : True })["results"][0]["count"]
        if totalCount > 0:
            results.append({ "scanName" : scan, "up" : upCount, "total" : totalCount })
    return render_template("scans.html", scans=results)

@pluginPages.route("/inga/scan/")
def getScan():
    scanName = urllib.parse.unquote_plus(request.args.get("scanName"))
    results = inga._inga().query(api.g.sessionData,query={ "scanName" : scanName, "up" : True },fields=["scanName","ip","up","lastScan","ports"])["results"]
    if "ipToPorts" in request.args:
        ipToPorts = []
        for scan in results:
            try:
                for portKey, portValue in scan["ports"]["tcp"].items():
                    if portValue["state"] == "open":
                        ipToPorts.append([scan["ip"],portValue["port"]])
            except KeyError:
                pass
        return { "results" : ipToPorts }, 200
    elif "portCount" in request.args:
        ports = { }
        for scan in results:
            try:
                for portKey, portValue in scan["ports"]["tcp"].items():
                    if portValue["port"] not in ports:
                        ports[portValue["port"]] = 0
                    if portValue["state"] == "open":
                        ports[portValue["port"]]+=1
            except KeyError:
                pass
        return { "results" : ports }, 200
    elif "ipCount" in request.args:
        ips = { }
        for scan in results:
            c = 0
            try:
                for portKey, portValue in scan["ports"]["tcp"].items():
                    if portValue["state"] == "open":
                        c += 1
                if c > 0:
                    try:
                        ips[scan["ip"]] = c
                    except KeyError:
                        pass
            except KeyError:
                pass
        return { "results" : ips }, 200
    return render_template("scan.html", scanResults=results)

@pluginPages.route("/inga/scan/images/")
def getScanImages():
    scanName = urllib.parse.unquote_plus(request.args.get("scanName"))
    results = inga._inga().query(api.g.sessionData,query={ "scanName" : scanName, "up" : True },fields=["portData","ip"])["results"]
    result = []
    for scan in results:
        try:
            for port,portValue in scan["portData"]["tcp"].items():
                if port == "443":
                    result.append({"ip" : scan["ip"], "port" : port, "fileData" : portValue["webScreenShot"]["fileData"], "type" : "https"})
                else:
                    result.append({"ip" : scan["ip"], "port" : port, "fileData" : portValue["webScreenShot"]["fileData"], "type" : "http"})
        except KeyError:
            pass
    return render_template("scanImages.html", result=result)
