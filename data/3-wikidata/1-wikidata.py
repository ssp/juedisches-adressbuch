#!/usr/bin/env python

import cache
import csvutf8
import os
import urllib
import urllib2
import json
import pprint

wikidataSearchURL = 'https://www.wikidata.org/w/api.php?';
wikidataIDBaseURL = 'https://www.wikidata.org/wiki/Special:EntityData/'

# cache
wikidataSearchCachePath = '/../wikidataSearchCache.json'
wikidataIDCachePath = '/../wikidataIDCache.json'
searchCache = cache.Cache(wikidataSearchCachePath)
IDCache = cache.Cache(wikidataIDCachePath)


# CSV fields
personIndexes = {'nr': 0, 'id':2, 'surname':3, 'firstname':4, 'street':6, 'bezirk':7, 'job':8, 'extras':9, 'remarks':10}

# read and process person list
addressReader = csvutf8.UnicodeReader(open(os.path.normpath(__file__ + '/../../0-adressen.csv')), delimiter='\t')
addressReader.next()

# run wikidata searches
for person in addressReader:
	fullname = person[personIndexes['firstname']] + ' ' + person[personIndexes['surname']]
	if not searchCache.getItem(fullname):
		searchURL = wikidataSearchURL + urllib.urlencode({
			'action': 'wbsearchentities',
			'language': 'de',
			'format': 'json',
			'search': fullname.encode('utf-8')
		})
		try:
			searchResultsDownload = urllib2.urlopen(searchURL)
			searchResultsText = searchResultsDownload.read()
			searchResults = json.loads(searchResultsText)
			searchCache.setItem(fullname, searchResults)
			print fullname + ' (' + str(len(searchResults['search'])) + ')'
		except:
			print 'failed to load ' + searchURL

searchCache.write()

# load wikidata items
for name, searchResults in searchCache.data.iteritems():
	for searchResult in searchResults['search']:
		wikidataID = searchResult['id']
		if not IDCache.getItem(wikidataID):
			IDURL = wikidataIDBaseURL + wikidataID + '.json'
			try:
				IDDownload = urllib2.urlopen(IDURL)
				IDText = IDDownload.read()
				IDInfo = json.loads(IDText)
				IDCache.setItem(wikidataID, IDInfo)
				print name + ' -> ' + wikidataID
			except:
				print 'failed to load ' + IDURL

IDCache.write()


# create result CSV
lines = [['ID', 'Wikidata ID', 'Name', 'Wikidata Name', 'Beziehung Namen', 'von', 'bis', 'Jahre plausibel', 'typ']]
dateParseString = '+0000000%Y-%m-%dT%H:%M:%SZ'
addressReader = csvutf8.UnicodeReader(open(os.path.normpath(__file__ + '/../../0-adressen.csv')), delimiter='\t')
addressReader.next()
for person in addressReader:
	fullname = person[personIndexes['firstname']] + ' ' + person[personIndexes['surname']]
	personData = searchCache.getItem(fullname)
	if personData:
		for result in personData['search']:
			wikidataID = result['id']
			print wikidataID + ' (' + fullname + ')'
			wikidataItem = IDCache.getItem(wikidataID)
			if wikidataItem:
				info = wikidataItem['entities'][wikidataID]
				personRecord = [person[personIndexes['id']], wikidataID, fullname]
				
				wikidataName = ''
				if info.has_key('labels'):
					labels = info['labels']
					if labels.has_key('de'):
						wikidataName = labels['de']['value']
					else:
						wikidataName = labels[labels.keys()[0]]['value']
				personRecord += [wikidataName]
				
				beziehungNamen = 'unklar'
				print fullname + ' / ' + wikidataName
				if fullname == wikidataName:
					beziehungNamen = 'identisch'
				elif len(fullname) > 0 and len(wikidataName) and fullname.split()[-1] == wikidataName.split()[-1]:
					beziehungenNamen = 'Nachname identisch'
				
				if info.has_key('claims'):
					claims = info['claims']
					
					birthDate = '-'
					birthYear = 0
					if claims.has_key('P569'):
						# print str(len(claims['P569'])) + ' birth dates'
						mainsnak = claims['P569'][0]['mainsnak']
						if mainsnak.has_key('datavalue'):
							dateString = mainsnak['datavalue']['value']['time']
							birthDate = dateString[8:18]
							birthYear = int(birthDate[0:4])
					
					deathDate = '-'
					deathYear = 0
					if claims.has_key('P570'):
						# print str(len(claims['P570'])) + ' death dates'
						mainsnak = claims['P570'][0]['mainsnak']
						if mainsnak.has_key('datavalue'):
							dateString = mainsnak['datavalue']['value']['time']
							deathDate = dateString[8:18]
							deathYear = int(deathDate[0:4])
					
					jahrePlausibel = 'unklar'
					if birthDate == '-' and deathDate == '-':
						jahrePlausibel = 'unbekannt'
					elif birthYear > 1830 and birthYear < 1931 and deathYear > 1931:
						jahrePlausibel = 'plausibel'
					elif deathYear > 1930 and birthYear < 1931:
						jahrePlausibel = 'plausibel'
					elif birthYear < 1820 or birthYear > 1931 or deathYear < 1931:
						jahrePlausibel = 'nein'
					
					typeLabel = '-'
					if claims.has_key('P31'):
						# print str(len(claims['P31'])) + ' types'
						mainsnak = claims['P31'][0]['mainsnak']
						if mainsnak.has_key('datavalue'):
							typeID = 'Q' + str(mainsnak['datavalue']['value']['numeric-id'])
							if not IDCache.getItem(typeID):
								IDURL = wikidataIDBaseURL + typeID + '.json'
								try:
									IDDownload = urllib2.urlopen(IDURL)
									IDText = IDDownload.read()
									IDInfo = json.loads(IDText)
									IDCache.setItem(typeID, IDInfo)
									print 'loaded ' + IDURL
								except:
									print 'failed to load ' + IDURL
							typeItem = IDCache.getItem(typeID)
							if typeItem:
								labels = typeItem['entities'][typeID]['labels']
								if labels.has_key('de'):
									typeLabel = labels['de']['value']
								else:
									typeLabel = labels[labels.keys()[0]]['value']
							else:
								typeItem = typeID
						
					personRecord += [beziehungNamen, birthDate, deathDate, jahrePlausibel, typeLabel]
				
				else:
					personRecord += ['', '', '']
					
				
				lines += [personRecord]

IDCache.write()


# write result file CSV
QFile = open(os.path.normpath(__file__ + '/../wikidataResults.csv'), 'w')
QWriter = csvutf8.UnicodeWriter(QFile)
QWriter.writerows(lines)
QFile.close()
