from collections import deque
from NavigatorView import NavigatorFrame
from wx.lib.floatcanvas import NavCanvas, FloatCanvas, Resources
import NavigatorModel
import pygame
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

      # Bind events to FloatCanvas
      self.canvas.Bind(FloatCanvas.EVT_LEFT_DOWN, self.onClick)
      self.canvas.Bind(FloatCanvas.EVT_MOTION, self.onDrag)
      self.canvas.Bind(FloatCanvas.EVT_LEFT_UP, self.onLUp)

      # Initialize member variables
      self.rects = {}
      self.selectedRects = []
      self.collidingRects = []
      self.mousePositions = deque([])
      self.mouseRel = 0, 0
      self.ctrl_down = False

      # @TODO: Remove this in the future, but for now populate the screen for prototyping
      self.populateScreen()

   #--------------------------------------------------------------------------------------#
   # Initialization
   #--------------------------------------------------------------------------------------#
   def populateScreen(self):
      randnum = random
      randnum.seed()
      for i in xrange(10):
         xy = (randnum.randint(0, 800), randnum.randint(0, 600))
         # xy = 0, 0
         rect = self.canvas.AddRectangle(self.canvas.PixelToWorld(xy), (80, 35), LineWidth=0, FillColor=NavigatorModel.colors['BLUE'])
         rect.Name = str(len(self.rects))
         rect.Bind(FloatCanvas.EVT_FC_LEFT_DOWN, lambda object, event=wx.MouseEvent(): self.onRectLeftClick(object, event)) # You can bind to the hit event of rectangle objects
         rect.Text = self.canvas.AddScaledText('Number ' + `i`, self.canvas.PixelToWorld((xy[0]+40, xy[1]-17.5)), 7, Position = "cc")
         self.rects[rect.Name] = [rect, pygame.Rect(xy[0], xy[1]-35, 80, 35)]
         rect.PutInBackground()
         rect.Text.PutInBackground()
      self.canvas.Draw()

   def show(self):
      self.mainWindow.Show()

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
      if not hasattr(self, "popupID1"):
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
      for rectNum in self.rects:
         self.rects[rectNum][0].SetLineColor(wx.Colour(0, 0, 0))
      self.selectedRects = []

   def onDrag(self, event):
      self.canvas._BackgroundDirty = True
      self.mousePositions.append((event.GetX(), event.GetY()))
      if len(self.mousePositions) == 2:
         self.mouseRel = ((self.mousePositions[1][0] - self.mousePositions[0][0]),
                          -(self.mousePositions[1][1] - self.mousePositions[0][1]))
         self.mousePositions.popleft()
      # Move all the selected rects
      if event.Dragging():
         if self.selectedRects:
            for rectNum in self.selectedRects:
               if self.rects[rectNum][0] not in self.canvas._ForeDrawList:
                  self.rects[rectNum][0].PutInForeground() # Moving rects go in foreground
                  self.rects[rectNum][0].Text.PutInForeground()
               self.rects[rectNum][0].Move(self.mouseRel)
               self.rects[rectNum][0].Text.Move(self.mouseRel)
               # Also have to update the 'virtual' rect stored in the pygame object
               self.rects[rectNum][1][0] += self.mouseRel[0]
               self.rects[rectNum][1][1] += -self.mouseRel[1]
            self.canvas.Draw(False)
         else:
            pass

   def onLUp(self, event):
      # Set all selected rects back to background
      for rectObj in self.selectedRects:
         self.rects[rectObj][0].PutInBackground()
         self.rects[rectObj][0].Text.PutInBackground()
      self.canvas.Draw()

   #--------------------------------------------------------------------------------------#
   # ContextMenu Bindings
   #--------------------------------------------------------------------------------------#
   def onArrangeHorizontally(self, event):
      print 'Arrange Horizontally'

   def onArrangeVertically(self, event):
      if self.selectedRects:
         # Get the position of the first rectangle
         firstKey = self.selectedRects[0]
         xpos1 = self.rects[firstKey][1][0]
         ypos1 = self.rects[firstKey][1][1]
         # Loop through the rectangles and align left with this rectangle
         index = 0
         for rectNum in self.selectedRects:
            xpos2 = self.rects[rectNum][1][0]
            ypos2 = self.rects[rectNum][1][1]

            differencex = xpos1-xpos2
            differencey = ypos1-ypos2+index

            self.rects[rectNum][0].Move((differencex, -differencey))
            self.rects[rectNum][0].Text.Move((differencex, -differencey))
            self.rects[rectNum][1][0] += differencex
            self.rects[rectNum][1][1] += differencey
            index += self.rects[rectNum][1][3] + 10
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