#!venv/bin/python

import time, re
directory = '/home/paul/projects/geossh/'

def getNewIPs():
	ftell = open (directory+'tell.txt')
	ftell.seek(0.0)
	offset = int(ftell.read()) 
	print "tell.txt --> "+ str(offset)

	flog = open (directory+'auth.log') #make a symlink to directory
	#open the log at the offset
	flog.seek(offset,0)
	tmp = flog.read()

	#save the new end of the log
	print "end of log --> "+  str(flog.tell())
	#re-open to overwrite file
	ftell.close()
	ftell = open (directory+'tell.txt','w')
	ftell.write(str(flog.tell()))


	#DO NOT NEED ANYMORE I THINK

	#fip = open (directory+'ip.txt')
	#fip.seek(0.0)
	#oldIP = fip.read()

	tmp = re.findall("Invalid .+ from (.+)", tmp)

	ipList = []
	#start as blank
	previous = ""
	for ip in sorted(tmp):
		#make sure this isnt the string as before it
		if ip != previous:
			ipList.append(ip)	
			previous = ip

	#oldIP = oldIP.split()
	#newIpList = list(set(ipList) - set(oldIP))  

	#newIpList = ipList 

	print ipList
	#write only the new ip address to the file
	outpoot =  open(directory+'ip.txt' , 'w')
	for ip in ipList:
		outpoot.write(ip+"\n")
	outpoot.close()
	return

def geolocateIPs():
	return


def updateKML():
	return

getNewIPs()	
#geolocateIPs()
#updateKML()
