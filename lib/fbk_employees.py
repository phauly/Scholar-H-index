# -*- coding: utf-8 -*-
#
# Paolo Massa   http://www.gnuband.org
#
# See the file LICENSE for information on usage and redistribution of
# this file, and for a DISCLAIMER OF ALL WARRANTIES.
#
# This script parses the list of FBK employees at http://www.fbk.eu/people?group=all
# and returns an array of them, possibly excluding those in some units

import urllib2
from aux import BeautifulSoup

def get_list_of_fbk_employee(exclude=[]):
	try:
		list = []
		response = urllib2.urlopen('http://www.fbk.eu/people?group=all')
		s = response.read()
		soup = BeautifulSoup.BeautifulSoup(s)
		table = soup.findAll(id='people')[0].find('table')
		rows = table.findAll('tr')
		for row in rows[1:]:
			tds = row.fetch("td")
			surname = tds[0].contents[0].string.strip()
			name = tds[0].contents[1].string.strip()
			if len(tds[1].contents) > 0:
				unit = tds[1].contents[0].string.strip()
			else:
				unit = ""
			#print surname.encode('utf8','ignore'), unit.encode('utf8','ignore')
			if not unit in exclude:
				list.append( (surname,name) )
		return list
	except:
		print "PROBLEM"
def main():
	employees = get_list_of_fbk_employee(exclude=['Amministrazione','Legale','Personale','Patrimonio'])
	#employees = get_list_of_fbk_employee()
	print "\n".join([((e[0].encode('utf8','ignore'))+"+"+(e[1].encode('utf8','ignore'))) for e in employees])

if __name__ == "__main__":
	main()
