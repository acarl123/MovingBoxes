from NavigatorView import NavigatorFrame
import wx
from collections import deque


class NavigatorController:
   def __init__(self):
      self.mainWindow = NavigatorFrame(None)
      self.mainWindow.Show()

      # Bindings
      self.mainWindow.Bind(wx.EVT_MENU, self.onExit, self.mainWindow.menuExit)
      self.mainWindow.Bind(wx.EVT_MOUSE_EVENTS, self.onMouse) # Add all mouse events to a single bind

      # Initialize member variables
      self.mousePositions = deque([])
      self.mouseRel = 0, 0

   """ Bindings """
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
