from collections import deque
import numpy
from NavigatorModel import NavRect, RectDict
from NavigatorView import NavigatorFrame
from wx.lib.floatcanvas import FloatCanvas, GUIMode
from NavigatorFloatCanvas import NavGuiMove
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
      self.rectModel = NavigatorModel.NavRect

      # Bind normal events
      self.mainWindow.Bind(wx.EVT_MENU, self.onExit, self.mainWindow.menuExit)
      self.mainWindow.Bind(wx.EVT_MENU, self.onExport, self.mainWindow.menuExport)
      self.mainWindow.Bind(wx.EVT_MOUSEWHEEL, self.onScroll)
      self.canvas.Bind(wx.EVT_CONTEXT_MENU, self.onContextMenu)
      self.canvas.Bind(wx.EVT_KEY_DOWN, self.onKeyEvents)
      self.canvas.Bind(wx.EVT_KEY_UP, self.onKeyEvents)
      self.canvas.Bind(wx.EVT_MIDDLE_DOWN, self.onMiddleDn)
      self.canvas.Bind(wx.EVT_MIDDLE_UP, self.onMiddleUp)

      # Initialize member variables
      self.rects = RectDict()
      self.selectedRects = []
      self.mousePositions = deque([])
      self.mouseRel = 0, 0
      self.ctrl_down = False
      # Initial bounding box member variables
      self.Drawing = False
      self.RBRect = None
      self.StartPointWorld = None
      self.Tol = 5

      self.allArrows = []
      self.arrowCount = 0

      # @TODO: Remove this in the future, but for now populate the screen for prototyping
      self.enable()
      self.populateScreen()

   #--------------------------------------------------------------------------------------#
   # Initialization (not bindings)
   #--------------------------------------------------------------------------------------#
   def populateScreen(self):
      xy = (300, 200)
      rect = NavRect('1', self.canvas, 'Number 1', xy, (80, 35), 0, NavigatorModel.colors['BLUE'])
      rect.rect.Bind(FloatCanvas.EVT_FC_LEFT_DOWN, lambda object, event=wx.MouseEvent(): self.onRectLeftClick(object, event)) # You can bind to the hit event of rectangle objects
      rect.rect.Bind(FloatCanvas.EVT_FC_LEFT_DCLICK, lambda object, event=wx.MouseEvent(): self.onRectLeftDClick(object, event))
      self.rects.append(rect)
      rect.rect.PutInBackground()
      rect.rect.Text.PutInBackground()

      # Hardcode in the children, parents, revisions
      self.fake_revisions = ['1.0', '1.1']
      self.rects[rect.rect.Name].children = ['2', '3', '4', '5']
      self.rects[rect.rect.Name].parents = ['6', '7', '8']
      self.rects[rect.rect.Name].revisions = {'1.0': self.fake_revisions, '1.1': self.fake_revisions, '1.2': self.fake_revisions} #@TODO: _revisions doesn't populate

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

   def onExport(self, event):
      dlg = wx.FileDialog(self.canvas, message="Save file as ...", defaultDir=os.getcwd(),
                          defaultFile="", wildcard="*.png", style=wx.SAVE)
      if dlg.ShowModal() == wx.ID_OK:
         path = dlg.GetPath()
         if not(path[-4:].lower() == ".png"):
            path = path+".png"
         self.canvas.SaveAsImage(path)

   def onScroll(self, event):
      scrollFactor = event.GetWheelRotation()
      if scrollFactor < 0:
         scrollFactor = 0.5
      elif scrollFactor > 0:
         scrollFactor = 2
      self.mainWindow.NavCanvas.scale /= scrollFactor
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
            self.canvas.Bind(wx.EVT_MENU, self.onExpandChildren, id=self.popupID1)
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

      if len(self.selectedRects) > 1:
         if not hasattr(self, 'popupID5'):
            self.popupID5 = wx.NewId()
            self.popupID6 = wx.NewId()
            self.popupID7 = wx.NewId()
            self.popupID8 = wx.NewId()
            self.canvas.Bind(wx.EVT_MENU, self.onArrangeHorizontally, id=self.popupID5)
            self.canvas.Bind(wx.EVT_MENU, self.onArrangeVertically, id=self.popupID6)
            self.canvas.Bind(wx.EVT_MENU, self.onDelete, id=self.popupID7)
            self.canvas.Bind(wx.EVT_MENU, self.onLock, id=self.popupID8)
         menu = wx.Menu()
         menu.Append(self.popupID5, 'Arrange Horizontally')
         menu.Append(self.popupID6, 'Arrange Vertically')
         menu.Append(self.popupID7, 'Delete Selected')
         menu.Append(self.popupID8, 'Lock')
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
            self.rects[rectNum].rect.SetLineColor(NavigatorModel.colors['BLACK'])
            # TODO: Make _revShown a property within NavigatorModel
            if self.rects[rectNum]._revShown:
               for revision in self.rects[rectNum]._revisionRects:
                  revision.SetLineColor(NavigatorModel.colors['BLACK'])
         self.selectedRects = []

   # @TODO: fix the logic of where the band box stuff should go and clean up the code a bit
   def onDrag(self, event):
      if self.mainWindow.NavCanvas.panning:
         return
      # Draw the band box
      if self.Drawing:
         x, y = self.StartPoint
         cornerx, cornery = event.GetPosition()
         w, h = (cornerx - x, cornery - y)
         if abs(w) > self.Tol and abs(h) > self.Tol:
            # draw the RB box TODO: if the mouse leaves the screen then stop drawing
            dc = wx.ClientDC(self.canvas)
            dc.SetPen(wx.Pen(NavigatorModel.colors['WHITE'], 2, wx.SHORT_DASH))
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
         self.mouseRel = ((self.mousePositions[1][0] - self.mousePositions[0][0])*self.mainWindow.NavCanvas.scale,
                          -(self.mousePositions[1][1] - self.mousePositions[0][1])*self.mainWindow.NavCanvas.scale)
         self.mousePositions.popleft()

      # Move all the selected rects
      if event.Dragging() and not self.ctrl_down:
         if self.selectedRects:
            for rectNum in self.selectedRects:
               self.moveRect(self.rects[rectNum].rect, self.mouseRel)
               for revisionRect in self.rects[rectNum]._revisionRects:
                  self.moveRect(revisionRect, self.mouseRel)
               self.redrawArrows()
            self.canvas.Draw(False)
         else:
            pass

   def onLUp(self, event):
      # Stop drawing RBbox
      if self.Drawing:
         self.Drawing = False
         if self.RBRect:
            WH = event.Coords - self.StartPointWorld
            wx.CallAfter(self.drawBandBox, (self.StartPointWorld, WH))
         self.RBRect = None
         self.StartPointWorld = None

      # Set all selected rects back to background
      for rectObj in self.selectedRects:
         self.rects[rectObj].rect.PutInBackground()
         self.rects[rectObj].rect.Text.PutInBackground()
         for revisionRect in self.rects[rectObj]._revisionRects:
            revisionRect.PutInBackground()
            revisionRect.Text.PutInBackground()
      for arrow in self.allArrows:
         arrow.PutInBackground
      self.canvas.Draw()

   #--------------------------------------------------------------------------------------#
   # ContextMenu with Single Object Selected Bindings
   #--------------------------------------------------------------------------------------#
   def onExpandChildren(self, event):
      rectNum = self.selectedRects[0]
      if not self.rects[rectNum]._childrenShown:
         self.rects[rectNum]._childrenShown=True
         xy = (440, 200)
         index = xy[1]
         for rect in self.rects[rectNum].children:
            rect = NavRect(rect, self.canvas, 'Number ' + rect, xy, (80, 35), 0, NavigatorModel.colors['BLUE'])
            rect.rect.Bind(FloatCanvas.EVT_FC_LEFT_DOWN, lambda object, event=wx.MouseEvent(): self.onRectLeftClick(object, event)) # You can bind to the hit event of rectangle objects
            rect.rect.Bind(FloatCanvas.EVT_FC_LEFT_DCLICK, lambda object, event=wx.MouseEvent(): self.onRectLeftDClick(object, event))
            self.rects.append(rect)
            rect.rect.PutInBackground()
            rect.rect.Text.PutInBackground()
            self.drawArrows(self.rects[rectNum].rect, self.rects[rect].rect)
            index += 40
            xy = (xy[0], index)
         self.draw()


   def onAttributes(self, event):
      print 'Show Attributes'

   #--------------------------------------------------------------------------------------#
   # ContextMenu with Multiple Objects Selected Bindings
   #--------------------------------------------------------------------------------------#
   def onArrangeHorizontally(self, event):
      # TODO: account for width of revisions
      if self.selectedRects:
         firstRect = self.selectedRects[0]
         xpos1 = self.rects[firstRect].rect.BoundingBox.Left
         ypos1 = self.rects[firstRect].rect.BoundingBox.Top
         index = 0
         for rectNum in self.selectedRects:
            xpos2 = self.rects[rectNum].rect.BoundingBox.Left
            ypos2 = self.rects[rectNum].rect.BoundingBox.Top
            differencex = xpos1-xpos2+index
            differencey = ypos1-ypos2
            self.moveRect(self.rects[rectNum].rect, (differencex, differencey))
            if self.rects[rectNum]._revShown:
               for revisionRect in self.rects[rectNum]._revisionRects:
                  self.moveRect(revisionRect, (differencex, differencey))
                  index += revisionRect.BoundingBox.Width
            index += self.rects[rectNum].rect.BoundingBox.Width +5
         self.draw()

   def onArrangeVertically(self, event):
      if self.selectedRects:
         firstRect = self.selectedRects[0]
         xpos1 = self.rects[firstRect].rect.BoundingBox.Left
         ypos1 = self.rects[firstRect].rect.BoundingBox.Top
         index = 0
         for rectNum in self.selectedRects:
            xpos2 = self.rects[rectNum].rect.BoundingBox.Left
            ypos2 = self.rects[rectNum].rect.BoundingBox.Top
            differencex = xpos1-xpos2
            differencey = ypos1-ypos2+index
            self.moveRect(self.rects[rectNum].rect, (differencex, differencey))
            for revisionRect in self.rects[rectNum]._revisionRects:
               self.moveRect(revisionRect, (differencex, differencey))
            index -= self.rects[rectNum].rect.BoundingBox.Height + 10
         self.draw()

   def onDelete(self, event):
      #TODO: remove revisions
      print 'Delete'
      # for rectNum in self.selectedRects:
      #    self.rects[rectNum].rect.UnBindAll()
      #    for revisionRect in self.rects[rectNum]._revisionRects:
      #       self.canvas.RemoveObjects([revisionRect, revisionRect.Text])
      #    self.canvas.RemoveObjects((self.rects[rectNum].rect, self.rects[rectNum].rect.Text))
      #    del self.rects[rectNum]
      # self.selectedRects=[]
      # self.draw()

   def onLock(self, event):
      print 'On Lock'

   #--------------------------------------------------------------------------------------#
   # FloatCanvas Rect Bindings
   #--------------------------------------------------------------------------------------#
   def onRectLeftClick(self, object, event):
      if self.ctrl_down:
         if str(object.Name) not in self.selectedRects:
            self.selectedRects.append(object.Name)
      else:
         if object.Name not in self.selectedRects:
            for rectNum in self.selectedRects:
               self.rects[rectNum].rect.SetLineColor(NavigatorModel.colors['BLACK'])
               for revisionRect in self.rects[rectNum]._revisionRects:
                  revisionRect.SetLineColor(NavigatorModel.colors['BLACK'])

            self.selectedRects = []
            self.selectedRects.append(object.Name)
      object.PutInForeground() # clicked rect pops to top
      object.Text.PutInForeground()
      object.SetLineColor(NavigatorModel.colors['WHITE'])
      if self.rects[object.Name]._revShown:
         for revisionRect in self.rects[object.Name]._revisionRects:
            revisionRect.PutInForeground()
            revisionRect.Text.PutInForeground()
            revisionRect.SetLineColor(NavigatorModel.colors['WHITE'])
      self.canvas.Draw()

   def onRectLeftDClick(self, object, event):
      if self.rects[object.Name]._revShown: #collapse the revisions and remove them from the screen
         self.rects[object.Name]._revShown = False
         for revisionRect in self.rects[object.Name]._revisionRects:
            self.canvas.RemoveObjects([revisionRect, revisionRect.Text])
         self.rects[object.Name]._revisionRects = []
      else:
         # Get the right middle position of the rectangle
         xy = object.BoundingBox.Right, object.BoundingBox.Center[1] - object.BoundingBox.Height/4
         # Loop through the keys in a dict
         for revision in self.rects[object.Name].revisions:
            rect = self.canvas.AddRectangle(xy, (40, 17.5), LineWidth=0, FillColor=NavigatorModel.colors['BLUE'], LineColor='WHITE')
            rect.Name = '%s' % revision
            rect.Text = self.canvas.AddScaledText('%s' % revision, (xy[0]+20, xy[1]+8.75), 7, Position = "cc")
            self.rects[object.Name]._revisionRects.append(rect)
            xy = xy[0] + 40, xy[1]
            self.rects[object.Name]._revShown=True
      self.draw()

   #--------------------------------------------------------------------------------------#
   # Drawing Methods
   #--------------------------------------------------------------------------------------#
   def draw(self):
      self.redrawArrows()
      self.canvas.Draw()

   # @TODO: Optimize this code a lot
   def drawArrows(self, rect1, rect2):
      # Get the smaller rect width and rect height
      if rect1.BoundingBox.Width <= rect2.BoundingBox.Width:minWidth = rect1.BoundingBox.Width
      else: minWidth = rect2.BoundingBox.Width
      if rect1.BoundingBox.Height <= rect2.BoundingBox.Height:minHeight = rect1.BoundingBox.Height
      else: minHeight = rect2.BoundingBox.Height
      # Use the absolute width and height to determine the middle width and middle height
      absoluteWidth = abs(rect1.BoundingBox.Center[0]-rect2.BoundingBox.Center[0])
      absoluteHeight = abs(rect1.BoundingBox.Center[1]-rect2.BoundingBox.Center[1])

      # Determining all cases where the arrows should be
      if rect1.BoundingBox.Center[0] <= rect2.BoundingBox.Center[0]:
         if rect1.BoundingBox.Center[1] >= rect2.BoundingBox.Center[1]: #x1<=x2 and y1>=y2
            xy1 = rect1.BoundingBox.Right, rect1.BoundingBox.Bottom
            xy2 = rect2.BoundingBox.Left, rect2.BoundingBox.Top
            if absoluteHeight<=minHeight: #In the middle height of the rects
               xy1=rect1.BoundingBox.Right, rect1.BoundingBox.Center[1]-absoluteHeight/3
               xy2=rect2.BoundingBox.Left, rect2.BoundingBox.Center[1]+absoluteHeight/3
         else: #x1<=x2 && y1<y2
            xy1 = rect1.BoundingBox.Right, rect1.BoundingBox.Top
            xy2 = rect2.BoundingBox.Left, rect2.BoundingBox.Bottom
            if absoluteHeight<=minHeight: #In the middle height of the rects
               xy1=rect1.BoundingBox.Right, rect1.BoundingBox.Center[1]+absoluteHeight/3
               xy2=rect2.BoundingBox.Left, rect2.BoundingBox.Center[1]-absoluteHeight/3
         if absoluteWidth<minWidth: # In the middle width of the rects
            xy1 = rect1.BoundingBox.Center[0]+absoluteWidth/2, xy1[1]
            xy2 = rect2.BoundingBox.Center[0]-absoluteWidth/2, xy2[1]
      else:
         if rect1.BoundingBox.Center[1] >= rect2.BoundingBox.Center[1]: #x1>x2 and y1>=y2
            xy1 = rect1.BoundingBox.Left, rect1.BoundingBox.Bottom
            xy2 = rect2.BoundingBox.Right, rect2.BoundingBox.Top
            if absoluteHeight<=minHeight: #In the middle height of the rects
               xy1=rect1.BoundingBox.Left, rect1.BoundingBox.Center[1]-absoluteHeight/3
               xy2=rect2.BoundingBox.Right, rect2.BoundingBox.Center[1]+absoluteHeight/3
         else:# x1>x2 and y1<y2
            xy1 = rect1.BoundingBox.Left, rect1.BoundingBox.Top
            xy2 = rect2.BoundingBox.Right, rect2.BoundingBox.Bottom
            if absoluteHeight<=minHeight: #In the middle height of the rects
               xy1=rect1.BoundingBox.Left, rect1.BoundingBox.Center[1]+absoluteHeight/3
               xy2=rect2.BoundingBox.Right, rect2.BoundingBox.Center[1]-absoluteHeight/3
         if absoluteWidth<minWidth: #In the middle width of the rects
            xy1 = rect1.BoundingBox.Center[0]-absoluteWidth/2, xy1[1]
            xy2 = rect2.BoundingBox.Center[0]+absoluteWidth/2, xy2[1]
      self.arrowCount += 1
      arrow = self.canvas.AddArrowLine((xy1, xy2), LineWidth =1, LineColor=NavigatorModel.colors['BLACK'], ArrowHeadSize=10, InForeground=False)
      self.allArrows.append(arrow)
      
   def drawBandBox(self, rect):
      # Get the four corner coordinates of the RBRect
      x1, y1 = rect[0][0], rect[0][1]
      x2, y2 = rect[1][0]+x1, rect[1][1]+y1
      # Make sure x1<x2 and y1<y2
      if x2 <= x1:
         x1, x2 = x2, x1
      if y2 <= y1:
         y1, y2 = y2, y1
      for rectNum in self.rects:
         if x1 <= self.rects[rectNum].rect.BoundingBox.Center[0] <= x2 and \
            y1 <= self.rects[rectNum].rect.BoundingBox.Center[1] <= y2:
            self.selectedRects.append(rectNum.name)
            self.rects[rectNum].rect.PutInForeground() # clicked rect pops to top
            self.rects[rectNum].rect.Text.PutInForeground()
            self.rects[rectNum].rect.SetLineColor(NavigatorModel.colors['WHITE'])
            if self.rects[rectNum]._revShown:
               for revisionRect in self.rects[rectNum]._revisionRects:
                  revisionRect.PutInForeground()
                  revisionRect.Text.PutInForeground()
                  revisionRect.SetLineColor(NavigatorModel.colors['WHITE'])
      self.canvas.Draw()

   def moveRect(self, rect, (x,y)):
      rect.PutInForeground()
      rect.Text.PutInForeground()
      rect.Move((x,y))
      rect.Text.Move((x,y))

   # @TODO: Move this to our expand children
   def redrawArrows(self):
      self.canvas.RemoveObjects(self.allArrows)
      self.arrowCount = 0
      self.allArrows = []
      for rectNum in self.rects:
         if not self.rects[rectNum]._revShown and self.rects[rectNum]._childrenShown:
            for rect in self.rects[rectNum].children:
               self.drawArrows(self.rects[rectNum].rect, self.rects[rect].rect)
         if self.rects[rectNum]._revShown and self.rects[rectNum]._childrenShown:
            for revisionRect in self.rects[rectNum]._revisionRects:
               for rect in self.rects[rectNum].children:
                  self.drawArrows(revisionRect, self.rects[rect].rect)
         # #
         # if self.rects[rectNum]._childrenShown:
         #    for rect in self.rects[rectNum].children:
         #       self.drawArrows(self.rects[rectNum].rect, self.rects[rect].rect)

   def onMiddleDn(self, event):
      mode = NavGuiMove(event, self.canvas)
      self.canvas.SetMode(mode)
      self.mainWindow.NavCanvas.panning = True

      mode.Canvas.SetCursor(mode.GrabCursor)
      mode.StartMove = numpy.array(event.GetPosition())
      mode.MidMove = mode.StartMove
      mode.PrevMoveXY = (0, 0)

   def onMiddleUp(self, event):
      mode = GUIMode.GUIMouse(self.canvas)
      self.canvas.SetMode(mode)
      self.mainWindow.NavCanvas.panning = False