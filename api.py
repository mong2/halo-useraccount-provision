#!/usr/bin/python
#
# This script creates user accounts, or resets passwords if they already exist.
# DON'T FORGET TO SET THE API KEY/SECRET.



import urllib
import httplib
import base64
import json
import urlparse
import sys

def apihit(host,conntype,authtoken,queryurl,reqbody):
    connection = httplib.HTTPSConnection(host)
    tokenheader = {"Authorization": 'Bearer ' + authtoken, "Content-type": "application/json", "Accept": "text/plain"}
    if conntype == "GET":
        connection.request(conntype, queryurl, '', tokenheader)
    else:
        print conntype, "type connection. Auth: ", authtoken , " URL " , queryurl , "Reqbody: " , reqbody
        connection.request(conntype, queryurl, json.dumps(reqbody), tokenheader)
    response = connection.getresponse()
    respbody = response.read()
    reqstatus = response.status
    jsondata = respbody.decode()
    connection.close()
    return reqstatus, json.loads(jsondata)

def getauthtoken(host,clientid,clientsecret):
    # Get the access token used for the API calls.
    connection = httplib.HTTPSConnection(host)
    authstring = "Basic " + base64.b64encode(clientid + ":" + clientsecret)
    header = {"Authorization": authstring}
    params = urllib.urlencode({'grant_type': 'client_credentials'})
    connection.request("POST", '/oauth/access_token', params, header)
    response = connection.getresponse()
    jsondata =  response.read().decode()
    data = json.loads(jsondata)
    key = data['access_token']
    connection.close()
    return key

def getserverlist(host,authtoken,groupid):
    queryurl = "/v1/groups/"+groupid+"/servers"
    reqstatus, jsondata = apihit(host,"GET", authtoken, queryurl, '')

    if reqstatus == 200:
        print "200 Get Server List"
    else:
        print reqstatus, "Get Server List -- Something is wrong"
        sys.exit()
    return jsondata

def getgroupid(host,authtoken,groupname):
    queryurl = "/v1/groups"
    reqstatus, jsondata = apihit(host,"GET", authtoken, queryurl, '')
    if reqstatus == 200:
        print "200 Get Group Id"
    else:
        print reqstatus, " Get Group Id -- Something is wrong"
        sys.exit()
    for g in jsondata["groups"]:
        if g["name"] == groupname:
            groupid = g["id"]
            return groupid
        else:
            continue
    #if we get to this point, there wasn't a match
    print "No matching group name found"
    sys.exit()
def updatessh(host, authtoken, username, serverid, skey):
    #We set up the new public key request body here
    reqbody = {"account":{"ssh_authorized_keys":[{"key": skey}]}}
    queryurl = "/v1/servers/" + serverid + "/accounts/" + username
    reqstatus, jsondata = apihit(host, "PUT", authtoken, queryurl, reqbody)
    if reqstatus == 202:
        print "202 Update SSH"
    else:
        print reqstatus, " Update SSH -- Something is wrong"
        sys.exit()
    print jsondata
    #cmdurl = jsondata["command"]["url"]

def changepass(host,authtoken,username,serverid,pwlength,pwspecial,pwnumbers,pwuppercase,skey):
#We set up the password change request body here
    reqbody =  {"password": {"length": pwlength, "include_special": pwspecial, "include_numbers": pwnumbers, "include_uppercase": pwuppercase}}
    queryurl = "/v1/servers/" + serverid + "/accounts/"+username+"/password"
    reqstatus, jsondata = apihit(host,"PUT", authtoken, queryurl, reqbody)
    if reqstatus == 200:
        print "200 Password"
        cmdurl = jsondata["command"]["url"]
    else:
        print reqstatus, "Password -- Something is wrong"
        sys.exit()
    return cmdurl



def doesuserexist(host,authtoken,user,serverid):
    queryurl = "/v1/servers/"+serverid+"/accounts?search[username]="+user
    reqstatus, checkresponse = apihit(host,"GET", authtoken, queryurl, '')

    if reqstatus == 200:
        print "200 Check user existance"
    else:
        print reqstatus, " Check user existance -- Somethig is wrong"
        sys.exit()
    try:
        if checkresponse["accounts"][0]["username"] == user :
            # print "User "+user+" exists"
            return True
    except:
        return False

def requestcreateuser(host,authtoken,serveridno,reqbody):
    queryurl = "/v1/servers/" + serveridno + "/accounts"
    reqstatus, jsondata = apihit(host,"POST", authtoken, queryurl, reqbody)
    deets = ''
    try:
        deets = jsondata["errors"][0]["details"]
        print "Whoops..."
    except:
        pass
    if deets != '':
        print "Well, something went wrong.  Details follow:\n",deets,"\nExiting"
        sys.exit(2)
    print "URL: ",queryurl
    print "Request Body: ",reqbody
    print "Response: ",jsondata
    cmdurl = jsondata["command"]["url"]
    return cmdurl

def checkcommand(authtoken,url,host):
    parsedurl = urlparse.urlparse(url)
    checkpath = parsedurl.path
    reqstatus,checkresponse = apihit(host,"GET", authtoken, checkpath, '')
    return checkresponse

def samscan(host, authtoken, serveridno, reqbody):
    queryurl = "/v1/servers/" + serveridno + "/scans"
    reqstatus, scan = apihit(host, "POST", authtoken, queryurl,reqbody)
    if reqstatus == 202:
        print "202 SAM scan"
    else:
        print reqstatus, " SAM scan -- Something is wrong"
