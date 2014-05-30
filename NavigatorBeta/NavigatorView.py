# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Nov  6 2013)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class NavigatorFrame
###########################################################################

class NavigatorFrame ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 725,558 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		self.m_menubar1 = wx.MenuBar( 0 )
		self.menuFile = wx.Menu()
		self.menuExport = wx.MenuItem( self.menuFile, wx.ID_ANY, u"Export Image", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuFile.AppendItem( self.menuExport )
		
		self.menuExit = wx.MenuItem( self.menuFile, wx.ID_ANY, u"Exit", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuFile.AppendItem( self.menuExit )
		
		self.m_menubar1.Append( self.menuFile, u"File" ) 
		
		self.menuEdit = wx.Menu()
		self.menuCut = wx.MenuItem( self.menuEdit, wx.ID_ANY, u"Cut", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuEdit.AppendItem( self.menuCut )
		
		self.menuCopy = wx.MenuItem( self.menuEdit, wx.ID_ANY, u"Copy", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuEdit.AppendItem( self.menuCopy )
		
		self.menuPaste = wx.MenuItem( self.menuEdit, wx.ID_ANY, u"Paste", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuEdit.AppendItem( self.menuPaste )
		
		self.menuDelete = wx.MenuItem( self.menuEdit, wx.ID_ANY, u"Delete", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuEdit.AppendItem( self.menuDelete )
		
		self.menuEdit.AppendSeparator()
		
		self.menuZoom = wx.MenuItem( self.menuEdit, wx.ID_ANY, u"Zoom", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuEdit.AppendItem( self.menuZoom )
		
		self.m_menubar1.Append( self.menuEdit, u"Edit" ) 
		
		self.SetMenuBar( self.m_menubar1 )
		
		self.m_statusBar1 = self.CreateStatusBar( 1, wx.ST_SIZEGRIP, wx.ID_ANY )
		bSizer1 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_panel1 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer1.Add( self.m_panel1, 1, wx.EXPAND |wx.ALL, 5 )
		
		
		self.SetSizer( bSizer1 )
		self.Layout()
		
		self.Centre( wx.BOTH )
	
	def __del__( self ):
		pass
	

