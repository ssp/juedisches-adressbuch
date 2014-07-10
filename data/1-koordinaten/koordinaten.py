#!/usr/bin/env python

import cache
import csvutf8
import os
import urllib
import urllib2
import json
import time

nominatimBaseURL = 'http://ubuntu.local/nominatim/search.php?'
sleepInterval = 0
#nominatimBaseURL = 'http://nominatim.openstreetmap.org/search.php?'
#sleepInterval = 1

results = [['id', 'lat', 'lon']]
browserResults = []

# cache
cachePath = '/../cache.json'
addressCache = cache.Cache(cachePath)


# look up coordinates
def bestCoordinate (coordinateInfos):
	best = None
	for index, coordinateInfo in enumerate(coordinateInfos):
		if index == 0:
			best = coordinateInfo
		if not best['type'] == 'house' and coordinateInfo['type'] == 'house':
			best = coordinateInfo
	return best


def coordinatesForAddress (address):
	global sleepInterval
	
	if not addressCache.getItem(address):
		time.sleep(sleepInterval)
		URL = nominatimBaseURL + urllib.urlencode({'format':'json', 'q':address.encode('utf-8')})
		coordinateDownload = urllib2.urlopen(URL)
		jsonText = coordinateDownload.read()
		coordinateInfos = json.loads(jsonText)
		best = bestCoordinate(coordinateInfos)
		cacheDict = {'response': coordinateInfos}
		if best and best.has_key('lat') and best.has_key('lon'):
			cacheDict['lat'] = best['lat']
			cacheDict['lon'] = best['lon']
		addressCache.setItem(address, cacheDict)

	return addressCache.getItem(address)


personIndexes = {'nr': 0, 'id':2, 'surname':3, 'firstname':4, 'street':6, 'bezirk':7, 'job':8, 'extras':9, 'remarks':10}

def coordinatesForPerson (person):
	address = person[personIndexes['street']] + ', Berlin'
	coordinates = coordinatesForAddress(address)
	
	return coordinates


def processPerson (person):
	global results, browserResults, personIndexes
	
	coordinates = coordinatesForPerson(person)
	personID = person[personIndexes['id']]
	CSVResult = [personID]
	if coordinates.has_key('lat') and coordinates.has_key('lon'):
		CSVResult += [coordinates['lat'], coordinates['lon']]
		
		fullname = person[personIndexes['firstname']] + ' ' + person[personIndexes['surname']]
		address = person[personIndexes['street']]
		if person[personIndexes['bezirk']] != '':
			address += ' (' + person[personIndexes['bezirk']] + ')'
		browserResult = [personID, coordinates['lat'], coordinates['lon'], fullname, person[personIndexes['job']], address]
		browserResults += [browserResult]
	else:
		CSVResult += ['', '']
			
	results += [CSVResult]



# read and process person list
addressReader = csvutf8.UnicodeReader(open(os.path.normpath(__file__ + '/../../0-adressen.csv')), delimiter='\t')
addressReader.next()
for person in addressReader:
	processPerson(person)


# write result file CSV
koordinatenFile = open(os.path.normpath(__file__ + '/../koordinaten.csv'), 'w')
koordinatenWriter = csvutf8.UnicodeWriter(koordinatenFile)
koordinatenWriter.writerows(results)
koordinatenFile.close()

# write JSON for browser use
jsonFile = open(os.path.normpath(__file__ + '/../koordinaten.json'), 'w')
json.dump(browserResults, jsonFile)
jsonFile.close()	

# write cache JSON
addressCache.write()
