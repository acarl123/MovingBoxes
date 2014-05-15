# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version Nov  6 2013)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
from wx.lib.floatcanvas import NavCanvas, FloatCanvas, Resources

###########################################################################
## Class MainFrame
###########################################################################

class MainFrame ( wx.Frame ):

   def __init__( self, parent ):
      wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 571,419 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

      self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )

      self.statusBar = self.CreateStatusBar( 1, wx.ST_SIZEGRIP, wx.ID_ANY )
      self.m_menubar1 = wx.MenuBar( 0 )
      self.m_menu1 = wx.Menu()
      self.menuExit = wx.MenuItem( self.m_menu1, wx.ID_ANY, u"Exit", wx.EmptyString, wx.ITEM_NORMAL )
      self.m_menu1.AppendItem( self.menuExit )

      self.m_menubar1.Append( self.m_menu1, u"&File" )

      self.SetMenuBar( self.m_menubar1 )

      bSizer1 = wx.BoxSizer( wx.VERTICAL )

      NC = NavCanvas.NavCanvas(self,
                               Debug=0,
                               BackgroundColor=(173, 173, 173))

      self.Canvas = NC.Canvas  # reference the contained FloatCanvas

      # self.drawingPanel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
      bSizer1.Add( NC, 1, wx.EXPAND |wx.ALL, 5 )


      self.SetSizer( bSizer1 )
      self.Layout()

      self.Centre( wx.BOTH )

   def __del__( self ):
      pass


