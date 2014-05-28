__author__ = 'mwj'
import wx
import wx.lib.dragscroller

class DragCanvas(wx.ScrolledWindow):
   def __init__(self, parent, ID):
      wx.ScrolledWindow.__init__(self, parent, ID)
      self.Bind(wx.EVT_PAINT, self.OnPaint)

      self.dragImage = None
      self.dragShape = None
      self.hiliteShape = None

      self.scroller = wx.lib.dragscroller.DragScroller(self)



   def OnPaint(self, event):
      event.Skip()

   def GetViewStart(self):
      return self.GetPositionTuple()



