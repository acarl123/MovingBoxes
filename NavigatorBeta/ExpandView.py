# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Nov  6 2013)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
from wx.lib.mixins.listctrl import CheckListCtrlMixin

###########################################################################
## Class ExpandView
###########################################################################

class ExpandView ( wx.Dialog ):

   def __init__( self, parent ):
      wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 408,485 ), style = wx.DEFAULT_DIALOG_STYLE|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX )

      self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )

      bSizer2 = wx.BoxSizer( wx.VERTICAL )

      self.checkBoxSelectAll = wx.CheckBox( self, wx.ID_ANY, u"Select/ Deselect All", wx.DefaultPosition, wx.DefaultSize, 0 )
      bSizer2.Add( self.checkBoxSelectAll, 0, wx.ALL, 5 )

      self.listCtrlChildren = CheckListCtrl(self)

      bSizer2.Add( self.listCtrlChildren, 1, wx.ALL|wx.EXPAND, 5 )

      self.btnAddSelected = wx.Button( self, wx.ID_ANY, u"Add Selected Items", wx.DefaultPosition, wx.DefaultSize, 0 )
      bSizer2.Add( self.btnAddSelected, 0, wx.ALL, 5 )


      self.SetSizer( bSizer2 )
      self.Layout()

      self.Centre( wx.BOTH )

   def __del__( self ):
      pass


class CheckListCtrl(wx.ListCtrl, CheckListCtrlMixin):
   def __init__(self, parent):
      wx.ListCtrl.__init__(self, parent, -1, style= wx.LC_REPORT)
      CheckListCtrlMixin.__init__(self)
      self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
      self.selectedRects = []

   def OnItemActivated(self, event):
      self.ToggleItem(event.m_itemIndex)

   def OnCheckItem(self, index, flag):
      if flag:
         self.selectedRects.append(index)
      else:
         self.selectedRects.remove(index)