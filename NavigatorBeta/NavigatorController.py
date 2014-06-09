from collections import deque
from NavigatorView import NavigatorFrame
from wx.lib.floatcanvas import NavCanvas, FloatCanvas, Resources

from CustomRect import NavRect
import NavigatorModel
import os
import random
import wx
FloatCanvas.FloatCanvas.HitTest = NavigatorModel.BB_HitTest

class NavigatorController:
   def __init__(self):
      # Setup view
      self.mainWindow = NavigatorFrame(None)

      # Initialize FloatCanvas defaults
      self.canvas = self.mainWindow.NavCanvas.Canvas
      self.canvas.InitializePanel()
      self.canvas.InitAll()
      self.canvas.Draw()

      # Setup model
      self.rectModel = NavigatorModel.RectInfo

      # Bind normal events
      self.mainWindow.Bind(wx.EVT_MENU, self.onExit, self.mainWindow.menuExit)
      self.mainWindow.Bind(wx.EVT_MOUSEWHEEL, self.onScroll)
      self.canvas.Bind(wx.EVT_CONTEXT_MENU, self.onContextMenu)
      self.canvas.Bind(wx.EVT_KEY_DOWN, self.onKeyEvents)
      self.canvas.Bind(wx.EVT_KEY_UP, self.onKeyEvents)

      # Initialize member variables
      self.rects = {}
      self.selectedRects = []
      self.collidingRects = []
      self.mousePositions = deque([])
      self.mouseRel = 0, 0
      self.ctrl_down = False
      self.Drawing = False
      self.RBRect = None
      self.StartPointWorld = None
      self.Tol = 5
      self.enable()

      # @TODO: Remove this in the future, but for now populate the screen for prototyping
      self.populateScreen()

   #--------------------------------------------------------------------------------------#
   # Initialization (not bindings)
   #--------------------------------------------------------------------------------------#
   def populateScreen(self):
      randnum = random
      randnum.seed()
      for i in xrange(50):
         xy = (randnum.randint(0, 800), randnum.randint(0, 600))
         rect = self.canvas.AddRectangle(self.canvas.PixelToWorld(xy), (80, 35), LineWidth=0, FillColor=NavigatorModel.colors['BLUE'])
         rect.Name = str(len(self.rects))
         rect.Bind(FloatCanvas.EVT_FC_LEFT_DOWN, lambda object, event=wx.MouseEvent(): self.onRectLeftClick(object, event)) # You can bind to the hit event of rectangle objects
         rect.Bind(FloatCanvas.EVT_FC_LEFT_DCLICK, lambda object, event=wx.MouseEvent(): self.onRectLeftDClick(object, event))
         rect.Text = self.canvas.AddScaledText('Number ' + `i`, self.canvas.PixelToWorld((xy[0]+40, xy[1]-17.5)), 7, Position = "cc")
         self.rects[rect.Name] = [rect]
         rect.PutInBackground()
         # rect.Text.PutInBackground()
      self.canvas.Draw()

   def show(self):
      self.mainWindow.Show()

   def enable(self):
      # Bind events to FloatCanvas
      self.canvas.Bind(FloatCanvas.EVT_LEFT_DOWN, self.onClick)
      self.canvas.Bind(FloatCanvas.EVT_MOTION, self.onDrag)
      self.canvas.Bind(FloatCanvas.EVT_LEFT_UP, self.onLUp)

   def disable(self):
      # Bind events to FloatCanvas
      self.canvas.Unbind(FloatCanvas.EVT_LEFT_DOWN, self.onClick)
      self.canvas.Unbind(FloatCanvas.EVT_MOTION, self.onDrag)
      self.canvas.Unbind(FloatCanvas.EVT_LEFT_UP, self.onLUp)

   #--------------------------------------------------------------------------------------#
   # Normal Bindings
   #--------------------------------------------------------------------------------------#
   def onExit(self, event):
      self.mainWindow.Destroy()
      exit()

   def onScroll(self, event):
      scrollFactor = event.GetWheelRotation()
      if scrollFactor < 0:
         scrollFactor = 0.5
      elif scrollFactor > 0:
         scrollFactor = 2
      self.canvas.Zoom(scrollFactor, event.GetPositionTuple(), 'pixel')

   def onContextMenu(self, event):
      if len(self.selectedRects) == 0:
         #@TODO: add context menu for no rects selected
         return
      elif len(self.selectedRects) == 1:
         if not hasattr(self, 'popupID1'):
            self.popupID1 = wx.NewId()
            self.popupID2 = wx.NewId()
            self.popupID3 = wx.NewId()
            self.popupID4 = wx.NewId()
            self.canvas.Bind(wx.EVT_MENU, self.onExpand, id=self.popupID1)
            self.canvas.Bind(wx.EVT_MENU, self.onAttributes, id=self.popupID2)
            self.canvas.Bind(wx.EVT_MENU, self.onDelete, id=self.popupID3)
            self.canvas.Bind(wx.EVT_MENU, self.onLock, id=self.popupID4)
         menu = wx.Menu()
         menu.Append(self.popupID1, 'Expand')
         menu.Append(self.popupID2, 'Attributes/Properties')
         menu.Append(self.popupID3, 'Delete Selected')
         menu.Append(self.popupID4, 'Lock')
         self.canvas.PopupMenu(menu)
         menu.Destroy()
         return
      elif len(self.selectedRects) > 1:
         if not hasattr(self, 'popupID1'):
            self.popupID1 = wx.NewId()
            self.popupID2 = wx.NewId()
            self.popupID3 = wx.NewId()
            self.popupID4 = wx.NewId()
            self.canvas.Bind(wx.EVT_MENU, self.onArrangeHorizontally, id=self.popupID1)
            self.canvas.Bind(wx.EVT_MENU, self.onArrangeVertically, id=self.popupID2)
            self.canvas.Bind(wx.EVT_MENU, self.onDelete, id=self.popupID3)
            self.canvas.Bind(wx.EVT_MENU, self.onLock, id=self.popupID4)
         menu = wx.Menu()
         menu.Append(self.popupID1, 'Arrange Horizontally')
         menu.Append(self.popupID2, 'Arrange Vertically')
         menu.Append(self.popupID3, 'Delete Selected')
         menu.Append(self.popupID4, 'Lock')
         self.canvas.PopupMenu(menu)
         menu.Destroy()

   def onKeyEvents(self, event):
      self.ctrl_down = event.ControlDown()
      if event.GetKeyCode() == wx.WXK_DELETE:
         self.onDelete(event)

   #--------------------------------------------------------------------------------------#
   # FloatCanvas Bindings
   #--------------------------------------------------------------------------------------#
   def onClick(self, event):
      # Start drawing band box
      self.Drawing = True
      self.StartPoint = event.GetPosition()
      self.StartPointWorld = event.Coords

      if not self.ctrl_down:
         for rectNum in self.rects:
            self.rects[rectNum][0].SetLineColor(wx.Colour(0, 0, 0))
         self.selectedRects = []

   # @TODO: fix the logic of where the band box stuff should go and clean up the code a bit
   def onDrag(self, event):
      # Draw the band box
      if self.Drawing:
         x, y = self.StartPoint
         cornerx, cornery = event.GetPosition()
         w, h = (cornerx - x, cornery - y)
         if abs(w) > self.Tol and abs(h) > self.Tol:
            # draw the RB box
            dc = wx.ClientDC(self.canvas)
            dc.SetPen(wx.Pen('WHITE', 2, wx.SHORT_DASH))
            dc.SetBrush(wx.TRANSPARENT_BRUSH)
            dc.SetLogicalFunction(wx.XOR)
            if self.RBRect:
               dc.DrawRectangle(*self.RBRect)
            self.RBRect = (x, y, w, h)
            dc.DrawRectangle(*self.RBRect)
      event.Skip()

      self.canvas._BackgroundDirty = True
      self.mousePositions.append(event.GetPositionTuple())
      if len(self.mousePositions) == 2:
         self.mouseRel = ((self.mousePositions[1][0] - self.mousePositions[0][0]),
                          -(self.mousePositions[1][1] - self.mousePositions[0][1]))
         self.mousePositions.popleft()

      # Move all the selected rects
      if event.Dragging() and not self.ctrl_down:
         if self.selectedRects:
            for rectNum in self.selectedRects:
               if self.rects[rectNum][0] not in self.canvas._ForeDrawList:
                  self.rects[rectNum][0].PutInForeground() # Moving rects go in foreground
                  self.rects[rectNum][0].Text.PutInForeground()
               self.rects[rectNum][0].Move(self.mouseRel)
               self.rects[rectNum][0].Text.Move(self.mouseRel)
            self.canvas.Draw(False)
         else:
            pass

   def onLUp(self, event):
      # Stop drawing
      if self.Drawing:
         self.Drawing = False
         if self.RBRect:
            WH = event.Coords - self.StartPointWorld
            wx.CallAfter(self.onBandBoxDrawn, (self.StartPointWorld, WH))
         self.RBRect = None
         self.StartPointWorld = None

      # Set all selected rects back to background
      for rectObj in self.selectedRects:
         self.rects[rectObj][0].PutInBackground()
         self.rects[rectObj][0].Text.PutInBackground()
      self.canvas.Draw()

   #--------------------------------------------------------------------------------------#
   # ContextMenu with Single Object Selected Bindings
   #--------------------------------------------------------------------------------------#
   def onExpand(self, event):
      print 'Expand'

   def onAttributes(self, event):
      print 'Show Attributes'

   #--------------------------------------------------------------------------------------#
   # ContextMenu with Multiple Objects Selected Bindings
   #--------------------------------------------------------------------------------------#
   def onArrangeHorizontally(self, event):
      if self.selectedRects:
         firstRect = self.selectedRects[0]
         xpos1 = self.rects[firstRect][0].BoundingBox.Left
         ypos1 = self.rects[firstRect][0].BoundingBox.Top
         index = 0
         for rectNum in self.selectedRects:
            xpos2 = self.rects[rectNum][0].BoundingBox.Left
            ypos2 = self.rects[rectNum][0].BoundingBox.Top
            differencex = xpos1-xpos2+index
            differencey = ypos1-ypos2
            self.rects[rectNum][0].Move((differencex, differencey))
            self.rects[rectNum][0].Text.Move((differencex, differencey))
            index += self.rects[rectNum][0].BoundingBox.Width + 5
         self.canvas.Draw()

   def onArrangeVertically(self, event):
      if self.selectedRects:
         firstRect = self.selectedRects[0]
         xpos1 = self.rects[firstRect][0].BoundingBox.Left
         ypos1 = self.rects[firstRect][0].BoundingBox.Top
         index = 0
         for rectNum in self.selectedRects:
            xpos2 = self.rects[rectNum][0].BoundingBox.Left
            ypos2 = self.rects[rectNum][0].BoundingBox.Top
            differencex = xpos1-xpos2
            differencey = ypos1-ypos2+index
            self.rects[rectNum][0].Move((differencex, differencey))
            self.rects[rectNum][0].Text.Move((differencex, differencey))
            index -= self.rects[rectNum][0].BoundingBox.Height + 10
         self.canvas.Draw()

   def onDelete(self, event):
      for rectNum in self.selectedRects:
         self.rects[rectNum][0].UnBindAll()
         self.canvas.RemoveObjects((self.rects[rectNum][0], self.rects[rectNum][0].Text))
         del self.rects[rectNum]
      self.selectedRects=[]
      self.canvas.Draw()

   def onLock(self, event):
      print 'On Lock'

   #--------------------------------------------------------------------------------------#
   # FloatCanvas Rect Bindings
   #--------------------------------------------------------------------------------------#
   def onRectLeftClick(self, object, event):
      if self.ctrl_down:
         if object.Name not in self.selectedRects:
            self.selectedRects.append(object.Name)
      else:
         if object.Name not in self.selectedRects:
            for rectNum in self.selectedRects:
               self.rects[rectNum][0].SetLineColor(NavigatorModel.colors['BLACK'])

            self.selectedRects = []
            self.selectedRects.append(object.Name)
      object.PutInForeground() # clicked rect pops to top
      object.Text.PutInForeground()
      object.SetLineColor(NavigatorModel.colors['WHITE'])
      self.canvas.Draw()

   def onRectLeftDClick(self, object, event):
      randnum = random
      randnum.seed()
      # Get the right middle position of the rectangle
      # xy = object.BoundingBox.Right, object.BoundingBox.Center[1] - object.BoundingBox.Height/4
      # for revision in range(randnum.randint(1, 5)):
      #    index = revision+1
      #
      #    self.rects[object.Name] = self.canvas.AddRectangle(xy, (40, 17.5), LineWidth=0, FillColor=NavigatorModel.colors['BLUE'])
      #    xy = xy[0] + 40, xy[1]
      # self.canvas.Draw()



         #
         # xy = (randnum.randint(0, 800), randnum.randint(0, 600))
         # rect = self.canvas.AddRectangle(self.canvas.PixelToWorld(xy), (80, 35), LineWidth=0, FillColor=NavigatorModel.colors['BLUE'])
         # rect.Name = str(len(self.rects))
         # rect.Bind(FloatCanvas.EVT_FC_LEFT_DOWN, lambda object, event=wx.MouseEvent(): self.onRectLeftClick(object, event)) # You can bind to the hit event of rectangle objects
         # rect.Bind(FloatCanvas.EVT_FC_LEFT_DCLICK, lambda object, event=wx.MouseEvent(): self.onRectLeftDClick(object, event))
         # rect.Text = self.canvas.AddScaledText('Number ' + `i`, self.canvas.PixelToWorld((xy[0]+40, xy[1]-17.5)), 7, Position = "cc")
         # self.rects[rect.Name] = [rect]
         # rect.PutInBackground()
         # rect.Text.PutInBackground()

   def onBandBoxDrawn(self, rect):
      # Get the four corner coordinates of the RBRect
      x1, y1 = rect[0][0], rect[0][1]
      x2, y2 = rect[1][0]+x1, rect[1][1]+y1
      # Make sure x1<x2 and y1<y2
      if x2 <= x1:
         x1, x2 = x2, x1
      if y2 <= y1:
         y1, y2 = y2, y1
      for rectNum in self.rects:
         if x1 <= self.rects[rectNum][0].BoundingBox.Center[0] <= x2 and \
            y1 <= self.rects[rectNum][0].BoundingBox.Center[1] <= y2:
            self.selectedRects.append(self.rects[rectNum][0].Name)
            self.rects[rectNum][0].PutInForeground() # clicked rect pops to top
            self.rects[rectNum][0].Text.PutInForeground()
            self.rects[rectNum][0].SetLineColor(NavigatorModel.colors['WHITE'])
      self.canvas.Draw()


