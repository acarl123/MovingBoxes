from NavigatorView import NavigatorFrame
import NavigatorModel
import wx
from collections import deque
from wx.lib.floatcanvas import NavCanvas, FloatCanvas, Resources
FloatCanvas.FloatCanvas.HitTest = NavigatorModel.BB_HitTest
import pygame
import random

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
      self.canvas.Bind(wx.EVT_KEY_DOWN, self.onUpdateCtrl)
      self.canvas.Bind(wx.EVT_KEY_UP, self.onUpdateCtrl)
      self.canvas.Bind(wx.EVT_CONTEXT_MENU, self.onContextMenu)

      # Bind events to FloatCanvas
      self.canvas.Bind(FloatCanvas.EVT_LEFT_DOWN, self.onClick)
      self.canvas.Bind(FloatCanvas.EVT_LEFT_UP, self.onLUp)
      # self.canvas.Bind(FloatCanvas.EVT_RIGHT_DOWN, self.onRClick)
      self.canvas.Bind(FloatCanvas.EVT_MOTION, self.onDrag)

      # Initialize member variables
      self.rects = {}
      self.selectedRects = []
      self.mousePositions = deque([])
      self.mouseRel = 0, 0

      self.collidingRects = []
      self.timer = wx.PyTimer(self.moveRects)
      self.frameDelay = 30
      self.ctrl_down = False

      self.show()

      # @TODO: Remove this in the future, but for now populate the screen for prototyping
      self.populateScreen()

   #--------------------------------------------------------------------------------------#
   # Bindings
   #--------------------------------------------------------------------------------------#
   def onExit(self, event):
      self.mainWindow.Destroy()
      exit()

   def onClick(self, event):
      # Set a black border rectangle on each shape
      print 'On Left Click'
      for rectNum in self.rects:
         self.rects[rectNum][0].SetLineColor(wx.Colour(0, 0, 0))
      self.selectedRects = []

   def onRClick(self, event):
      print 'On Right Click'

   def onLUp(self, event):
      print 'On Left Up'
      for rectObj in self.selectedRects: # Only the moving rects should be in the foreground
         self.rects[rectObj][0].PutInBackground()
         self.rects[rectObj][0].Text.PutInBackground()

      self.findCollidingRects()
      if self.collidingRects:
         self.timer.Start(self.frameDelay)
      self.canvas.Draw()

   def onDrag(self, event):
      self.canvas._BackgroundDirty = True
      self.mousePositions.append((event.GetX(), event.GetY()))
      if len(self.mousePositions) == 2:
         self.mouseRel = ((self.mousePositions[1][0] - self.mousePositions[0][0]),
                          -(self.mousePositions[1][1] - self.mousePositions[0][1]))
         self.mousePositions.popleft()

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

   def onScroll(self, event):
      scrollFactor = event.GetWheelRotation()
      if scrollFactor < 0:
         print 'scrolling out'
         scrollFactor = 0.5
      elif scrollFactor > 0:
         print 'scrolling in'
         scrollFactor = 2
      self.canvas.Zoom(scrollFactor, event.GetPositionTuple(), 'pixel')

   def onRectLeftClick(self, object, event):
      print 'On Rect Left Click'
      if self.ctrl_down:
         if object.Name not in self.selectedRects:
            self.selectedRects.append(object.Name)
      else:
         if object.Name not in self.selectedRects:
            for rectnum in self.selectedRects:
               self.rects[rectnum][0].SetLineColor(NavigatorModel.colors['BLACK'])

            self.selectedRects = []
            self.selectedRects.append(object.Name)
      object.PutInForeground() # clicked rect pops to top
      object.Text.PutInForeground()
      object.SetLineColor(NavigatorModel.colors['WHITE'])
      self.canvas.Draw()

   def onRectRightClick(self, object, event):
      print 'On Rect Right Click'

   def onContextMenu(self, event):
      print 'On Context Menu'
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
      menu.Append(self.popupID1, "Arrange Horizontally")
      menu.Append(self.popupID2, "Arrange Vertically")
      menu.Append(self.popupID3, "Delete Selected")
      menu.Append(self.popupID4, "Lock")
      self.canvas.PopupMenu(menu)
      menu.Destroy()

   def onArrangeHorizontally(self, event):
      print 'Arrange Horizontally'

   def onArrangeVertically(self, event):
      print 'Arrange Vertically'

   def onDelete(self, event):
      print 'Delete'

   def onLock(self, event):
      print 'Lock'

   def onUpdateCtrl(self, event):
      self.ctrl_down = event.ControlDown()
      event.Skip()
      pass

   # def offCtrl(self, event):
   #    pass

   #--------------------------------------------------------------------------------------#
   # Initialize Methods
   #--------------------------------------------------------------------------------------#
   def show(self):
      self.mainWindow.Show()

   def populateScreen(self):
      # self.canvas.AddRectangle(self.canvas.PixelToWorld((20, 20)), (80, 35), lineWidth=2, FILLColor=wx.Colour('BLUE'))
      randnum = random
      randnum.seed()
      for i in xrange(10):
         xy = (randnum.randint(0, 800), randnum.randint(0, 600))
         rect = self.canvas.AddRectangle(self.canvas.PixelToWorld(xy), (80, 35), LineWidth=2, FillColor=NavigatorModel.colors['BLUE'])
         rect.Name = str(len(self.rects))
         rect.Bind(FloatCanvas.EVT_FC_LEFT_DOWN, lambda object, event=wx.MouseEvent(): self.onRectLeftClick(object, event)) # You can bind to the hit event of rectangle objects
         rect.Text = self.canvas.AddScaledText('Hello There', self.canvas.PixelToWorld((xy[0]+40, xy[1]-17.5)), 7, Position = "cc")
         self.rects[rect.Name] = [rect, pygame.Rect(xy[0], xy[1]-35, 80, 35)]
         rect.PutInBackground()
         rect.Text.PutInBackground()
      self.canvas.Draw()

   def moveRects(self, *args): # This is the autocorrection for overlap part
      try:
         if not self.collidingRects:
            self.timer.Stop()
            return
         for rectNum in self.collidingRects:
            rectNum = str(rectNum) # The key for the rect dict is a string

            for key, rect in self.rects.iteritems():# check collision against all rects
               if rect[1].collidepoint(self.rects[rectNum][1][0], self.rects[rectNum][1][1]):
                  lastRel = 1, 1
               elif rect[1].collidepoint(self.rects[rectNum][1][0]+self.rects[rectNum][1][2], self.rects[rectNum][1][1]):
                  lastRel = -1, 1
               elif rect[1].collidepoint(self.rects[rectNum][1][0], self.rects[rectNum][1][1]+self.rects[rectNum][1][3]):
                  lastRel = 1, -1
               elif rect[1].collidepoint(self.rects[rectNum][1][0]+self.rects[rectNum][1][2], self.rects[rectNum][1][1]+self.rects[rectNum][1][3]):
                  lastRel = -1, -1
               else:
                  lastRel = 0, 0

               self.rects[rectNum][0].Move((lastRel[0], -lastRel[1]))
               self.rects[rectNum][0].Text.Move((lastRel[0], -lastRel[1]))
               self.rects[rectNum][1][0] += lastRel[0]
               self.rects[rectNum][1][1] += lastRel[1]

         self.canvas.Draw()
         self.findCollidingRects()
         
      except wx._core.PyDeadObjectError:
         pass # TODO: warn user of unsafe closure

   def findCollidingRects(self):
      self.collidingRects = []

      pygameRects = {}
      for key, rect in self.rects.items():
         pygameRects[tuple(rect[1])] = key

      for key, rect in self.rects.iteritems():
         if (tuple(rect[1])) in pygameRects.keys():
            pygameRects.pop(tuple(rect[1]))
         collideIndex = rect[1].collidedictall(pygameRects)
         if collideIndex:
            for item in collideIndex:
               self.collidingRects.append(item[1])
         pygameRects[tuple(rect[1])] = key