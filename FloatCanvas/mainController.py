from collections import deque
from mainView import MainFrame
import wx
from wx.lib.floatcanvas import NavCanvas, FloatCanvas, Resources
import pygame
import random
import itertools

pygame.init()

BLACK = wx.Colour(0, 0, 0)
BLUE = wx.Colour(100, 223, 237, 200)
GREY = wx.Colour(173,173,173)
RED = wx.Colour(255, 0, 0)
WHITE = wx.Colour(255, 255, 255)

def BB_HitTest(self, event, HitEvent):
    """ Hit Test Function for BoundingBox Based HitMap System"""
    if self.HitDict and self.HitDict[HitEvent]:
        # loop though the objects associated with this event
        objects = [] #Create object list for holding multiple objects
        object_index_list = [] #Create list for holding the indexes
        xy_p = event.GetPosition()
        xy = self.PixelToWorld( xy_p ) #Convert to the correct coords
        for key2 in self.HitDict[HitEvent].keys():
            #Get Mouse Event Position
            bb =  self.HitDict[HitEvent][key2].BoundingBox
            if bb.PointInside(xy):
                Object = self.HitDict[HitEvent][key2]
                objects.append(Object)
                try:
                    #First try the foreground index and add the length of the background index
                    #to account for the two 'layers' that already exist in the code
                    index = self._ForeDrawList.index(Object) + len(self._DrawList)
                except ValueError:
                    index = self._DrawList.index(Object) #Now check background if not found in foreground
                object_index_list.append(index) #append the index found
            else:
                Object = self.HitDict[HitEvent][key2]
        if len(objects) > 0: #If no objects then do nothing
            #Get the highest index object
            highest_object = objects[object_index_list.index(max(object_index_list))]
            highest_object.HitCoords = xy
            highest_object.HitCoordsPixel = xy_p
            highest_object.CallBackFuncs[HitEvent](highest_object)
            return True
        else:
            return False
    return False

FloatCanvas.FloatCanvas.HitTest = BB_HitTest


N_RECTANGLES = 1500
randnum = random
randnum.seed()

