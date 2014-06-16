#!/usr/bin/python
import wx
import ast
from StringIO import *
import os
import imp
from sets import *
import Icons

class ScriptFile:
	def __init__(self,filename,loader,special):
		tree = ast.parse(''.join(open(filename)))
		self.Name = os.path.basename(filename)
		self.File = filename
		self.Description = ""
		self.IsRunOnce = False
		self.ParseDocString(ast.get_docstring(tree))
		self.MenuItem = None
		self.Loader = loader
		self.Special = special
		
		
	def ParseDocString(self,docstr):
		if (docstr == None):
			return
	
		#print "Doc: " + docstr
		buf = StringIO(docstr)
		lines = buf.readlines()
		
		for line in lines:
			splitpoint = line.find(":")
			prop = line[:splitpoint].lower()
			value = line[splitpoint+1:].strip()
			if prop == "name":
				self.Name = value
			elif prop == "desc":
				self.Description = value
			elif prop == "runonce":
				self.IsRunOnce = (value.lower() == "true")

	def OnClicked(self,e):
		self.Loader.ExecuteScript(self.File)
class ScriptLoader:
	def __init__ (self,navigator, menu):
		self.Navigator = navigator
		self.Menu = menu
		self.Scripts = []
		self.RunScripts = Set()
		self.ScriptModules = []
		self.SpecialDir = self.Navigator.Config.Get("specialscriptdir")
		
	def LoadMenu (self):
		#clear the menu
		for s in self.Scripts:
			self.Menu.RemoveItem(s.MenuItem)
		
		self.Scripts = []
		if (os.path.exists("./Scripts")):
			for filename in os.listdir("./Scripts"):
				sf = ScriptFile("./Scripts/" + filename,self,False)
				if (sf.IsRunOnce):
					if sf.File not in self.RunScripts:
						self.RunScripts.add(sf.File)
						self.ExecuteScript(sf.File)
				else:
					self.Scripts.append(sf)
					
		if (os.path.exists(self.SpecialDir)):
			for filename in os.listdir(self.SpecialDir):
				sf = ScriptFile(self.SpecialDir + "/" + filename,self,True)
				if (sf.IsRunOnce):
					if sf.File not in self.RunScripts:
						self.RunScripts.add(sf.File)
						self.ExecuteScript(sf.File)
				else:
					self.Scripts.append(sf)
		
		
		self.Scripts = sorted(self.Scripts, key=lambda s: s.Name)
		
		for s in reversed(self.Scripts):
			s.MenuItem = wx.MenuItem(self.Menu,wx.ID_ANY,s.Name,s.Description)
			if (s.Special):
				s.MenuItem.SetBitmap(Icons.getstarBitmap())
			self.Menu.PrependItem(s.MenuItem)
			self.Navigator.Bind(wx.EVT_MENU,s.OnClicked,s.MenuItem)
		
		
	def ExecuteScript (self, script):
		pseudo_module = imp.new_module(script)
		vars(pseudo_module).update(self.Navigator.InjectedImports)
		f = open(script,'r')
		exec f.read() in vars(pseudo_module)
		f.close ()
		self.ScriptModules.append(pseudo_module)
		