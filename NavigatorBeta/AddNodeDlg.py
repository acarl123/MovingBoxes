#!/usr/bin/python

import wx
from sets import Set
import os
import ExportFileUtils
import ExportFileBusinessObject as efbo
import fnmatch

def SizeColumns(listctrl):
	ncolumns = listctrl.GetColumnCount()
	width = listctrl.GetClientSize()[0] / ncolumns
	for c in xrange(0,ncolumns):
		listctrl.SetColumnWidth(c,width)

class AddNodeDlg(wx.Dialog):
   def __init__(self, parent, efd):
      wx.Dialog.__init__(self,parent, title="Find Node", size=(800, 800), style=wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX | wx.RESIZE_BORDER | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)
      self.efd = efd
      vbox = wx.BoxSizer(wx.VERTICAL)
      self.ctrlPressed = False # variable to hold whether or not control key is pressed

      hbox1 = wx.BoxSizer(wx.HORIZONTAL)
      st1 = wx.StaticText (self, label='Name: ')
      hbox1.Add(st1, border=8)
		
      self.NodeNameCtrl = wx.TextCtrl(self,style=wx.TE_PROCESS_ENTER)
      hbox1.Add(self.NodeNameCtrl,flag=wx.EXPAND, proportion=1)
      self.Bind(wx.EVT_TEXT_ENTER, self.DoSearch, self.NodeNameCtrl)
		
      self.SearchButton = wx.Button (self,label='Search')
      self.SearchButton.Bind(wx.EVT_BUTTON, self.DoSearch)
      hbox1.Add(self.SearchButton, border=8)
		
		
      vbox.Add(hbox1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
      vbox.Add((-1,10))
      okbutton = wx.Button (self,label='Insert',id=wx.ID_OK)
      okbutton.Bind(wx.EVT_BUTTON,self.OnOK)
      self.Results = wx.ListCtrl(self,style=wx.LC_REPORT)			
		
      self.Results.InsertColumn (0,'Type')
      self.Results.InsertColumn (1,'Name')
      self.Results.InsertColumn (2,'Revision')
      self.Results.InsertColumn (3,'Dataset')
		
      self.Results.SetColumnWidth(0, 220)
      self.Results.SetColumnWidth(1, 220)
      self.Results.SetColumnWidth(2, 100)
      self.Results.SetColumnWidth(3, 220)
		
      self.Bind (wx.EVT_LIST_COL_CLICK, self.OnColumnClick, self.Results)
      self.Bind (wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemDoubleClick, self.Results)      
		
      vbox.Add (self.Results,proportion=1,flag=wx.EXPAND|wx.ALL,border=10)
		
      hbox3 = wx.BoxSizer (wx.HORIZONTAL)
		
      hbox3.Add(okbutton)
      vbox.Add(hbox3,proportion=0,flag=wx.ALIGN_RIGHT | wx.RIGHT | wx.BOTTOM,border=10)
		
      self.SetSizer(vbox)
		
   def OnOK (self, event):
      self.ReturnBOs = None
      if (self.Results.GetSelectedItemCount () == 0):
         self.EndModal(wx.ID_CANCEL)
         return
		
      self.ReturnBOs = []

      selitm = self.Results.GetFirstSelected ()
		
      while selitm != -1:
         self.ReturnBOs.append(self.Results.GetItemData(selitm))
         selitm = self.Results.GetNextSelected (selitm)
		
      self.EndModal(wx.ID_OK)
	
   def DoSearch (self,event):
      print "Searching: " + self.NodeNameCtrl.GetValue ()
		
      name = self.NodeNameCtrl.GetValue ()
      self.SearchBOs = Set ([])
      for bo in self.efd.getAllBusinessObjects ():
         if (fnmatch.fnmatch(efbo.getName (bo),name)):
            self.SearchBOs.add (efbo.getLastRevision (bo,self.efd.getAllBusinessObjects()))
		
      self.Results.DeleteAllItems ()
		
      index = 0
      for bo in self.SearchBOs:
         tnrd = efbo.getTnrd (bo)
         pos = self.Results.InsertStringItem (0,tnrd[0])
         self.Results.SetStringItem      (pos,1,tnrd[1])
         self.Results.SetStringItem      (pos,2,tnrd[2])
         self.Results.SetStringItem      (pos,3,tnrd[3])
         self.Results.SetItemData        (pos,bo)
         index += 1
			
   def OnColumnClick (self, event):
      coldict = dict ()
      for i in xrange (0,self.Results.GetItemCount ()):
         coldict[self.Results.GetItemData(i)] = self.Results.GetItem(i,e.m_col).GetText ()
			
      self.Results.SortItems (lambda a,b: coldict[a] < coldict[b])

   def OnItemDoubleClick (self, event):
      self.OnOK(event)