class Main:
   def __init__(self, parent=None):
      self.mainWindow = MainFrame(None)
      self.mainWindow.SetSize((1024, 768))
      wx.GetApp().Yield(True)

      self.canvas = self.mainWindow.Canvas
      self.canvas.InitializePanel()

      # Bind normal events
      self.mainWindow.Bind(wx.EVT_MENU, self.exit, self.mainWindow.menuExit)
      self.mainWindow.Bind(wx.EVT_KEY_DOWN, self.onCtrl, self.mainWindow.Canvas)
      self.mainWindow.Bind(wx.EVT_KEY_UP, self.offCtrl, self.mainWindow.Canvas)

      # Bind events to FloatCanvas
      self.canvas.Bind(FloatCanvas.EVT_LEFT_DOWN, self.onClick)
      self.canvas.Bind(FloatCanvas.EVT_MOTION, self.onDrag)
      self.canvas.Bind(FloatCanvas.EVT_LEFT_UP, self.onUp)

      # Initialize defaults in the floatcanvas
      self.canvas.InitAll()
      self.canvas.Draw()

      # initialize member variables
      self.rects = {}
      self.selectedRects = []
      self.collidingRects = []
      self.mousePositions = deque([])
      self.timer = wx.PyTimer(self.moveRects)
      self.frameDelay = 30

      self.show()
      for i in xrange(N_RECTANGLES):
         self.onClick(None)

   def show(self, *args, **kwargs):
      self.mainWindow.Show()

   def exit(self, *args):
      self.mainWindow.Destroy()
      exit()

   def onCtrl(self, event):
      print 'controlled'

   def offCtrl(self, event):
      pass

   def onClick(self, event):
      for rectNum in self.rects:
         self.rects[rectNum][0].SetLineColor(BLACK)

      self.selectedRects = []

      if not event or not event.Dragging():
         if event:
            xy = event.GetX(), event.GetY()
         else:
            xy = (randnum.randint(0, 800), randnum.randint(0, 600))
         rect = self.canvas.AddRectangle(self.canvas.PixelToWorld(xy), (80, 35), LineWidth=2, FillColor=BLUE)
         rect.Name = str(len(self.rects))
         rect.HitFill = False
         rect.HitLineWidth = 10
         rect.Bind(FloatCanvas.EVT_FC_LEFT_DOWN, lambda object, evt=wx.MouseEvent(): self.onRectHit(object, evt)) # You can bind to the hit event of rectangle objects
         self.rects[rect.Name] = [rect, pygame.Rect(xy[0], xy[1]-35, 80, 35)]
         rect.PutInBackground()
         if event:
            self.canvas.Draw()

   def onUp(self, event):
      for rectObj in self.canvas._ForeDrawList: # Only the moving rects should be in the foreground
         rectObj.PutInBackground()

      # self.findCollidingRects()
      # if self.collidingRects:
      #    self.timer.Start(self.frameDelay)
      # self.canvas.Draw()

   def onDrag(self, event):
      # Calculate change in mouse position since last event using a queue system
      self.canvas._BackgroundDirty = False
      self.mousePositions.append((event.GetX(), event.GetY()))
      if len(self.mousePositions) == 2:
         self.mouserel = ((self.mousePositions[1][0] - self.mousePositions[0][0]),
                          -(self.mousePositions[1][1] - self.mousePositions[0][1]))
         self.mousePositions.popleft()

      if event.Dragging():
         if self.selectedRects:
            for rectNum in self.selectedRects:
               if self.rects[rectNum][0] not in self.canvas._ForeDrawList:
                  self.rects[rectNum][0].PutInForeground() # Moving rects go in foreground
               self.rects[rectNum][0].Move(self.mouserel)
               # Also have to update the 'virtual' rect stored in the pygame object
               self.rects[rectNum][1][0] += self.mouserel[0]
               self.rects[rectNum][1][1] += -self.mouserel[1]
            self.canvas.Draw(False)
         else:
            pass
            # TODO: Add logic for drawing selection rectangle

   def onRectHit(self, object, event):

      if event.ControlDown():
         if object.Name not in self.selectedRects:
            self.selectedRects.append(object.Name)
      else:
         if object.Name not in self.selectedRects:
            for rectnum in self.selectedRects:
               self.rects[rectnum][0].SetLineColor(BLACK)

            self.selectedRects = []
            self.selectedRects.append(object.Name)

      object.PutInForeground() # clicked rect pops to top
      object.SetLineColor(WHITE)
      # self.canvas._BackgroundDirty = True
      # self.canvas.Draw()

   def moveRects(self, *args): # This is the autocorrection for overlap part
      try:
         if not self.collidingRects:
            self.timer.Stop()
            return
         for rectNum in self.collidingRects:
            rectNum = str(rectNum) # The key for the rect dict is a string

            for key, rect in self.rects.iteritems():# check collision against all rects
               if rect[1].collidepoint(self.rects[rectNum][1][0], self.rects[rectNum][1][1]):
                  lastrel = 1, 1
               elif rect[1].collidepoint(self.rects[rectNum][1][0]+self.rects[rectNum][1][2], self.rects[rectNum][1][1]):
                  lastrel = -1, 1
               elif rect[1].collidepoint(self.rects[rectNum][1][0], self.rects[rectNum][1][1]+self.rects[rectNum][1][3]):
                  lastrel = 1, -1
               elif rect[1].collidepoint(self.rects[rectNum][1][0]+self.rects[rectNum][1][2], self.rects[rectNum][1][1]+self.rects[rectNum][1][3]):
                  lastrel = -1, -1
               else:
                  lastrel = 0, 0

               self.rects[rectNum][0].Move((lastrel[0], -lastrel[1]))
               self.rects[rectNum][1][0] += lastrel[0]
               self.rects[rectNum][1][1] += lastrel[1]

         self.canvas.Draw()
         self.findCollidingRects()
      except wx._core.PyDeadObjectError:
         pass # TODO: warn user of unsafe closure

   def findCollidingRects(self):
      # print self.collidingRects
      self.collidingRects = []
      pygamerects = dict((tuple(rect[1]), key) for key, rect in self.rects.items())  # Make a temp list of just the pygame objects for collision detection

      for key, rect in self.rects.iteritems():
         if (tuple(rect[1])) in pygamerects.keys():
            pygamerects.pop(tuple(rect[1]))
         colIndex = rect[1].collidedictall(pygamerects)
         if colIndex:
            colIndex = colIndex[0][1]
            self.collidingRects.append(colIndex)
         pygamerects[tuple(rect[1])] = key

      # self.collidingRects = [index for index in self.collidingRects if index != []]
      # self.collidingRects = list(itertools.chain.from_iterable(self.collidingRects))

      # self.collidingRects = filter(lambda a: a != -1,
      #                              self.collidingRects)  # Remove all instances of -1 from the collision list
      # self.collidingRects = list(set(self.collidingRects)) # Remove duplicates

      if not self.collidingRects: self.timer.Stop()