import sys
import os

class ConfigFile:
	def __init__ (self,file):
		self.Attrs = dict ()
		
		if (not os.path.exists(file)):
			return
		
		f = open(file,"r")
		
		for line in f.readlines():
			splitpoint = line.find(":")
			prop = line[:splitpoint].lower()
			value = line[splitpoint+1:].strip()
			
			self.Attrs[prop] = value
			
	
	def Get (self,prop):
		return self.Attrs[prop.lower()]