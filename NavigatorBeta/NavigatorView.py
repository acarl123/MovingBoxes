# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Feb 26 2014)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class NavigatorFrame
###########################################################################
from NavigatorFloatCanvas import NavigatorFloatCanvas


class NavigatorFrame ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"EFS Navigator", pos = wx.DefaultPosition, size = wx.Size( 800,600 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		self.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNTEXT ) )
		
		bSizer1 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_splitter1 = wx.SplitterWindow( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.SP_LIVE_UPDATE )
		self.m_splitter1.Bind( wx.EVT_IDLE, self.m_splitter1OnIdle )
		self.m_splitter1.SetMinimumPaneSize( 10 )
		
		# self.m_panel1 = wx.Panel( self.m_splitter1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		# bSizer3 = wx.BoxSizer( wx.VERTICAL )
		#
		# self.NavCanvas = NavigatorFloatCanvas(self, Debug=0, BackgroundColor=(173, 173, 173))
		# bSizer3.Add( self.NavCanvas, 1, wx.ALL|wx.EXPAND, 5 )
		
		self.NavCanvas = NavigatorFloatCanvas(self.m_splitter1, Debug=0, BackgroundColor=(173, 173, 173))
		# self.NavCanvas.SetSizer( bSizer3 )
		self.NavCanvas.Layout()
		# bSizer3.Fit( self.m_panel1 )
		self.m_panel2 = wx.Panel( self.m_splitter1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer2 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_listCtrl1 = wx.ListCtrl( self.m_panel2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_REPORT )
		bSizer2.Add( self.m_listCtrl1, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		self.m_panel2.SetSizer( bSizer2 )
		self.m_panel2.Layout()
		bSizer2.Fit( self.m_panel2 )
		self.m_splitter1.SplitVertically( self.NavCanvas, self.m_panel2, 700 )
		bSizer1.Add( self.m_splitter1, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( bSizer1 )
		self.Layout()
		self.m_menubar1 = wx.MenuBar( 0 )
		self.fileMenu = wx.Menu()
		self.menuOpen = wx.MenuItem( self.fileMenu, wx.ID_ANY, u"Open", wx.EmptyString, wx.ITEM_NORMAL )
		self.fileMenu.AppendItem( self.menuOpen )
		
		self.menuAddObject = wx.MenuItem( self.fileMenu, wx.ID_ANY, u"Add Node", wx.EmptyString, wx.ITEM_NORMAL )
		self.fileMenu.AppendItem( self.menuAddObject )
		
		self.menuExport = wx.MenuItem( self.fileMenu, wx.ID_ANY, u"Export as", wx.EmptyString, wx.ITEM_NORMAL )
		self.fileMenu.AppendItem( self.menuExport )
		
		self.menuSaveAs = wx.MenuItem( self.fileMenu, wx.ID_ANY, u"Save as", wx.EmptyString, wx.ITEM_NORMAL )
		self.fileMenu.AppendItem( self.menuSaveAs )
		
		self.menuSave = wx.MenuItem( self.fileMenu, wx.ID_ANY, u"Save", wx.EmptyString, wx.ITEM_NORMAL )
		self.fileMenu.AppendItem( self.menuSave )
		
		self.menuExit = wx.MenuItem( self.fileMenu, wx.ID_ANY, u"Exit", wx.EmptyString, wx.ITEM_NORMAL )
		self.fileMenu.AppendItem( self.menuExit )
		
		self.m_menubar1.Append( self.fileMenu, u"File" ) 
		
		self.editMenu = wx.Menu()
		self.deleteMenuItem = wx.MenuItem( self.editMenu, wx.ID_ANY, u"Delete", wx.EmptyString, wx.ITEM_NORMAL )
		self.editMenu.AppendItem( self.deleteMenuItem )
		
		self.copyMenuItem = wx.MenuItem( self.editMenu, wx.ID_ANY, u"Copy", wx.EmptyString, wx.ITEM_NORMAL )
		self.editMenu.AppendItem( self.copyMenuItem )
		
		self.undoMenuItem = wx.MenuItem( self.editMenu, wx.ID_ANY, u"Undo", wx.EmptyString, wx.ITEM_NORMAL )
		self.editMenu.AppendItem( self.undoMenuItem )
		
		self.m_menubar1.Append( self.editMenu, u"Edit" ) 
		
		self.viewMenu = wx.Menu()
		self.showLegendMenuItem = wx.MenuItem( self.viewMenu, wx.ID_ANY, u"Show Legend", wx.EmptyString, wx.ITEM_NORMAL )
		self.viewMenu.AppendItem( self.showLegendMenuItem )
		
		self.hideLegendMenuItem = wx.MenuItem( self.viewMenu, wx.ID_ANY, u"Hide Legend", wx.EmptyString, wx.ITEM_NORMAL )
		self.viewMenu.AppendItem( self.hideLegendMenuItem )
		
		self.latestRevisionMenuItem = wx.MenuItem( self.viewMenu, wx.ID_ANY, u"Latest Revision Mode", wx.EmptyString, wx.ITEM_NORMAL )
		self.viewMenu.AppendItem( self.latestRevisionMenuItem )
		
		self.allRevisionMenuItem = wx.MenuItem( self.viewMenu, wx.ID_ANY, u"All Revisions Mode", wx.EmptyString, wx.ITEM_NORMAL )
		self.viewMenu.AppendItem( self.allRevisionMenuItem )
		
		self.noRevisionMenuItem = wx.MenuItem( self.viewMenu, wx.ID_ANY, u"No Revision Mode", wx.EmptyString, wx.ITEM_NORMAL )
		self.viewMenu.AppendItem( self.noRevisionMenuItem )
		
		self.m_menubar1.Append( self.viewMenu, u"View" ) 
		
		self.helpMenu = wx.Menu()
		self.aboutMenuItem = wx.MenuItem( self.helpMenu, wx.ID_ANY, u"About", wx.EmptyString, wx.ITEM_NORMAL )
		self.helpMenu.AppendItem( self.aboutMenuItem )
		
		self.userGuideMenuItem = wx.MenuItem( self.helpMenu, wx.ID_ANY, u"User Guide", wx.EmptyString, wx.ITEM_NORMAL )
		self.helpMenu.AppendItem( self.userGuideMenuItem )
		
		self.m_menubar1.Append( self.helpMenu, u"Help" ) 
		
		self.SetMenuBar( self.m_menubar1 )
		
		
		self.Centre( wx.BOTH )
	
	def __del__( self ):
		pass
	
	def m_splitter1OnIdle( self, event ):
		self.m_splitter1.SetSashPosition( 700 )
		self.m_splitter1.Unbind( wx.EVT_IDLE )
	

