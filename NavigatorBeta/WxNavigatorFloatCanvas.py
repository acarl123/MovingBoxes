import wx
from wx.lib.floatcanvas import FloatCanvas, NavCanvas, Resources, GUIMode
import numpy as N


def YDownProjection(CenterPoint):
   return N.array((1, -1))


class NavigatorFloatCanvas( NavCanvas.NavCanvas ):
   def __init__(self, parent, id=wx.ID_ANY, size=wx.DefaultSize, **kwargs):
      self.navCanvas = NavCanvas.NavCanvas
      self.navCanvas.__init__(self, parent, id, size, ProjectionFun=YDownProjection, **kwargs)
      self.ToolBar.Destroy()

      self.Modes = [("Pointer", GUIMode.GUIMouse(), Resources.getPointerBitmap()),
                    ("Pan", GUIMode.GUIMove(), Resources.getHandBitmap()),]
      self.BuildToolbar()
      # # Create the vertical sizer for the toolbar and Panel
      box = wx.BoxSizer(wx.VERTICAL)
      box.Add(self.ToolBar, 0, wx.ALL | wx.ALIGN_LEFT | wx.GROW, 4)

      self.Canvas = FloatCanvas.FloatCanvas(self, **kwargs)
      box.Add(self.Canvas, 1, wx.GROW)

      self.SetSizerAndFit(box)

      # default to first mode
      #self.ToolBar.ToggleTool(self.PointerTool.GetId(), True)
      self.Canvas.SetMode(self.Modes[0][1])
      self.scale = 1.
      self.panning = False


   def ZoomToFit(self, event):
      super(NavigatorFloatCanvas, self).ZoomToFit(event)
      self.scale = 1. / self.Canvas.Scale

   def SetMode(self, event):
      super(NavigatorFloatCanvas, self).SetMode(event)
      if event.GetId() == 120:
         self.panning = True
      else:
         self.panning = False


class NavGuiMove( GUIMode.GUIMove ):
   def __init__(self, event, canvas=None):
      super(NavGuiMove, self).__init__(canvas)
      self.Canvas = canvas
      self.event = event


   def OnMove(self, event):
      self.Canvas._RaiseMouseEvent(event, FloatCanvas.EVT_FC_MOTION)
      if event.Dragging() and event.MiddleIsDown() and not self.StartMove is None:
         self.EndMove = N.array(event.GetPosition())
         self.MoveImage(event)
         DiffMove = self.MidMove - self.EndMove
         self.Canvas.MoveImage(DiffMove, 'Pixel', ReDraw=False)  # reset the canvas without re-drawing
         self.MidMove = self.EndMove
         self.MoveTimer.Start(30, oneShot=True)

   def OnMiddleUp(self, event):
      print 'p'

   def __del__(self):
      self.OnLeftUp(self.event)
      self.MoveTimer.Stop()
