__author__ = 'mwj'
import ExpandView
import wx
import ExportFileBusinessObject as efbo
import ExportFileRelationship as efrel
import MDXUtils
import sys

class ExpandChildrenController:
   def __init__(self, parent, bo, busObjDict):
      self.bo = bo
      self.busObjDict = busObjDict

      # Setup view
      self.expandDlg = ExpandView.ExpandView(parent)
      self.childrenList = self.expandDlg.listCtrlChildren
      self.childrenList.InsertColumn(0, "Name")
      self.childrenList.InsertColumn(1, "Type")

      # Bindings
      self.expandDlg.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected, self.childrenList)
      self.expandDlg.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected, self.childrenList)
      self.expandDlg.Bind(wx.EVT_BUTTON, self.OnAddChildren, self.expandDlg.btnAddSelected)
      self.expandDlg.Bind(wx.EVT_CHECKBOX, self.OnSelectAll, self.expandDlg.checkBoxSelectAll)
      # self.expandDlg.Bind(wx.EVT_)

      # Initial member variables
      self.childrenData = {}
      self.returnBOs = []

      # Populate the list and finish the view
      self.populateList()
      self.childrenList.SetColumnWidth(0, wx.LIST_AUTOSIZE)
      self.childrenList.SetColumnWidth(1, wx.LIST_AUTOSIZE)

   def show(self):
      self.expandDlg.Show()

   def OnItemSelected(self, event):
      print 'you selected' + str(event.GetEventObject())

   def OnItemDeselected(self, event):
      print 'you deselected' + str(event.GetEventObject())

   def OnAddChildren(self, event):
      if not self.childrenList.selectedRects:
         self.expandDlg.EndModal(wx.ID_CANCEL)
      for index in self.childrenList.selectedRects:
         bo = self.childrenData[index]
         self.returnBOs.append(bo)
      self.expandDlg.EndModal(wx.ID_OK)
      self.expandDlg.Destroy()

   def OnSelectAll(self, event):
      if event.IsChecked():
         for child in self.childrenData:
            self.childrenList.CheckItem(child)
      else:
         for child in self.childrenData:
            if self.childrenList.IsChecked(child):
               self.childrenList.ToggleItem(child)

   def populateList(self):
      for revision in efbo.getAllRevisions(self.bo, self.busObjDict):
         relationships = efbo.getFromRelationship(revision)
         for rel in relationships:
            if efrel.getTypeName(rel) == MDXUtils.REL_AD: continue # Skip Drawings
            toBo = efrel.getTo(rel)
            if toBo in self.childrenData.values(): continue # Skip repeats
            name, type = efbo.getName(toBo), efbo.getTypeName(toBo)
            index = self.childrenList.InsertStringItem(sys.maxint, name)
            self.childrenData[index] = toBo
            self.childrenList.SetStringItem(index, 1, type)

