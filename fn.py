#!/usr/bin/python
import api
import time

def amisane(apikey,apisecret):
    sanity = True
    if apikey == '':
        return False
    if apisecret == '':
        return False
    return sanity
def checkreq(reqbody):
    #reqbody =  {"account": {"username": accountname,"comment": accountcomment,"groups": accountgroups, "password": {"length": passwordlength, "include_special": passwordspecialchar, "include_numbers": passwordnumberchar, "include_uppercase": passworduppercasechar}}}
    #Really need to complete this... it is meant to check the sanity of the reqbody, which can indicate psychosis in whoever populated the configs.

    return True

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
        print "Command is queued..."
        return ("queued", '')
    if checkresults["command"]["status"] == "completed":
        print "Command completed successfully!\n",checkresults
        return ("completed", checkresults["command"]["result"]["password"])
    if checkresults["command"]["status"] == "failed":
        print "Command failed! "
        print checkresults["command"]["result"]
        return ("failed", '')

def provision(host,authtoken,accountname,accountcomment,accountgroups,serveridno,passwordlength,passwordspecialchar,passwordnumberchar,passworduppercasechar):
    reqbody =  {"account": {"username": accountname,"comment": accountcomment,"groups": accountgroups,
                            "password": {"length": passwordlength, "include_special": passwordspecialchar,
                                         "include_numbers": passwordnumberchar, "include_uppercase": passworduppercasechar}}}
    if api.doesuserexist(host, authtoken, accountname, serveridno):
        print "\nAccount", accountname, "already exists on serveridno: ", serveridno
    else:
        url = api.requestcreateuser(host, authtoken, serveridno, reqbody)
    return url

def sam(host,authtoken, serveridno):
    reqbody= {"scan":{"module":"sam"}}
    url = api.samscan(host, authtoken, serveridno, reqbody)
    return url


def updatessh(host, authtoken, accountname, serveridno, skey):
    if api.doesuserexist(host, authtoken, accountname, serveridno):
        print "\nupdating ssh authorized key"
        url_ssh = api.updatessh(host, authtoken, accountname, serveridno, skey)
    else:
        print "\nSomething is wrong.", accountname,  "doesn't exist"

