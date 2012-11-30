# -*- coding: utf-8 -*-

import HTMLParser, urllib2, copy, sys, time, os

class sanntid(HTMLParser.HTMLParser):
	get_data = False
	sanntid_data = []
	grand_iterator = -2;

	local_iterator = 0;
	local_map = {};

	def handle_starttag(self, tag, attrs):
		if tag=="a" and len(attrs) > 0:

			#unique identifier for line containing sanntid data.
			if attrs[0] == ('class', 'tq'):
				self.get_data = True
				self.local_iterator += 1;
		else:
			self.get_data = False

		if tag=="tr":
			self.local_iterator = -1;
			self.grand_iterator+=1;
		
	def handle_endtag(self, tag):
		self.get_data = False
		if tag=="tr":
			self.local_iterator = 0;
			if (self.grand_iterator >= 0): 
				self.sanntid_data.append(copy.deepcopy(self.local_map))
			self.local_map = {}

	def handle_data(self, data):
		if (self.get_data):
			if self.local_iterator == 0:
				self.local_map["time"] = data
			elif self.local_iterator == 1:
				self.local_map["route"] = "[" + data + "] ";
			elif self.local_iterator == 3:
				self.local_map["route"] += data;
	
	def return_data(self):
		return self.sanntid_data
				


url_map = {"blindern" : "http://reiseplanlegger.ruter.no/no/Stoppested/%283010360%29Blindern%20%5BT-bane%5D%20%28Oslo%29/Avganger/_timetag_#st:1,zo:0,sp:0}"}

filter_map = {"blindern_west" : ["Sognsvann", "Ringen", "Storo"],
	      "blindern_east"  : ["Mortensrud", "Bergkrystallen", "Vestli"]
             }

def get_dt(TIME):
	dt = int(TIME.split(".")[1]) - int(time.strftime("%M"))
	dt += 60*(int(TIME.split(".")[0]) - int(time.strftime("%H")))
	return dt

if __name__ == "__main__":

	#CML parse
	direction = ""

	if len(sys.argv) > 1:
		direction = sys.argv[1]
	if direction in ["west", "v", "w", "vest"]:
		direction = "west"
	elif direction in ["east", "e", "ø", "øst"]:
		direction = "east"
	else:
		print "Usage: python %s direction" % sys.argv[0]
		print "\ndirections: west/v/w/vest or east/e/ø/øst\n"
		sys.exit(1)
	

	#get URL
	
	location = "blindern"
	timetag = "%s%s%s%s%s" % (time.strftime("%d"), time.strftime("%m"), time.strftime("%Y"), time.strftime("%H"), time.strftime("%M"))
	url = url_map[location].replace("_timetag_", timetag)
	

	#fetch data

	parser = sanntid()
	opener = urllib2.urlopen(url)

	parser.feed(opener.read())
	
	sanntid_data = parser.return_data()
	parser.close()





	#Output
	stdout = "\r"
	routes = []
	spacing = 20
	for data in sanntid_data:
		if data["route"].split()[1] in filter_map["_".join([location, direction])]: 
		
			if data["route"] not in routes:
				routes.append(data["route"])

	stdout += "\n"
	stdout += "%s"*len(routes) % tuple([route.center(spacing) for route in routes]) + "\n"
	stdout +="\n"	

	times = []
	for i in range(len(routes)):
		times.append([])
	for data in sanntid_data:
		for i in range(len(routes)):
			if data["route"] == routes[i]:
				times[i].append(data["time"])

	i = 0
	for timeset in zip(*times[:]):
		
		stdout += "%s"*len(routes) % tuple([(TIME + (" (%2dm)".replace(" ( 0m)", " (now)") % get_dt(TIME))*(i<3)).center(spacing) for TIME in timeset]) + "\n"
		i+=1
	
	sys.stdout.write(stdout)





















