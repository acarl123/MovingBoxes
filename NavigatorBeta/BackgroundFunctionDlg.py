import wx
import sys
import threading
import contextlib

EVT_OUTPUT_ID = wx.NewId()

class OutputEvent(wx.PyEvent):
	def __init__(self,data):
		wx.PyEvent.__init__(self)
		self.SetEventType(EVT_OUTPUT_ID)
		self.data = data
		
def EVT_OUTPUT(win,func):
	win.Connect(-1,-1,EVT_OUTPUT_ID,func)
	
class OutputStreamNotifier:
	def __init__(self,target,dbgout):
		self.target = target
		self.dbgout = dbgout
		
	def write (self,str):
		wx.PostEvent(self.target,OutputEvent(str))
		
	def __getattr__(self, name):
		return self.dbgout.__getattr__(name)

@contextlib.contextmanager
def stdoutMsgPump(target):
	oldout = sys.stdout
	olderr = sys.stderr
	sys.stdout = OutputStreamNotifier(target,oldout)
	sys.stderr = OutputStreamNotifier(target,olderr)
	yield None
	sys.stdout = oldout
	sys.stderr = olderr
	


class BackgroundFunctionDlg(wx.Dialog):
	def __init__(self, parent, name, function, *workargs):
		super(BackgroundFunctionDlg, self).__init__(parent, title=name, size=(300, 300), style=wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX | wx.RESIZE_BORDER | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)
		EVT_OUTPUT(self,self.OnOutput)
		self.Bind(wx.EVT_CLOSE,self.OnClose)
		self.work = function
		self.workerthread = threading.Thread (target=self.DoWork, args=workargs)
		self.done = False
		vbox = wx.BoxSizer(wx.VERTICAL)
		
		self.Output = wx.TextCtrl(parent = self, id = -1, style = wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_AUTO_URL)
		vbox.Add (self.Output,proportion=1,flag=wx.EXPAND|wx.ALL,border=10)
		
		self.SetSizer(vbox)
		
	def DoWork (self,*args):
		with stdoutMsgPump(self) as s:
			self.work(*args)
		self.done = True
		#self.EndModal(wx.ID_OK)
		
	def Go (self):
		self.workerthread.start ()
		self.ShowModal ()
		
	def OnOutput(self, e):
		self.Output.AppendText(e.data)
		
	def OnClose (self, e):
		if (e.CanVeto() and not self.done):
			e.Veto()
		else:
			e.Skip()