import sys
import os
import json

class Cache:
	
	def __init__ (self, path):
		self.data = {}
		self.changeCount = 0
		self.maximumUnsavedChanges = 100
		
		basePath = ''
		if hasattr(sys.modules['__main__'], '__file__'):
			basePath = sys.modules['__main__'].__file__
		self.path = os.path.normpath(basePath + path)
		
		self.read()
	
	
	def read (self):
		if os.path.exists(self.path):
			cacheFile = open(self.path)
			try:
				self.data = json.load(cacheFile)
				print '* Cache ' + self.path + ': ' + str(len(self.data)) + ' entries read'
			except:
				print 'Could not parse cache from ' + self.path
			cacheFile.close()
		else:
			print 'Could not load cache at ' + self.path
	
	
	def write (self):
		if self.changeCount > 0:
			cacheFile = open(self.path, 'w')
			json.dump(self.data, cacheFile, indent=2, separators=(',', ': '), sort_keys=True)
			cacheFile.close()
			print '* Cache ' + self.path + ': ' + str(len(self.data)) + ' entries written'
			self.changeCount = 0
	
	
	def getItem (self, key):
		result = None
		if self.data.has_key(key):
			result = self.data[key]
		return result
	
	
	def setItem (self, key, value):
		self.data[key] = value
		self.changeCount = self.changeCount + 1
		
		if self.changeCount >= self.maximumUnsavedChanges:
			self.write()
