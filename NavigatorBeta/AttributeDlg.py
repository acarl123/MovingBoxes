import wx
import ExportFileUtils
import ExportFileBusinessObject as efbo

def AttrNameCmp (a, b):
	a = a.lower ()
	b = b.lower ()
	if (a[0] == '$'):
		if (b[0] == '$'):
			return -1 if a > b else 1
		return 1
	if (b[0] == '$'):
		return -1

	if (a[0] == '%'):
		if (b[0] == '%'):
			return -1 if a > b else 1
		return 1
	if (b[0] == '%'):
		return -1

	return -1 if a > b else 1

class AttributeDlg(wx.Dialog):
	def __init__(self, parent, bo):
		super(AttributeDlg, self).__init__(parent, title="Attributes", size=(800, 800), style=wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX | wx.RESIZE_BORDER | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)

		vbox = wx.BoxSizer(wx.VERTICAL)

		hbox = wx.BoxSizer(wx.HORIZONTAL)

		self.attrlist = wx.ListCtrl(self,style=wx.LC_REPORT)
		self.attrlist.InsertColumn (0,'Name')
		self.attrlist.InsertColumn (1,'Value')

		self.prevbutton = wx.Button (self, label="Prev Rev.")
		self.nextbutton = wx.Button (self, label="Next Rev.")
		self.nextbutton.Bind(wx.EVT_BUTTON,self.OnNext)
		self.prevbutton.Bind(wx.EVT_BUTTON,self.OnPrev)

		hbox.Add(self.prevbutton)
		hbox.Add(self.nextbutton)

		vbox.Add (self.attrlist, proportion=1,flag=wx.EXPAND|wx.ALL,border = 10)
		vbox.Add (hbox,proportion=0,flag=wx.ALIGN_RIGHT | wx.RIGHT | wx.BOTTOM, border=10)

		self.SetSizer(vbox)

		self.SetBo(bo)

		#-------Attach event to CTRL + C key combination-------
		randomId = wx.NewId()
		self.Bind(wx.EVT_MENU, self.onKeyCombo, id=randomId)
		accel_tbl = wx.AcceleratorTable([(wx.ACCEL_CTRL, ord('C'), randomId)])
		self.SetAcceleratorTable(accel_tbl)

	def SetBo (self, bo):
		self.bo = bo
		self.attrlist.DeleteAllItems ()
		attrs = efbo.getAttributes(self.bo)
		attrs['$state'] = efbo.getState(self.bo)
		attrkeys = attrs.keys ()
		attrkeys = sorted(attrkeys, cmp = AttrNameCmp)

		for a in attrkeys:
			pos = self.attrlist.InsertStringItem (0,a)
			self.attrlist.SetStringItem  (pos,1,attrs[a])
		pos = self.attrlist.InsertStringItem(0,'BoPtr')
		self.attrlist.SetStringItem(pos,1,str(bo))

		tnrd = efbo.getTnrd (bo)
		self.SetTitle ("\"" + tnrd[0] + "\", " + tnrd[1] + "\", " + tnrd[2] + "\", " + tnrd[3])

		if (efbo.getNextRevision(self.bo,None) == None):
			self.nextbutton.Disable()
		else:
			self.nextbutton.Enable ()

		if (efbo.getPreviousRevision(self.bo,None) == None):
			self.prevbutton.Disable()
		else:
			self.prevbutton.Enable ()

	def OnNext (self, e):
		self.SetBo (efbo.getNextRevision(self.bo,None))

	def OnPrev (self, e):
		self.SetBo (efbo.getPreviousRevision(self.bo,None))

	#===========================================================
	# Event handler for copying selected rows from list control
	#===========================================================
	def onKeyCombo (self, e):
		#-------Return if nothing selected-------
		if not self.attrlist:
			return
		selectedCount = self.attrlist.GetSelectedItemCount()
		if selectedCount == 0:
			return
		#-------Get list of selected indexes-------
		selection = []
		curIndex = -1
		while True:
			nextIndex = self.attrlist.GetNextItem(curIndex, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
			if nextIndex == -1:
				break
			selection.append(nextIndex)
			curIndex = nextIndex

		#-------Get values of selected rows-------
		columnCount = self.attrlist.GetColumnCount()
		values = ""
		for rowIndex in selection:
			value = ""
			for column in range(0,columnCount):
				item = self.attrlist.GetItem(rowIndex,column)
				value += "%s	" %item.GetText()
			values += value[:-1]
			values += "\n"

		#-------Copy to clipboard-------
		if wx.TheClipboard.Open():
			self.dataObj = wx.TextDataObject()
			self.dataObj.SetText(values[:-1])
			wx.TheClipboard.SetData(self.dataObj)
			wx.TheClipboard.Close()
		else:
			wx.MessageBox("Unable to open the clipboard","Error")
		pass
	#===========================================================