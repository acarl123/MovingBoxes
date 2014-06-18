import os, sys
sys.path.append('C:\\hg\\tools_lag\\EFSUtils')
from collections import deque
from ConfigFile import *
from DirectoryToken import *
from NavigatorModel import NavRect, RectDict
from NavigatorView import NavigatorFrame
from wx.lib.floatcanvas import FloatCanvas, GUIMode
from NavigatorFloatCanvas import NavGuiMove
import AddNodeDlg
import AttributeDlg
import BackgroundFunctionDlg
import cPickle
import ExportFileBusinessObject as efbo
import ExportFileRelationship as efrel
import ExportFileUtils
import MDXUtils
import NavigatorModel
import numpy
import TypeColors
import random
import wx
FloatCanvas.FloatCanvas.HitTest = NavigatorModel.BB_HitTest

class NavigatorController:
   def __init__(self):
      # Setup view
      self.mainWindow = NavigatorFrame(None)
      self.makeLegend()

      # Initialize FloatCanvas defaults
      self.canvas = self.mainWindow.NavCanvas.Canvas
      self.canvas.InitializePanel()
      self.canvas.InitAll()
      self.canvas.Draw()

      # Setup model and efs
      self.rectModel = NavigatorModel.NavRect
      self.Config = ConfigFile('Config.txt')
      self.efs = ExportFileUtils.ExportFileSet()
      self.busObjDict = self.efs.newBusinessObjectDict(bodType=efbo.BOD_BOOLEAN_TYPE)
      self.addNodeDlg = AddNodeDlg.AddNodeDlg(self.canvas, self.efs)

      # Bind normal canvas events
      self.canvas.Bind(wx.EVT_CONTEXT_MENU, self.onContextMenu)
      self.canvas.Bind(wx.EVT_KEY_DOWN, self.onKeyEvents) #TODO: fix it so these are actually binding
      self.canvas.Bind(wx.EVT_KEY_UP, self.onKeyEvents)
      self.canvas.Bind(wx.EVT_MIDDLE_DOWN, self.onMiddleDn)
      self.canvas.Bind(wx.EVT_MIDDLE_UP, self.onMiddleUp)
      # Bind normal window events
      self.mainWindow.Bind(wx.EVT_MENU, self.onAddObject, self.mainWindow.menuAddObject)
      self.mainWindow.Bind(wx.EVT_MENU, self.onExit, self.mainWindow.menuExit)
      self.mainWindow.Bind(wx.EVT_MENU, self.onExport, self.mainWindow.menuExport)
      self.mainWindow.Bind(wx.EVT_MENU, self.onOpen, self.mainWindow.menuOpen)
      self.mainWindow.Bind(wx.EVT_MENU, self.onSave, self.mainWindow.menuSave)
      self.mainWindow.Bind(wx.EVT_MOUSEWHEEL, self.onScroll)

      # Initialize member variables
      self.rects = RectDict()
      self.revisionRects = {} # Used for rectangles that are drawn on the canvas only
      self.selectedRects = []
      self.expandingRects = []
      self.mousePositions = deque([])
      self.mouseRel = 0, 0
      self.ctrl_down = False
      self.allArrows = []
      self.arrowCount = 0
      self.enable()

      # Initial bounding box member variables
      self.Drawing = False
      self.RBRect = None
      self.StartPointWorld = None
      self.Tol = 5

   #--------------------------------------------------------------------------------------#
   # Initialization (not bindings)
   #--------------------------------------------------------------------------------------#
   def show(self):
      self.mainWindow.Show()

   def enable(self):
      # Bind events to FloatCanvas
      self.canvas.Bind(FloatCanvas.EVT_LEFT_DOWN, self.onClick)
      self.canvas.Bind(FloatCanvas.EVT_MOTION, self.onDrag)
      self.canvas.Bind(FloatCanvas.EVT_LEFT_UP, self.onLUp)

   def disable(self):
      # Unbind events to FloatCanvas
      self.canvas.Unbind(FloatCanvas.EVT_LEFT_DOWN, self.onClick)
      self.canvas.Unbind(FloatCanvas.EVT_MOTION, self.onDrag)
      self.canvas.Unbind(FloatCanvas.EVT_LEFT_UP, self.onLUp)

   def makeLegend(self):
      listCtrl = self.mainWindow.m_listCtrl1
      listCtrl.InsertColumn(0, 'Type', width=75)
      listCtrl.InsertColumn(1, 'Color',) # TODO: use list autowidth mixin

      for type, color in TypeColors.ObjColorDict.iteritems():
         index = listCtrl.InsertStringItem(sys.maxint, type)
         listCtrl.SetStringItem(index, 1, ' ')
         item = listCtrl.GetItem(index)
         item.SetBackgroundColour(color)
         listCtrl.SetItem(item)

   def OpenFile (self, file):
      # Parse and populate the dictionary
      self.efs.parseFiles (file, ignoreDanglingRefs=False, skipRels=False)
      self.busObjDict = self.efs.getAllBusinessObjectsDict()

   #--------------------------------------------------------------------------------------#
   # Normal Canvas Bindings
   #--------------------------------------------------------------------------------------#
   def onKeyEvents(self, event):
      self.ctrl_down = event.ControlDown()
      if event.GetKeyCode() == wx.WXK_DELETE:
         self.onDelete(event)

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

   #--------------------------------------------------------------------------------------#
   # Normal Window Bindings
   #--------------------------------------------------------------------------------------#
   # TODO: Need to eventually redo Matt Fuller's code but this addNodeDlg works for now
   def onAddObject(self, event):
      if (self.addNodeDlg.ShowModal () == wx.ID_OK):
         if (self.addNodeDlg.ReturnBOs != None):
            for bo in self.addNodeDlg.ReturnBOs:
               xy = (random.randint(0, self.mainWindow.GetSize()[0]), random.randint(0, self.mainWindow.GetSize()[1]))
               self.boType = efbo.getTypeName(bo)
               if self.boType in TypeColors.ObjColorDict:
                  colorSet = TypeColors.ObjColorDict[self.boType]
                  rect = NavRect(bo, self.mainWindow.NavCanvas, '%s' % efbo.getName(bo), xy, (80, 35), 0, colorSet)
               else:
                  rect = NavRect(bo, self.mainWindow.NavCanvas, '%s' % efbo.getName(bo), xy, (80, 35), 0, NavigatorModel.colors['WHITE'])
               rect.rect.Bind(FloatCanvas.EVT_FC_LEFT_DOWN, lambda object, event=wx.MouseEvent(): self.onRectLeftClick(object, event)) # You can bind to the hit event of rectangle objects
               rect.rect.Bind(FloatCanvas.EVT_FC_LEFT_DCLICK, lambda object, event=wx.MouseEvent(): self.onRectLeftDClick(object, event))
               self.rects.append(rect)
               rect.rect.PutInBackground()
               rect.rect.Text.PutInBackground()
         self.draw()

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
            self.popupID5 = wx.NewId()
            self.canvas.Bind(wx.EVT_MENU, self.onExpandRevisions, id=self.popupID1)
            self.canvas.Bind(wx.EVT_MENU, self.onAttributes, id=self.popupID2)
            self.canvas.Bind(wx.EVT_MENU, self.onDelete, id=self.popupID3)
            self.canvas.Bind(wx.EVT_MENU, self.onLock, id=self.popupID4)
            self.canvas.Bind(wx.EVT_MENU, self.onExpandOutgoing, id=self.popupID5)
         menu = wx.Menu()
         menu.Append(self.popupID1, 'Expand Revisions')
         menu.Append(self.popupID2, 'Attributes/Properties')
         menu.Append(self.popupID3, 'Delete Selected')
         menu.Append(self.popupID4, 'Lock')
         menu.Append(self.popupID5, 'Expand Outgoing')
         self.canvas.PopupMenu(menu)
         menu.Destroy()
         return

      if len(self.selectedRects) > 1:
         if not hasattr(self, 'popupID6'):
            self.popupID6 = wx.NewId()
            self.popupID7 = wx.NewId()
            self.popupID8 = wx.NewId()
            self.popupID9 = wx.NewId()
            self.canvas.Bind(wx.EVT_MENU, self.onArrangeHorizontally, id=self.popupID6)
            self.canvas.Bind(wx.EVT_MENU, self.onArrangeVertically, id=self.popupID7)
            self.canvas.Bind(wx.EVT_MENU, self.onDelete, id=self.popupID8)
            self.canvas.Bind(wx.EVT_MENU, self.onLock, id=self.popupID9)
         menu = wx.Menu()
         menu.Append(self.popupID6, 'Arrange Horizontally')
         menu.Append(self.popupID7, 'Arrange Vertically')
         menu.Append(self.popupID8, 'Delete Selected')
         menu.Append(self.popupID9, 'Lock')
         self.canvas.PopupMenu(menu)
         menu.Destroy()

   def onOpen(self, event):
      dlg = wx.FileDialog(
            self.canvas, message="Opening an EFS...",
            defaultDir=os.getcwd(),
            defaultFile="",
            wildcard="EFS files (*txt)|*.txt",
            style=wx.OPEN | wx.CHANGE_DIR
            )
      if dlg.ShowModal() == wx.ID_OK:
         path = dlg.GetPath()
         print "Opening:" + path
         dlg = BackgroundFunctionDlg.BackgroundFunctionDlg(self.canvas, 'Opening EFS', self.OpenFile, path)
         dlg.Go()
      dlg.Destroy()

   def onSave(self, event):
      print 'saved'

   def onScroll(self, event):
      scrollFactor = event.GetWheelRotation()
      if scrollFactor < 0:
         scrollFactor = 0.5
      elif scrollFactor > 0:
         scrollFactor = 2
      self.mainWindow.NavCanvas.scale /= scrollFactor
      self.canvas.Zoom(scrollFactor, event.GetPositionTuple(), 'pixel')

   #--------------------------------------------------------------------------------------#
   # FloatCanvas Bindings
   #--------------------------------------------------------------------------------------#
   def onClick(self, event):
      # Start drawing band box
      self.Drawing = True
      self.StartPoint = event.GetPosition()
      self.StartPointWorld = event.Coords

      if not self.ctrl_down:
         for bo in self.rects:
            self.rects[bo].rect.SetLineColor(NavigatorModel.colors['BLACK'])
            if self.rects[bo]._revShown:
               for revision in self.rects[bo]._revisionRects:
                  self.rects[bo]._revisionRects[revision].SetLineColor(NavigatorModel.colors['BLACK'])
         self.selectedRects = []

   # @TODO: fix the logic of where the band box stuff should go and clean up the code a bit
   def onDrag(self, event):
      if self.mainWindow.NavCanvas.panning: return
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
            for bo in self.selectedRects:
               self.moveRect(self.rects[bo].rect, self.mouseRel)
               for revision in self.rects[bo]._revisionRects:
                  self.moveRect(self.rects[bo]._revisionRects[revision], self.mouseRel)
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
      for bo in self.selectedRects:
         self.rects[bo].rect.PutInBackground()
         self.rects[bo].rect.Text.PutInBackground()
         for revision in self.rects[bo]._revisionRects:
            self.rects[bo]._revisionRects[revision].PutInBackground()
            self.rects[bo]._revisionRects[revision].Text.PutInBackground()
      for arrow in self.allArrows:
         arrow.PutInBackground()
      self.draw()

   #--------------------------------------------------------------------------------------#
   # ContextMenu with Single Object Selected Bindings
   #--------------------------------------------------------------------------------------#
   def onExpandRevisions(self, event):
      bo = self.selectedRects[0] # TODO: For group selection we need to go through the entire selected rects
      if self.rects[bo]._revShown:
         self.rects[bo]._revShown = False
         for revision in self.rects[bo]._revisionRects:
            self.canvas.RemoveObjects([self.rects[bo]._revisionRects[revision], self.rects[bo]._revisionRects[revision].Text])
         self.rects[bo]._revisionRects = {}
      else:
         self.rects[bo]._revShown = True
         xy = self.rects[bo].rect.BoundingBox.Right, self.rects[bo].rect.BoundingBox.Center[1] - self.rects[bo].rect.BoundingBox.Height/4
         for revision in efbo.getAllRevisions(bo, self.busObjDict):
            self.boType = efbo.getTypeName(revision)
            if self.boType in TypeColors.ObjColorDict:
               colorSet = TypeColors.ObjColorDict[self.boType]
               #TODO: eventually revs need to be selectable and remove hardcoded size
               rect = self.canvas.AddRectangle(xy, (40, 17.5), LineWidth=0, FillColor=colorSet, LineColor='WHITE')
            else:
               rect = self.canvas.AddRectangle(xy, (40, 17.5), LineWidth=0, FillColor=NavigatorModel.colors['WHITE'], LineColor='WHITE')
            rect.Name = '%s' % efbo.getRevision(revision)
            rect.Text = self.canvas.AddScaledText('%s' % efbo.getRevision(revision), (xy[0]+20, xy[1]+8.75), 7, Position = "cc")
            # TODO: Put in bindings maybe
            rect.PutInBackground()
            rect.Text.PutInBackground()
            self.rects[bo]._revisionRects[int(revision)] = rect
            xy = xy[0] + 40, xy[1]
      self.draw()

   def onExpandOutgoing(self, event):
      bo = self.selectedRects[0]
      self.selectedRects = []
      xy = (440, 200) # TODO: this needs to be calculated not hardcoded in
      for revision in efbo.getAllRevisions(bo, self.busObjDict):
         relationships = efbo.getFromRelationship(revision)
         for rel in relationships:
            if efrel.getTypeName(rel) == MDXUtils.REL_AD: continue
            toBo = efrel.getTo(rel)
            if not self.rects[toBo]: # Check if the bo is already on the canvas
               self.boType = efbo.getTypeName(toBo)
               if self.boType in TypeColors.ObjColorDict:
                  colorSet = TypeColors.ObjColorDict[self.boType]
                  rect = NavRect(toBo, self.mainWindow.NavCanvas, '%s' % efbo.getName(toBo), xy, (80, 35), 0, colorSet)
               else:
                  rect = NavRect(toBo, self.mainWindow.NavCanvas, '%s' % efbo.getName(toBo), xy, (80, 35), 0, NavigatorModel.colors['WHITE'])
               rect.rect.Bind(FloatCanvas.EVT_FC_LEFT_DOWN, lambda object, event=wx.MouseEvent(): self.onRectLeftClick(object, event))
               rect.rect.Bind(FloatCanvas.EVT_FC_LEFT_DCLICK, lambda object, event=wx.MouseEvent(): self.onRectLeftDClick(object, event))
               rect.rect.PutInBackground()
               rect.rect.Text.PutInBackground()
               self.selectedRects.append(toBo)
               self.rects.append(rect)
               self.drawArrows(self.rects[bo].rect, self.rects[toBo].rect) # Draw arrows between the two rects
      self.onArrangeVertically(event)

   # TODO: Add third parameter for node and use the attribute dialog that is already written
   def onAttributes(self, event):
      print 'Show Attributes'
      bo = self.selectedRects[0]
      dlg = AttributeDlg.AttributeDlg(self.canvas, self.rects[bo].rect.Name)
      dlg.Show()

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
         for bo in self.selectedRects:
            xpos2 = self.rects[bo].rect.BoundingBox.Left
            ypos2 = self.rects[bo].rect.BoundingBox.Top
            differencex = xpos1-xpos2+index
            differencey = ypos1-ypos2
            self.moveRect(self.rects[bo].rect, (differencex, differencey))
            if self.rects[bo]._revShown:
               for revision in self.rects[bo]._revisionRects:
                  self.moveRect(self.rects[bo]._revisionRects[revision], (differencex, differencey))
                  index += self.rects[bo]._revisionRects[revision].BoundingBox.Width
            index += self.rects[bo].rect.BoundingBox.Width + 5 #TODO: allow the user to change this hardcoded 5
         self.draw()

   def onArrangeVertically(self, event):
      if self.selectedRects:
         firstRect = self.selectedRects[0]
         xpos1 = self.rects[firstRect].rect.BoundingBox.Left
         ypos1 = self.rects[firstRect].rect.BoundingBox.Top
         index = 0
         for bo in self.selectedRects:
            # self.rects[rectNum].rect.SetLineColor(NavigatorModel.colors['WHITE'])
            xpos2 = self.rects[bo].rect.BoundingBox.Left
            ypos2 = self.rects[bo].rect.BoundingBox.Top
            differencex = xpos1-xpos2
            differencey = ypos1-ypos2+index
            self.moveRect(self.rects[bo].rect, (differencex, differencey))
            if self.rects[bo]._revShown:
               for revision in self.rects[bo]._revisionRects:
                  self.moveRect(self.rects[bo]._revisionRects[revision], (differencex, differencey))
            index -= self.rects[bo].rect.BoundingBox.Height + 10
         self.draw()

   def onDelete(self, event):
      #TODO: remove revisions
      for bo in self.selectedRects:
         self.rects[bo].rect.UnBindAll()
         if self.rects[bo]._revShown:
            for revision in self.rects[bo]._revisionRects:
               self.canvas.RemoveObjects([self.rects[bo]._revisionRects[revision], self.rects[bo]._revisionRects[revision].Text])
            self.rects[bo]._revisionRects = {}
         self.canvas.RemoveObjects((self.rects[bo].rect, self.rects[bo].rect.Text))
         del self.rects[bo]
      self.selectedRects=[]
      self.draw()

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
            for bo in self.selectedRects:
               self.rects[bo].rect.SetLineColor(NavigatorModel.colors['BLACK'])
               if self.rects[bo]._revShown:
                  for revision in self.rects[bo]._revisionRects:
                     self.rects[bo]._revisionRects[revision].SetLineColor(NavigatorModel.colors['BLACK'])
            self.selectedRects = []
            self.selectedRects.append(object.Name)
      object.PutInForeground() # clicked rect pops to top
      object.Text.PutInForeground()
      object.SetLineColor(NavigatorModel.colors['WHITE'])
      if self.rects[object.Name]._revShown:
         for revision in self.rects[object.Name]._revisionRects:
            self.rects[object.Name]._revisionRects[revision].PutInForeground()
            self.rects[object.Name]._revisionRects[revision].Text.PutInForeground()
            self.rects[object.Name]._revisionRects[revision].SetLineColor(NavigatorModel.colors['WHITE'])
      self.canvas.Draw()

   def onRectLeftDClick(self, object, event):
      self.selectedRects = []
      self.selectedRects.append(object.Name)
      self.onExpandRevisions(event)

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
      arrow = self.canvas.AddArrowLine((xy1, xy2), LineWidth=1, LineColor='BLACK', ArrowHeadSize=10, InForeground=False)
      self.allArrows.append(arrow)
      self.canvas.Draw()

   def drawBandBox(self, rect):
      # Get the four corner coordinates of the RBRect
      x1, y1 = rect[0][0], rect[0][1]
      x2, y2 = rect[1][0]+x1, rect[1][1]+y1
      # Make sure x1<x2 and y1<y2
      if x2 <= x1:
         x1, x2 = x2, x1
      if y2 <= y1:
         y1, y2 = y2, y1
      for bo in self.rects:
         if x1 <= self.rects[bo].rect.BoundingBox.Center[0] <= x2 and \
            y1 <= self.rects[bo].rect.BoundingBox.Center[1] <= y2:
            self.selectedRects.append(bo.name)
            self.rects[bo].rect.PutInForeground() # clicked rect pops to top
            self.rects[bo].rect.Text.PutInForeground()
            self.rects[bo].rect.SetLineColor(NavigatorModel.colors['WHITE'])
            if self.rects[bo]._revShown:
               for revision in self.rects[bo]._revisionRects:
                  self.rects[bo]._revisionRects[revision].PutInForeground()
                  self.rects[bo]._revisionRects[revision].Text.PutInForeground()
                  self.rects[bo]._revisionRects[revision].SetLineColor(NavigatorModel.colors['WHITE'])
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
      for bo in self.rects: # Go through and redraw all the arrows as they move
         for revision in efbo.getAllRevisions(self.rects[bo].rect.Name, self.busObjDict):
            relationships = efbo.getFromRelationship(revision)
            for rel in relationships:
               if efrel.getTypeName(rel) == MDXUtils.REL_AD: continue
               toBo = efrel.getTo(rel)
               if self.rects[toBo]: # If the object is on the screen still
                  if not self.rects[bo]._revShown and not self.rects[toBo]._revShown: #both revs collapsed
                     self.drawArrows(self.rects[bo].rect, self.rects[toBo].rect)
                  elif self.rects[bo]._revShown and not self.rects[toBo]._revShown: # one collapsed
                     self.drawArrows(self.rects[bo]._revisionRects[revision], self.rects[toBo].rect)
                  elif not self.rects[bo]._revShown and self.rects[toBo]._revShown: # one collapsed
                     for revision in efbo.getAllRevisions(toBo, self.busObjDict):
                        self.drawArrows(self.rects[bo].rect, self.rects[toBo]._revisionRects[revision])
                  else: # both not collapsed
                     for rev in efbo.getAllRevisions(toBo, self.busObjDict):
                        self.drawArrows(self.rects[bo]._revisionRects[revision], self.rects[toBo]._revisionRects[rev])


