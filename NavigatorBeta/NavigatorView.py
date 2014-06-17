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
from NavigatorBeta.NavigatorFloatCanvas import NavigatorFloatCanvas


class NavigatorFrame ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 725,558 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		bSizer1 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_splitter1 = wx.SplitterWindow( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.SP_3D )
		self.m_splitter1.Bind( wx.EVT_IDLE, self.m_splitter1OnIdle )
		self.m_splitter1.SetMinimumPaneSize( 5 )
		
		self.m_panel1 = wx.Panel( self.m_splitter1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer5 = wx.BoxSizer( wx.VERTICAL )
		
		self.NavCanvas = NavigatorFloatCanvas(self, Debug=0, BackgroundColor=(173, 173, 173))
		bSizer5.Add( self.NavCanvas, 0, wx.ALL, 5 )
		
		
		self.m_panel1.SetSizer( bSizer5 )
		self.m_panel1.Layout()
		bSizer5.Fit( self.m_panel1 )
		self.m_panel2 = wx.Panel( self.m_splitter1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer6 = wx.BoxSizer( wx.VERTICAL )
		
		self.lstLegend = wx.ListCtrl( self.m_panel2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_REPORT )
		bSizer6.Add( self.lstLegend, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		self.m_panel2.SetSizer( bSizer6 )
		self.m_panel2.Layout()
		bSizer6.Fit( self.m_panel2 )
		self.m_splitter1.SplitHorizontally( self.m_panel1, self.m_panel2, 500 )
		bSizer1.Add( self.m_splitter1, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( bSizer1 )
		self.Layout()
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
		
		self.Centre( wx.BOTH )
	
	def __del__( self ):
		pass
	
	def m_splitter1OnIdle( self, event ):
		self.m_splitter1.SetSashPosition( 500 )
		self.m_splitter1.Unbind( wx.EVT_IDLE )
	

