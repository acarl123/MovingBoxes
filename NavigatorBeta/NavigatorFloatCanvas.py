import wx
from wx.lib.floatcanvas import FloatCanvas, NavCanvas, Resources


class NavigatorFloatCanvas( NavCanvas.NavCanvas ):
   def __init__(self, parent, id=wx.ID_ANY, size=wx.DefaultSize, **kwargs):
      self.navCanvas = NavCanvas.NavCanvas
      self.navCanvas.__init__(self, parent, id, size, **kwargs)
      pass