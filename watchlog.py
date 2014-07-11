#!venv/bin/python


#Need to handle log rotation --> "if offset too high then zero"
#			     --> same IP over different logs files?
#				 --> store offset of ip.txt also to keep master list of IPs
#				 --> add new IPs to the list then come back to geolocate just like 
#				     it does to find the IPs in the first place
#				     --> this should work if getNewIP first then geolocate second

import time, re, simplekml
import requests, json, sqlite3 as lite
from jinja2 import Environment, PackageLoader
directory = '/home/paul/projects/geossh/'

def getNewIPs():

	update = False

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

	#connect to IP database
	db = connect_db('data.db')
	cur = db[0]
	con = db[1]
	
	#get the list of IPs from the database
	cur.execute('SELECT ip FROM coordinates;')
	oldIP = []
	tmp_oldIP = cur.fetchall()
	for ip in tmp_oldIP:
		oldIP.append(ip[0].encode("utf-8"))	

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

	newIpList = list(set(ipList) - set(oldIP))  

	print "old IPs --> " + str(oldIP)
	print "new IPs --> " + str(newIpList)

	#write only the new ip address to the file
	for ip in newIpList:
		update = True
		#look up the ip
		coords = geolocateIP(ip)
		#add to database
		entry = [ip, coords[0], coords[1] ]
		cur.execute('insert into coordinates values(?,?,?)', entry)

	#save db changes
	con.commit()
	con.close()
	
	#update the KML if any new IPs were added
#	if update:
#		updateKML()
	return 

def geolocateIP(ip):
	r = requests.get('https://freegeoip.net/json/'+ip)
	json_data = r.json()
	lat = json_data["latitude"]
	lon = json_data["longitude"]
	
	print ip + "    " + str(lat) + "  " + str(lon)	
	
	return lat, lon

def updateKML():
	#connect to IP database
	db = connect_db('data.db')
	cur = db[0]
	con = db[1]
	
	#get the list of IPs from the database
	cur.execute('SELECT * FROM coordinates;')
	ipList = cur.fetchall()

	kml = simplekml.Kml()
	for ip in ipList:
		kml.newpoint(name=ip[0].encode('utf-8'),description = "worthless piece of shit", coords=[(str(ip[1])+"000",str(ip[2])+"000", "0")] )	

	kml.save(directory+"/test.kml")
	print kml.kml()
	return

def updateMap():
	#connect to IP database
	db = connect_db('data.db')
	cur = db[0]
	con = db[1]
	
	#get the list of IPs from the database
	cur.execute('SELECT * FROM coordinates;')
	points = cur.fetchall()

	env = Environment(loader=PackageLoader('watchlog', 'templates'))
	template = env.get_template('map.jinja')

	html = open("test.html",'w')
	html.write(template.render(points=points))

	return

def connect_db(db):
	con = None
	try:
		con = lite.connect(db)
		cur = con.cursor()
		return cur, con
	except lite.Error, e:
		print "Error %s:" %e.args[0]
		return


#getNewIPs()
updateMap()
#updateKML()
