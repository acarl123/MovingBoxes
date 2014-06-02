# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version Nov  6 2013)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
from NavigatorFloatCanvas import NavigatorFloatCanvas

###########################################################################
## Class MyFrame1
###########################################################################

class MyFrame1 ( wx.Frame ):

	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 725,558 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )

		self.m_menubar1 = wx.MenuBar( 0 )
		self.menuFile = wx.Menu()
		self.menuOpen = wx.MenuItem( self.menuFile, wx.ID_ANY, u"Open", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuFile.AppendItem( self.menuOpen )

		self.menuAddObject = wx.MenuItem( self.menuFile, wx.ID_ANY, u"Add object", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuFile.AppendItem( self.menuAddObject )

		self.menuExport = wx.MenuItem( self.menuFile, wx.ID_ANY, u"Export image", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuFile.AppendItem( self.menuExport )

		self.menuSaveAs = wx.MenuItem( self.menuFile, wx.ID_ANY, u"Save as", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuFile.AppendItem( self.menuSaveAs )

		self.menuSave = wx.MenuItem( self.menuFile, wx.ID_ANY, u"Save", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuFile.AppendItem( self.menuSave )

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

		self.menuUndo = wx.MenuItem( self.menuEdit, wx.ID_ANY, u"Undo", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuEdit.AppendItem( self.menuUndo )

		self.menuDelete = wx.MenuItem( self.menuEdit, wx.ID_ANY, u"Delete", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuEdit.AppendItem( self.menuDelete )

		self.menuEdit.AppendSeparator()

		self.menuZoom = wx.MenuItem( self.menuEdit, wx.ID_ANY, u"Zoom", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuEdit.AppendItem( self.menuZoom )

		self.m_menubar1.Append( self.menuEdit, u"Edit" )

		self.menuView = wx.Menu()
		self.menuShowLegend = wx.MenuItem( self.menuView, wx.ID_ANY, u"Show Legend", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuView.AppendItem( self.menuShowLegend )

		self.m_menubar1.Append( self.menuView, u"View" )

		self.menuHelp = wx.Menu()
		self.menuAbout = wx.MenuItem( self.menuHelp, wx.ID_ANY, u"About", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuHelp.AppendItem( self.menuAbout )

		self.menuUserGuide = wx.MenuItem( self.menuHelp, wx.ID_ANY, u"User Guide", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuHelp.AppendItem( self.menuUserGuide )

		self.m_menubar1.Append( self.menuHelp, u"Help" )

		self.SetMenuBar( self.m_menubar1 )

		self.m_statusBar1 = self.CreateStatusBar( 1, wx.ST_SIZEGRIP, wx.ID_ANY )
		bSizer1 = wx.BoxSizer( wx.VERTICAL )

		self.m_panel1 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer1.Add( self.m_panel1, 1, wx.EXPAND |wx.ALL, 5 )

		self.NavCanvas = NavigatorFloatCanvas(self, Debug=0, BackgroundColor=(173, 173, 173))
		bSizer1.Add( self.NavCanvas, 1, wx.ALL|wx.EXPAND, 5 )

		self.SetSizer( bSizer1 )
		self.Layout()

		self.Centre( wx.BOTH )

	def __del__( self ):
		pass

