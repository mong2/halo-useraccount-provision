#!/usr/bin/python
import api

def printresults(serverlist):
    print "\n\n\n"
    print "Results:"
    print "Hostname\t\tUsername\tPassword"
    print "--------------------------------------------------"
    for s in serverlist:
        print s.name,"\t",s.user,"\t",s.password

def getjobstatus(serverlist):
    totalcount = len(serverlist)
    donecount = 0
    for s in serverlist:
        if s.password !=  '' :
            donecount = donecount + 1
        else:
            continue
    return (totalcount,donecount)

def passwordcheck(url,key,host):
    checkresults = api.checkcommand(key,url,host)
    if checkresults["command"]["status"] == "queued":
        #print "Command is queued..."
        return ("queued", '')
    if checkresults["command"]["status"] == "completed":
        #print "Command completed successfully!\n",checkresults
        return ("completed", checkresults["command"]["result"]["password"])
    if checkresults["command"]["status"] == "failed":
        #print "Command failed! "
        #print checkresults["command"]["result"]
        return ("failed", '')

def provision(host,authtoken,accountname,accountcomment,accountgroups,serveridno,passwordlength,passwordspecialchar,passwordnumberchar,passworduppercasechar):
    reqbody =  {"account": {"username": accountname,"comment": accountcomment,"groups": accountgroups, "password": {"length": passwordlength, "include_special": passwordspecialchar, "include_numbers": passwordnumberchar, "include_uppercase": passworduppercasechar}}}
    if api.doesuserexist(host,authtoken,accountname,serveridno):
        print "\nAccount ", accountname , " already exists on serveridno: ",serveridno
        url = api.changepass(host,authtoken,accountname,serveridno,passwordlength,passwordspecialchar,passwordnumberchar,passworduppercasechar)
    else:
        url = api.requestcreateuser(host,authtoken,serveridno,reqbody)
    return url
