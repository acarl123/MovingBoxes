from NavigatorView import NavigatorFrame
import NavigatorModel
import wx
from collections import deque


class NavigatorController:
   def __init__(self):
      self.mainWindow = NavigatorFrame(None)
      self.mainWindow.Show()
      self.rectModel = NavigatorModel.RectInfo

      # Bindings
      self.mainWindow.Bind(wx.EVT_MENU, self.onExit, self.mainWindow.menuExit)
      self.mainWindow.Bind(wx.EVT_MOUSE_EVENTS, self.onMouse) # Add all mouse events to a single bind

      # Initialize member variables
      self.rects = {}
      self.selectedRects = []
      self.collidedRects = []
      self.mousePositions = deque([])
      self.mouseRel = 0, 0

   #--------------------------------------------------------------------------------------#
   # Bindings
   #--------------------------------------------------------------------------------------#
   def onExit(self, event):
      self.mainWindow.Destroy()
      exit()

   # Handles all mouse events
   def onMouse(self, event):
      # Calculate change in mouse position since last event using a queue system
      self.mousePositions.append((event.GetX(), event.GetY()))
      if len(self.mousePositions) == 2:
         self.mouseRel = ((self.mousePositions[1][0] - self.mousePositions[0][0]), (self.mousePositions[1][1] - self.mousePositions[0][1]))
         self.mousePositions.popleft()

      if event.GetEventType() == wx.wxEVT_LEFT_DOWN: self.onClick(event)
      if event.GetEventType() == wx.wxEVT_RIGHT_DOWN: self.onRClick(event)
      if event.GetEventType() == wx.wxEVT_LEFT_UP: self.onLUp(event)
      if event.Dragging() == True: self.onDrag(event)

   def onClick(self, event):
      # Set a black border rectangle on each shape
      for rectNum in self.rects:
         self.rects[rectNum][0].SetLineColor(wx.Colour(0, 0, 0))
      self.selectedRects = []

      print 'foo'

   def onRClick(self, event):
      print 'foo'

   def onLUp(self, event):
      print 'foo'

   def onDrag(self, event):
      print 'foo'
