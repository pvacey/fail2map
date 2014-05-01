#!venv/bin/python


#Need to handle log rotation --> "if offset too high then zero"
#			     --> same IP over different logs files?
#				 --> store offset of ip.txt also to keep master list of IPs
#				 --> add new IPs to the list then come back to geolocate just like 
#				     it does to find the IPs in the first place
#				     --> this should work if getNewIP first then geolocate second

import time, re, simplekml
import requests, json
directory = '/home/paul/projects/geossh/'

def getNewIPs():
	#open file that holds offset (tell) value
	ftell = open (directory+'offset.txt')
	ftell.seek(0.0)
	offset = int(ftell.readline()) 
	#ftell.close()

	print "tell.txt --> "+ str(offset)

	#open the log at the offset point
	flog = open (directory+'auth.log') #make a symlink to directory
	#find current endpoint of file
	flog.seek(0,2)
	logLength = flog.tell()
	#if current endpoint is less than old one, start at 0 again (new log file)
	if logLength < offset:
		offset = 0
	
	print "starting log from --> " + str(offset)
	
	flog.seek(offset,0)
	tmp = flog.read()
	newOffset = str(flog.tell())
	flog.close()

	print "end of log --> "+  newOffset

	#this also checks to see where the end of ip.txt file is, and starts fresh if past end	
	ipOffset = ftell.readline() 
	print ipOffset
	fip = open (directory+'ip.txt')
	fip.seek(0,2)
	ipLogLength = fip.tell()
	if ipOffset > ipLogLength:
		fip.close()
		reOpen = True
		#fip = open(directory+'ip.txt','w')
		ipOffset = 0
	if reOpen:
		fip = open(directory+'ip.txt','r+')

	print "start ip.txt -->" + str(ipOffset)
	fip.seek(int(ipOffset),0)
	oldIP = fip.read()
	ipOffset = str(fip.tell()) 	

	#overwrite the offset value
	ftell = open (directory+'offset.txt','w')
	ftell.write(newOffset+"\n")
	ftell.write(ipOffset)
	ftell.close()

	#grab the IPs from the log
	tmp = re.findall("Invalid .+ from (.+)", tmp)

	ipList = []
	previous = ""
	#remove duplicates
	for ip in sorted(tmp):
		#make sure each ip is different from the one before it
		if ip != previous:
			ipList.append(ip)	
			previous = ip

	#checks for duplicates
	oldIP = oldIP.split()
	print oldIP
	newIpList = list(set(ipList) - set(oldIP))  
	#newIpList = ipList 

	print newIpList

	#!!!!!
	#Can probably just keep this as a list...?
	#!!!!!!

	#write only the new ip address to the file
	outpoot =  open(directory+'ip.txt' , 'a')
	for ip in newIpList:
		outpoot.write(ip+"\n")
		geolocateIP(ip)
	outpoot.close()
	return

def geolocateIP(ip):
	r = requests.get('https://freegeoip.net/json/'+ip)
	json_data = r.json()
#	data = json.load(json_data)
#	print data["latitude"]
	lon = json_data["longitude"]
	lat = json_data["latitude"]
	
	print ip + "    " + str(lat) + "  " + str(lon)	
	
	#write to database 
	
	return

def updateKML():
	f = open (directory+"/ip.txt")
	ipList = f.read()
	ipList = ipList.split()

	kml = simplekml.Kml()
	for ip in ipList:
		kml.newpoint(name=ip, coords=[(33.343434,-33.909090)])	
		kml.save(directory+"/test.kml")

	print kml.kml()
	return


getNewIPs()	
#geolocateIP()

# IF NEW IP ADDED THEN UPDATE (ADD A GLOBAL BOOLEAN )
updateKML()
