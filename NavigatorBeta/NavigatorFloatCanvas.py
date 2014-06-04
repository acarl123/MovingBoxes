import wx
from wx.lib.floatcanvas import FloatCanvas, NavCanvas, Resources
import numpy


def YDownProjection(CenterPoint):
   return numpy.array((1, -1))


class NavigatorFloatCanvas( NavCanvas.NavCanvas ):
   def __init__(self, parent, id=wx.ID_ANY, size=wx.DefaultSize, **kwargs):
      self.navCanvas = NavCanvas.NavCanvas
      self.navCanvas.__init__(self, parent, id, size, **kwargs)


   # def BuildToolbar(self):
   # You can use this method to override the default
   # pass

