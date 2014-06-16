#!/usr/bin/python
import sys
import io
import os

class DirectoryToken:
	def __init__(self,name):
		self.Name = name;

	def get (self):
		if not os.path.exists(self.Name + ".dirtoken"):
			open(self.Name + ".dirtoken","w").close ()
		f = open(self.Name + ".dirtoken","r")
		dir = f.read()
		f.close()
		return dir

	def update (self, path):
		f = open(self.Name + ".dirtoken","w")
		dir = os.path.dirname(path)
		f.write(dir)
		f.close ()

