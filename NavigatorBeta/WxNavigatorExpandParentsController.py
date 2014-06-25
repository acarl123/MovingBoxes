__author__ = 'mwj'

import WxNavigatorExpandView
import wx
import ExportFileBusinessObject as efbo
import ExportFileRelationship as efrel
import MDXUtils
import sys

class ExpandParentsController:
   def __init__(self, parent, bo, busObjDict):
      self.bo = bo
      self.busObjDict = busObjDict

      # Setup view
      self.expandParentDlg = WxNavigatorExpandView.ExpandView(parent)
      self.parentList = self.expandParentDlg.listCtrlChildren
      self.parentList.InsertColumn(0, "Name")
      self.parentList.InsertColumn(1, "Type")

      # Bindings
      self.expandParentDlg.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected, self.parentList)
      self.expandParentDlg.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected, self.parentList)
      self.expandParentDlg.Bind(wx.EVT_BUTTON, self.OnAddParents, self.expandParentDlg.btnAddSelected)
      self.expandParentDlg.Bind(wx.EVT_CHECKBOX, self.OnSelectAll, self.expandParentDlg.checkBoxSelectAll)

      # Initial member variables
      self.parentData = {}
      self.returnBOs = []
      self.names = []

      # Populate the list and finish the view
      self.populateList()
      self.parentList.SetColumnWidth(0, wx.LIST_AUTOSIZE)
      self.parentList.SetColumnWidth(1, wx.LIST_AUTOSIZE)

   def show(self):
      self.expandParentDlg.Show()

   def OnItemSelected(self, event):
      print 'you selected' + str(event.GetEventObject())

   def OnItemDeselected(self, event):
      print 'you deselected' + str(event.GetEventObject())

   def OnAddParents(self, event):
      if not self.parentList.selectedRects:
         self.expandParentDlg.EndModal(wx.ID_CANCEL)
      for index in self.parentList.selectedRects:
         bo = self.parentData[index]
         self.returnBOs.append(bo)
      self.expandParentDlg.EndModal(wx.ID_OK)
      self.expandParentDlg.Destroy()

   def OnSelectAll(self, event):
      if event.IsChecked():
         for child in self.parentData:
            self.parentList.CheckItem(child)
      else:
         for child in self.parentData:
            if self.parentList.IsChecked(child):
               self.parentList.ToggleItem(child)

   def populateList(self):
      for revision in efbo.getAllRevisions(self.bo, self.busObjDict):
         relationships = efbo.getToRelationship(revision)
         for rel in relationships:
            if efrel.getTypeName(rel) == MDXUtils.REL_AD: continue # Skip Drawings
            fromBo = efrel.getFrom(rel)
            name, type = efbo.getName(fromBo), efbo.getTypeName(fromBo)
            if name in self.names: continue # Skip repeats
            self.names.append(name)
            index = self.parentList.InsertStringItem(sys.maxint, name)
            self.parentData[index] = fromBo
            self.parentList.SetStringItem(index, 1, type)

