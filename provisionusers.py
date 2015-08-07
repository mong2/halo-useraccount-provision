#!/usr/bin/python
#
# This script creates user accounts, or resets passwords if they already exist.

import time
import sys
import getopt
import json
import api
import server
import fn

def main(argv):
    config={}
    #First, we get the vars from the config file
    execfile("config.conf",config)
    usagetext = "provisionusers.py -u USER -g GROUP -s SERVERGROUP"
    serverolist = []
    # Next, we attempt to parse args from CLI, overriding vars from config file.
    try:
        opts, args = getopt.getopt(argv, "hu:g:s:",["user=","group=","servergroup="])
    except getopt.GetoptError:
        print config["usagetext"]
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print config["usagetext"]
            sys.exit()
        elif opt in ("-u", "--user"):
            config["accountname"] = arg
        elif opt in ("-g", "--group"):
            config["accountgroups"] = arg
        elif opt in ("-s","--servergroup"):
            config["servergroupname"] = arg

    servergroupname = config["servergroupname"]
    iterations = config["iterations"]
    accountname = config["accountname"]
    accountcomment = config["accountcomment"]
    accountgroups = config["accountgroups"]
    passwordlength = config["passwordlength"]
    passwordspecialchar = config["passwordspecialchar"]
    passwordnumberchar = config["passwordnumberchar"]
    passworduppercasechar = config["passworduppercasechar"]
    clientid = config["clientid"]
    clientsecret = config["clientsecret"]
    host = config["host"]
    skey = config["skey"]

    # Sanity check, let's make sure that we aren't speaking crazytalk
    sanity = fn.amisane(clientid,clientsecret)
    if sanity == False:
        print "Insane in the membrane.  Crazy insane, got no keys."
        sys.exit(2)
    reqbody =  {"account": {"username": accountname,"comment": accountcomment,"groups": accountgroups, "password": {"length": passwordlength, "include_special": passwordspecialchar, "include_numbers": passwordnumberchar, "include_uppercase": passworduppercasechar}}}
    print json.dumps(reqbody, indent = 2)
    sanity = fn.checkreq(reqbody)
    if sanity == False:
        print "Check your config file, looks like you are missing something..."
        sys.exit(2)
    # Call the routine to set the autentication token
    authtoken = api.getauthtoken(host,clientid,clientsecret)
    # Determine the group ID number
    groupid = api.getgroupid(host,authtoken,servergroupname)
    # Get a list of member servers
    serverlist = api.getserverlist(host,authtoken,groupid)
    # Populate the server list
    for s in serverlist["servers"]:
        serveridno = s["id"]
        print "========================="
        print "populate the server", serveridno
        print "========================="
        url = fn.provision(host,authtoken,accountname, serveridno, reqbody)
        serverolist.append(server.Server(s["hostname"],accountname,url))
    #Launch SAM scan
    for s in serverlist ["servers"]:
        serveridno = s["id"]
        print "\n\n"
        print "\nPlease wait: Luanching SAM scan"
        fn.sam(host, authtoken, serveridno)
    time.sleep(120)


    #Update SSH key
    if skey != '':
        for s in serverlist["servers"]:
            serveridno = s["id"]
            fn.updatessh(host, authtoken, accountname, serveridno, skey)
            print "\nFinished updating ssh"

    # All jobs submitted, notify user and check until all are done
    print "\n\n"
    print "All jobs have been submitted.  Now checking results.\nPlease stand by..."
    for i in xrange(1, iterations):
        totalservers,serversdone = fn.getjobstatus(serverolist)
        if totalservers == serversdone:
            continue
        print "Waiting on jobs to finish..."
        time.sleep(30)
        print serversdone ," of " , totalservers , " have finished."
        i = i+1
        for node in serverolist:
            print node
            # If the password is set, move along.  This is not the job you're looking for.
            if node.password != '':
                continue
            else:
                result, pw= fn.passwordcheck(str(node.url),str(authtoken),str(host))
                if result == "completed":
                    # If the password is empty and job is complete, something went wrong.  We resubmit the job.
                    if pw == ('' or None):
                        print "\nPassword failed to set. (specifically, it was set to: ",pw,")  Resubmitting job."
                        node.url = fn.provision(host,authtoken,accountname,accountcomment,accountgroups,serveridno,passwordlength,passwordspecialchar,passwordnumberchar,passworduppercasechar)
                    else:
                        node.password = pw
                # If the job fails, we resubmit.
                if result == "failed":
                    print "\nJob on ",node.name," failed!  Resubmitting"
                    print node.name , "\t" , node.password , "\t" , node.url
                    node.url = fn.provision(host,authtoken,accountname,accountcomment,accountgroups,serveridno,passwordlength,passwordspecialchar,passwordnumberchar,passworduppercasechar)

    print "\n Done!"
    fn.printresults(serverolist)

if __name__ == "__main__":
    main(sys.argv[1:])
