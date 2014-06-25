import os, sys, stat
sys.path.append('C:\\hg\\tools_lag\\EFSUtils')
from collections import deque
from ConfigFile import *
from DirectoryToken import *
from NavigatorFloatCanvas import NavGuiMove
from NavigatorModel import NavRect, RectDict
from NavigatorView import NavigatorFrame
from wx._controls import LIST_AUTOSIZE
from wx.lib.floatcanvas import FloatCanvas, GUIMode
import AddNodeDlg
import AttributeDlg
import BackgroundFunctionDlg
import cPickle as pickle
import ExpandChildrenController
import ExpandParentsController
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


def reloadSelf(path):
   frame = NavigatorController(path)
   frame.show()

class NavigatorController:
   def __init__(self, dbPath=None):
      # Setup view
      self.mainWindow = NavigatorFrame(None)
      self.makeLegend()

      # Initialize FloatCanvas defaults
      self.canvas = self.mainWindow.NavCanvas.Canvas
      self.canvas.InitializePanel()
      self.canvas.InitAll()

      # Setup model and efs
      self.rectModel = NavigatorModel.NavRect
      self.Config = ConfigFile('Config.txt')
      self.efs = ExportFileUtils.ExportFileSet()
      self.busObjDict = self.efs.newBusinessObjectDict(bodType=efbo.BOD_BOOLEAN_TYPE)

      # Bind normal canvas events
      self.canvas.Bind(wx.EVT_CONTEXT_MENU, self.onContextMenu)
      self.canvas.Bind(wx.EVT_KEY_DOWN, self.onKeyEvents) #TODO: fix it so these are actually binding
      self.canvas.Bind(wx.EVT_KEY_UP, self.onKeyEvents)
      self.canvas.Bind(wx.EVT_LEAVE_WINDOW, self.onLeaveWindow)
      self.canvas.Bind(wx.EVT_ENTER_WINDOW, self.onEnterWindow)
      self.canvas.Bind(wx.EVT_MIDDLE_DOWN, self.onMiddleDn)
      self.canvas.Bind(wx.EVT_MIDDLE_UP, self.onMiddleUp)

      # Bind normal window events
      self.mainWindow.Bind(wx.EVT_MENU, self.onAddObject, self.mainWindow.menuAddObject)
      self.mainWindow.Bind(wx.EVT_MENU, self.onExit, self.mainWindow.menuExit)
      self.mainWindow.Bind(wx.EVT_MENU, self.onExport, self.mainWindow.menuExport)
      self.mainWindow.Bind(wx.EVT_MENU, self.onHideLegend, self.mainWindow.hideLegendMenuItem)
      self.mainWindow.Bind(wx.EVT_MENU, self.onOpen, self.mainWindow.menuOpen)
      self.mainWindow.Bind(wx.EVT_MENU, self.onSave, self.mainWindow.menuSave)
      self.mainWindow.Bind(wx.EVT_MENU, self.onSaveAs, self.mainWindow.menuSaveAs)
      self.mainWindow.Bind(wx.EVT_MENU, self.onLoad, self.mainWindow.menuLoad)
      self.mainWindow.Bind(wx.EVT_MOUSEWHEEL, self.onScroll)
      self.mainWindow.Bind(wx.EVT_MENU, self.onShowLegend, self.mainWindow.showLegendMenuItem)

      # Initialize member variables
      self.allArrows = []
      self.arrowCount = 0
      self.ctrl_down = False
      self.enable()
      self.expandingRects = []
      self.mousePositions = deque([])
      self.mouseRel = 0, 0
      self.rects = RectDict()
      self.selectedRects = []
      self.saved = [False, None]

      # Initial bounding box member variables
      self.Drawing = False
      self.RBRect = None
      self.StartPointWorld = None
      self.Tol = 5 # tolerance for bounding box

      # Grouping member variables
      self.groupBox = None
      self.groups = {}
      self.groupNumber = 0

      if dbPath:
         self.loadNavFile(dbPath)

   #--------------------------------------------------------------------------------------#
   # Initialization (not bindings) TODO: Need a better name for this
   #--------------------------------------------------------------------------------------#
   def enable(self):
      # Bind events to FloatCanvas
      self.canvas.Bind(FloatCanvas.EVT_LEFT_DOWN, self.onClick)
      self.canvas.Bind(FloatCanvas.EVT_MOTION, self.onDrag)
      self.canvas.Bind(FloatCanvas.EVT_LEFT_UP, self.onLUp)

   def disable(self):
      # Unbind events to FloatCanvas
      self.canvas.Unbind(FloatCanvas.EVT_LEFT_DOWN)
      self.canvas.Unbind(FloatCanvas.EVT_MOTION)
      self.canvas.Unbind(FloatCanvas.EVT_LEFT_UP)

   def makeLegend(self):
      listCtrl = self.mainWindow.m_listCtrl1
      listCtrl.InsertColumn(0, 'Type', width=self.mainWindow.GetSize()[1]) # TODO: use list autowidth mixin
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

   def show(self):
      self.mainWindow.Show()

   def close(self):
      self.mainWindow.Destroy()

   #--------------------------------------------------------------------------------------#
   # Normal Canvas Bindings
   #--------------------------------------------------------------------------------------#
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
            self.popupID10 = wx.NewId()
            self.popupID15 = wx.NewId()
            self.popupID16 = wx.NewId()
            self.popupID17 = wx.NewId()
            self.canvas.Bind(wx.EVT_MENU, self.onExpandRevisions, id=self.popupID1)
            self.canvas.Bind(wx.EVT_MENU, self.onExpandRevisions, id=self.popupID15)
            self.canvas.Bind(wx.EVT_MENU, self.onCollapseRevisions, id=self.popupID16)
            self.canvas.Bind(wx.EVT_MENU, self.onAttributes, id=self.popupID2)
            self.canvas.Bind(wx.EVT_MENU, self.onDelete, id=self.popupID3)
            self.canvas.Bind(wx.EVT_MENU, self.onLock, id=self.popupID4)
            self.canvas.Bind(wx.EVT_MENU, self.onExpandOutgoing, id=self.popupID5)
            self.canvas.Bind(wx.EVT_MENU, self.onExpandIncoming, id=self.popupID10)
            self.canvas.Bind(wx.EVT_MENU, self.onExpandOutgoing, id=self.popupID17)
         menu = wx.Menu()
         submenu = wx.Menu()
         submenu.Append(self.popupID15, 'Expand Revisions')
         submenu.Append(self.popupID16, 'Collapse Revisions')
         menu.AppendMenu(self.popupID1, 'Revisions', submenu)
         menu.Append(self.popupID2, 'Attributes/Properties')
         menu.Append(self.popupID3, 'Delete Selected')
         menu.Append(self.popupID4, 'Lock')
         submenu = wx.Menu()
         submenu.Append(self.popupID5, 'Expand Children')
         submenu.Append(self.popupID10, 'Expand Where Used')
         menu.AppendMenu(self.popupID17, 'Expand', submenu)
         self.canvas.PopupMenu(menu)
         menu.Destroy()
         return

      if len(self.selectedRects) > 1:
         if not hasattr(self, 'popupID6'):
            self.popupID6 = wx.NewId()
            self.popupID14 = wx.NewId()
            self.popupID7 = wx.NewId()
            self.popupID8 = wx.NewId()
            self.popupID9 = wx.NewId()
            self.popupID11 = wx.NewId()
            self.popupID12 = wx.NewId()
            self.popupID13 = wx.NewId()
            self.canvas.Bind(wx.EVT_MENU, self.onArrangeHorizontally, id=self.popupID6)
            self.canvas.Bind(wx.EVT_MENU, self.onArrangeHorizontally, id=self.popupID14)
            self.canvas.Bind(wx.EVT_MENU, self.onArrangeVertically, id=self.popupID7)
            self.canvas.Bind(wx.EVT_MENU, self.onDelete, id=self.popupID8)
            self.canvas.Bind(wx.EVT_MENU, self.onLock, id=self.popupID9)
            self.canvas.Bind(wx.EVT_MENU, self.onGroup, id=self.popupID11)
            self.canvas.Bind(wx.EVT_MENU, self.onGroup, id=self.popupID12)
            self.canvas.Bind(wx.EVT_MENU, self.onUngroup, id=self.popupID13)
         submenu = wx.Menu()
         submenu.Append(self.popupID14, 'Arrange Horizontally')
         submenu.Append(self.popupID7, 'Arrange Vertically')
         menu = wx.Menu()
         menu.AppendMenu(self.popupID6, 'Arrange', submenu)
         submenu = wx.Menu()
         submenu.Append(self.popupID12, 'Group')
         submenu.Append(self.popupID13, 'Ungroup')
         menu.Append(self.popupID8, 'Delete Selected')
         menu.Append(self.popupID9, 'Lock')
         menu.AppendMenu(self.popupID11, 'Group', submenu)
         self.canvas.PopupMenu(menu)
         menu.Destroy()

   def onKeyEvents(self, event):
      self.ctrl_down = event.ControlDown()
      if event.GetKeyCode() == wx.WXK_DELETE:
         self.onDelete(event)
      if self.ctrl_down and event.GetKeyCode() == 71: # Ctrl + g
         self.onGroup(event)
      event.Skip()

   def onLeaveWindow(self, event):
      self.disable()
      # TODO: Look into capturing up and down and left up mouseevents off the canvas
      if self.Drawing:
         self.Drawing = False
         if self.RBRect:
            WH = self.canvas.PixelToWorld(event.GetPosition()) - self.StartPointWorld
            wx.CallAfter(self.drawBandBox, (self.StartPointWorld, WH))
         self.RBRect = None
         self.StartPointWorld = None
      self.draw()
      event.Skip()

   def onEnterWindow(self, event):
      self.enable()
      event.Skip()

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
      addNodeDlg = AddNodeDlg.AddNodeDlg(self.canvas, self.efs)
      self.clearSelectedRects()
      if (addNodeDlg.ShowModal () == wx.ID_OK):
         if (addNodeDlg.ReturnBOs != None):
            for bo in addNodeDlg.ReturnBOs:
               if bo in self.rects: continue # Check if this bo is already on the canvas
               xy = (random.randint(0, self.mainWindow.GetSize()[0]), random.randint(0, self.mainWindow.GetSize()[1])) #TODO: Come up with a good way to populate the screen
               self.boType = efbo.getTypeName(bo)
               if self.boType in TypeColors.ObjColorDict:
                  colorSet = TypeColors.ObjColorDict[self.boType]
                  rect = NavRect(bo, self.mainWindow.NavCanvas, '%s' % efbo.getName(bo), xy, 0, colorSet, 'WHITE')
               else:
                  rect = NavRect(bo, self.mainWindow.NavCanvas, '%s' % efbo.getName(bo), xy, 0, 'WHITE', 'WHITE')
               rect.rect.Bind(FloatCanvas.EVT_FC_LEFT_DOWN, lambda object, event=wx.MouseEvent(): self.onRectLeftClick(object, event)) # You can bind to the hit event of rectangle objects
               rect.rect.Bind(FloatCanvas.EVT_FC_LEFT_DCLICK, lambda object, event=wx.MouseEvent(): self.onRectLeftDClick(object, event))
               self.rects.append(rect)
               self.selectedRects.append(bo)
               rect.rect.PutInForeground()
               rect.rect.Text.PutInForeground()
            addNodeDlg.Destroy()
      self.draw()

   def onExit(self, event):
      self.mainWindow.Destroy()
      exit()

   def onExport(self, event):
      for bo in self.selectedRects:
         self.rects[bo].rect.PutInBackground()
         self.rects[bo].rect.Text.PutInBackground()
         if self.rects[bo]._revShown:
            for revision in self.rects[bo]._revisionRects:
               self.rects[bo]._revisionRects[revision].PutInBackground()
               self.rects[bo]._revisionRects[revision].Text.PutInBackground()
      self.canvas.Draw()
      dlg = wx.FileDialog(self.canvas, message="Save file as ...", defaultDir=os.getcwd(),
                          defaultFile="", wildcard="*.png", style=wx.SAVE)
      if dlg.ShowModal() == wx.ID_OK:
         path = dlg.GetPath()
         if not(path[-4:].lower() == ".png"):
            path = path+".png"
         self.canvas.SaveAsImage(path)

      for bo in self.selectedRects:
         self.rects[bo].rect.PutInForeground()
         self.rects[bo].rect.Text.PutInForeground()
         if self.rects[bo]._revShown:
            for revision in self.rects[bo]._revisionRects:
               self.rects[bo]._revisionRects[revision].PutInForeground()
               self.rects[bo]._revisionRects[revision].Text.PutInForeground()

   def onHideLegend(self, event):
      if self.mainWindow.m_splitter1.IsSplit():
         self.mainWindow.m_splitter1.Unsplit()

   def onOpen(self, event):
      dlg = wx.FileDialog(
            self.canvas, message="Opening an EFS...",
            defaultDir=os.getcwd(),
            defaultFile="",
            wildcard="EFS files (*txt)|*.txt",
            style=wx.OPEN | wx.CHANGE_DIR
            )
      if dlg.ShowModal() == wx.ID_OK:
         self.efsPath = dlg.GetPath()
         print "Opening:" + self.efsPath
         dlg = BackgroundFunctionDlg.BackgroundFunctionDlg(self.canvas, 'Opening EFS', self.OpenFile, self.efsPath )
         dlg.Go()
         _, efsFileName = os.path.split(self.efsPath)
         self.mainWindow.SetTitle('EFS Navigator - %s' % efsFileName)
      dlg.Destroy()

   def onSaveAs(self, event):
      dlg = wx.FileDialog(self.canvas,
                          message="Save the canvas as...",
                          defaultDir=os.getcwd(),
                          wildcard="Navigator files (*.nav)|*.nav",
                          style=wx.SAVE | wx.CHANGE_DIR | wx.FD_OVERWRITE_PROMPT
      )

      if dlg.ShowModal() == wx.ID_OK:
         self.saved[1] = dlg.GetPath()
         self.saved[0] = True
      else:
         return
      self.onSave(event)

   def onSave(self, event):
      if not 'efsPath' in self.__dict__.keys(): return # makes sure an EFS is loaded so you cannot save a blank canvas

      if not self.saved[0]:
         # Show save file dialog
         dlg = wx.FileDialog(self.canvas,
                                   message="Save the canvas as...",
                                   defaultDir=os.getcwd(),
                                   wildcard="Navigator files (*.nav)|*.nav",
                                   style=wx.SAVE | wx.CHANGE_DIR | wx.FD_OVERWRITE_PROMPT
         )
         if dlg.ShowModal() == wx.ID_OK:
            self.saved[1] = dlg.GetPath()
            self.saved[0] = True
         else: return


      # converts rect dict to a pickleable object
      obj = {}
      for rect in self.rects:
         if isinstance(rect, (int, long)):
            key = rect
         else:
            key = rect.name
         obj[key] = [
            (rect.rect.BoundingBox.Right,
             rect.rect.BoundingBox.Top,
             rect.rect.BoundingBox.Width,
             rect.rect.BoundingBox.Height
            ),
            [rect for rect in rect._revisionRects]
         ]

      # captures all of the pickleable class variables to restore same state
      data = {}
      for name, value in self.__dict__.iteritems():
         try:
            _ = pickle.dumps(value)
            data[name] = value
         except:
            pass

      # captures the few canvas variables needed
      # TODO: maybe capture _foredrawlist and _backgroundDirty
      canvasStates = {
         'scale' : self.canvas.Scale,
         'origin': self.mainWindow.NavCanvas.GetClientAreaOrigin()
      }

      pickleList = [self.efsPath, obj, data, canvasStates]

      try:
         fileAtt = os.stat(self.saved[1])[0]
         if (not fileAtt & stat.S_IWRITE):
            # File is read-only, so make it writeable
            os.chmod(self.saved[1], stat.S_IWRITE)

         pickle.dump(pickleList, open(self.saved[1], 'wb+'))
         dlg = wx.MessageDialog(self.mainWindow, 'Save to %s complete!' % self.saved[1], 'Save Successful', wx.ICON_INFORMATION|wx.OK, wx.DefaultPosition)
         dlg.ShowModal()

      except:
         e = sys.exc_info()[0]
         dlg = wx.MessageDialog(self.mainWindow, 'Save Failed at: \n%s' % e, 'Save Error', wx.ICON_ERROR|wx.OK, wx.DefaultPosition)
         dlg.ShowModal()

      finally:
         # make file Read-Only so user cannot accidentally mess it up
         os.chmod(self.saved[1], stat.S_IREAD)

   def onLoad(self, event):
      dlg = wx.FileDialog(
         self.canvas,
         message = "Save the canvas as...",
         defaultDir = os.getcwd(),
         wildcard = "Navigator files (*.nav)|*.nav",
         style = wx.OPEN | wx.CHANGE_DIR
      )

      if dlg.ShowModal() == wx.ID_OK:
         path = dlg.GetPath()
         self.close()
         del self.efs
         newFrame = NavigatorController(path)
         del self
      else:
         return

      # TODO: Clear existing canvas

   def loadNavFile(self, path):
      # Loads the EFS from the saved path
      vars = pickle.load(open(path, 'rb'))
      self.efsPath = vars[0]
      print "Opening:" + self.efsPath
      dlg = BackgroundFunctionDlg.BackgroundFunctionDlg(self.mainWindow, 'Opening EFS', self.OpenFile, self.efsPath)
      dlg.Go()
      _, efsFileName = os.path.split(self.efsPath)
      self.show()
      self.mainWindow.SetTitle('EFS Navigator - %s' % efsFileName)

      # Loads in class variables
      for name, value in self.__dict__.iteritems():
         if name in vars[2]:
            self.__dict__[name] = vars[2][name]

      # Loads all rectangles on the screen
      self.canvas.Scale = vars[3]['scale'] # must set scale first so coordinates are correct
      for key, value in vars[1].iteritems():
         if not key: continue
         xy = (value[0][0], -value[0][1])
         self.boType = efbo.getTypeName(key)
         if key in self.selectedRects: color = 'WHITE'
         else: color = 'BLACK'

         if self.boType in TypeColors.ObjColorDict:
            colorSet = TypeColors.ObjColorDict[self.boType]
            rect = NavRect(key, self.mainWindow.NavCanvas, '%s' % efbo.getName(key), xy, 0, colorSet, color)
         else:
            rect = NavRect(key, self.mainWindow.NavCanvas, '%s' % efbo.getName(key), xy, 0, 'WHITE', color)

         rect.rect.Bind(FloatCanvas.EVT_FC_LEFT_DOWN,
                        lambda object, event=wx.MouseEvent(): self.onRectLeftClick(object, event))  # You can bind to the hit event of rectangle objects
         rect.rect.Bind(FloatCanvas.EVT_FC_LEFT_DCLICK,
                        lambda object, event=wx.MouseEvent(): self.onRectLeftDClick(object, event))
         self.rects.append(rect)
         rect.rect.PutInForeground()
         rect.rect.Text.PutInForeground()

         # Load revisions if they were shown
         if value[1]:
            bo = key  # TODO: For group selection we need to go through the entire selected rects
            if not self.rects[bo]._revShown:
               self.rects[bo]._revShown = True
               xy = self.rects[bo].rect.BoundingBox.Right, self.rects[bo].rect.BoundingBox.Top
               for revision in efbo.getAllRevisions(bo, self.busObjDict):
                  self.boType = efbo.getTypeName(revision)
                  text = self.canvas.AddScaledText('%s' % efbo.getRevision(revision), xy,
                                                   Size=12, Family=wx.ROMAN, Weight=wx.BOLD)
                  wh = text.BoundingBox.Width, text.BoundingBox.Height
                  if self.boType in TypeColors.ObjColorDict:
                     colorSet = TypeColors.ObjColorDict[self.boType]
                     # TODO: eventually revs need to be selectable
                     rect = self.canvas.AddRectangle((xy[0], xy[1] - wh[1]), wh, LineWidth=0, FillColor=colorSet,
                                                     LineColor=color)
                  else:
                     rect = self.canvas.AddRectangle((xy[0], xy[1] - wh[1]), wh, LineWidth=0, FillColor='WHITE',
                                                     LineColor=color)
                  rect.Name = '%s' % efbo.getRevision(revision)
                  rect.Text = text
                  # TODO: Put in bindings maybe to the revision rects
                  rect.PutInForeground()
                  rect.Text.PutInForeground()
                  self.rects[bo]._revisionRects[int(revision)] = rect  # append the dict with bo: rect
                  xy = xy[0] + wh[0], xy[1]

      # Loads saved canvas scale and origin
      # self.canvas.Zoom(vars[3]['scale'], vars[3]['origin'], 'pixel')
      self.mainWindow.NavCanvas.ZoomToFit(None)

      self.draw()

   def onScroll(self, event):
      scrollFactor = event.GetWheelRotation()
      if scrollFactor < 0:
         scrollFactor = 0.5
      elif scrollFactor > 0:
         scrollFactor = 2
      self.mainWindow.NavCanvas.scale /= scrollFactor
      self.canvas.Zoom(scrollFactor, event.GetPositionTuple(), 'pixel')

   def onShowLegend(self, event):
      if not self.mainWindow.m_splitter1.IsSplit():
         leftWindow = self.mainWindow.NavCanvas
         rightWindow = self.mainWindow.m_panel2
         self.mainWindow.m_splitter1.SplitVertically(leftWindow, rightWindow, 900)

   #--------------------------------------------------------------------------------------#
   # FloatCanvas Bindings
   #--------------------------------------------------------------------------------------#
   def onClick(self, event):
      if self.groupBox and self.inGroupBox(event):
         self.onDrag(event)
         return

      # Start drawing band box
      self.Drawing = True
      self.StartPoint = event.GetPosition()
      self.StartPointWorld = event.Coords

      if not self.ctrl_down:
         self.clearSelectedRects()

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

      # self.canvas._BackgroundDirty = True #TODO: Remove this and learn how to handle foreground correctly
      self.mousePositions.append(event.GetPositionTuple())
      if len(self.mousePositions) == 2:
         self.mouseRel = ((self.mousePositions[1][0] - self.mousePositions[0][0])*self.mainWindow.NavCanvas.scale,
                          -(self.mousePositions[1][1] - self.mousePositions[0][1])*self.mainWindow.NavCanvas.scale)
         self.mousePositions.popleft()

      # Move all the selected rects
      if event.Dragging() and not self.ctrl_down:
         if self.selectedRects:
            for bo in self.selectedRects:
               self.rects[bo].rect.PutInForeground()
               self.rects[bo].rect.Text.PutInForeground()
               self.moveRect(self.rects[bo].rect, self.mouseRel)
               for revision in self.rects[bo]._revisionRects:
                  self.moveRect(self.rects[bo]._revisionRects[revision], self.mouseRel)
            self.draw()
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
      self.draw()

   #--------------------------------------------------------------------------------------#
   # ContextMenu with Single Object Selected Bindings
   #--------------------------------------------------------------------------------------#
   def onAttributes(self, event):
      bo = self.selectedRects[0]
      dlg = AttributeDlg.AttributeDlg(self.canvas, self.rects[bo].rect.Name)
      dlg.Show()
      if dlg.ShowModal () == wx.ID_OK:
         dlg.Destroy()

   def onCollapseRevisions(self, event):
      bo = self.selectedRects[0] # TODO: For group selection we need to go through the entire selected rects
      if self.rects[bo]._revShown:
         self.rects[bo]._revShown = False
         for revision in self.rects[bo]._revisionRects:
            self.canvas.RemoveObjects([self.rects[bo]._revisionRects[revision], self.rects[bo]._revisionRects[revision].Text])
         self.rects[bo]._revisionRects = {}
      self.draw()

   def onExpandRevisions(self, event):
      bo = self.selectedRects[0] # TODO: For group selection we need to go through the entire selected rects
      if not self.rects[bo]._revShown:
         self.rects[bo]._revShown = True
         xy = self.rects[bo].rect.BoundingBox.Right, self.rects[bo].rect.BoundingBox.Top
         for revision in efbo.getAllRevisions(bo, self.busObjDict):
            self.boType = efbo.getTypeName(revision)
            text = self.canvas.AddScaledText('%s' % efbo.getRevision(revision), xy,
                                             Size=12, Family=wx.ROMAN, Weight=wx.BOLD)
            wh = text.BoundingBox.Width, text.BoundingBox.Height
            if self.boType in TypeColors.ObjColorDict:
               colorSet = TypeColors.ObjColorDict[self.boType]
               #TODO: eventually revs need to be selectable
               rect = self.canvas.AddRectangle((xy[0], xy[1]-wh[1]), wh, LineWidth=0, FillColor=colorSet, LineColor='WHITE')
            else:
               rect = self.canvas.AddRectangle((xy[0], xy[1]-wh[1]), wh, LineWidth=0, FillColor='WHITE', LineColor='WHITE')
            rect.Name = '%s' % efbo.getRevision(revision)
            rect.Text = text
            # TODO: Put in bindings maybe to the revision rects
            rect.PutInForeground()
            rect.Text.PutInForeground()
            self.rects[bo]._revisionRects[int(revision)] = rect #append the dict with bo: rect
            xy = xy[0] + wh[0], xy[1]
      self.draw()

   def onExpandOutgoing(self, event):
      bo = self.selectedRects[0]
      self.clearSelectedRects()
      xy = self.rects[bo].rect.BoundingBox.Right + self.rects[bo].rect.BoundingBox.Width, \
           self.rects[bo].rect.BoundingBox.Top
      xy = self.canvas.WorldToPixel(xy)
      expandDlg = ExpandChildrenController.ExpandChildrenController(self.canvas, bo, self.busObjDict)
      expandDlg.show()
      if expandDlg.expandDlg.ShowModal() == wx.ID_OK:
         if (expandDlg.returnBOs != None):
            for toBo in expandDlg.returnBOs:
               if not toBo in self.rects:
                  self.boType = efbo.getTypeName(toBo)
                  if self.boType in TypeColors.ObjColorDict: colorSet = TypeColors.ObjColorDict[self.boType]
                  else: colorSet = 'WHITE'
                  rect = NavRect(toBo, self.mainWindow.NavCanvas, '%s' % efbo.getName(toBo), xy, 0, colorSet, 'WHITE')
                  rect.rect.Bind(FloatCanvas.EVT_FC_LEFT_DOWN, lambda object, event=wx.MouseEvent(): self.onRectLeftClick(object, event))
                  rect.rect.Bind(FloatCanvas.EVT_FC_LEFT_DCLICK, lambda object, event=wx.MouseEvent(): self.onRectLeftDClick(object, event))
                  rect.rect.PutInForeground()
                  rect.rect.Text.PutInForeground()
                  self.selectedRects.append(toBo)
                  self.rects.append(rect)
      self.onArrangeVertically(event)

   def onExpandIncoming(self, event):
      bo = self.selectedRects[0]
      self.clearSelectedRects()
      xy = (100, 200) #TODO: Don't just hardcode in a position
      expandDlg = ExpandParentsController.ExpandParentsController(self.canvas, bo, self.busObjDict)
      expandDlg.show()
      if expandDlg.expandParentDlg.ShowModal() == wx.ID_OK:
         if (expandDlg.returnBOs != None):
            for fromBo in expandDlg.returnBOs:
               if not fromBo in self.rects:
                  self.boType = efbo.getTypeName(fromBo)
                  if self.boType in TypeColors.ObjColorDict: colorSet = TypeColors.ObjColorDict[self.boType]
                  else: colorSet = 'WHITE'
                  rect = NavRect(fromBo, self.mainWindow.NavCanvas, '%s' % efbo.getName(fromBo), xy, 0, colorSet, 'WHITE')
                  rect.rect.Bind(FloatCanvas.EVT_FC_LEFT_DOWN, lambda object, event=wx.MouseEvent(): self.onRectLeftClick(object, event))
                  rect.rect.Bind(FloatCanvas.EVT_FC_LEFT_DCLICK, lambda object, event=wx.MouseEvent(): self.onRectLeftDClick(object, event))
                  rect.rect.PutInForeground()
                  rect.rect.Text.PutInForeground()
                  self.selectedRects.append(fromBo)
                  self.rects.append(rect)
      self.onArrangeVertically(event)
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
      self.selectedRects = []
      if self.groupBox:
         self.groupBox.UnBindAll()
         self.canvas.RemoveObject(self.groupBox)
         self.groupBox = None
      self.draw()

   def onGroup(self, event):
      print 'Grouping objects together'

   def onLock(self, event):
      print 'On Lock'

   def onUngroup(self, event):
      print 'Ungroup objects'

   #--------------------------------------------------------------------------------------#
   # FloatCanvas Rect Bindings
   #--------------------------------------------------------------------------------------#
   def onRectLeftClick(self, object, event):
      if self.ctrl_down:
         if str(object.Name) not in self.selectedRects:
            self.selectedRects.append(object.Name)
      else:
         if object.Name not in self.selectedRects:
            self.clearSelectedRects()
            self.selectedRects.append(object.Name)
      object.SetLineColor(NavigatorModel.colors['WHITE'])
      object.PutInForeground() # clicked rect pops to top
      object.Text.PutInForeground()
      if self.rects[object.Name]._revShown:
         for revision in self.rects[object.Name]._revisionRects:
            self.rects[object.Name]._revisionRects[revision].SetLineColor(NavigatorModel.colors['WHITE'])
            self.rects[object.Name]._revisionRects[revision].PutInForeground()
            self.rects[object.Name]._revisionRects[revision].Text.PutInForeground()
      self.canvas.Draw()

   def onRectLeftDClick(self, object, event):
      self.clearSelectedRects()
      self.selectedRects.append(object.Name)
      self.rects[object.Name].rect.SetLineColor('WHITE')
      self.rects[object.Name].rect.PutInForeground()
      self.rects[object.Name].rect.Text.PutInForeground()
      if self.rects[object.Name]._revShown: self.onCollapseRevisions(event)
      else: self.onExpandRevisions(event)

   #--------------------------------------------------------------------------------------#
   # Drawing Methods
   #--------------------------------------------------------------------------------------#
   def draw(self):
      self.redrawArrows()
      self.drawGroupBox()
      self.canvas.Draw()

   def drawArrowsBetweenRevs(self, rev1, rev2):
      if rev1.BoundingBox.Height <= rev2.BoundingBox.Height:minHeight = rev1.BoundingBox.Height
      else: minHeight = rev2.BoundingBox.Height
      absoluteHeight = abs(rev1.BoundingBox.Center[1]-rev2.BoundingBox.Center[1])

      if rev1.BoundingBox.Center[1] >= rev2.BoundingBox.Center[1]:
         if absoluteHeight >= minHeight:xy1 = rev1.BoundingBox.Center[0], rev1.BoundingBox.Bottom
         else:xy1 = rev1.BoundingBox.Center[0], rev1.BoundingBox.Top
         xy2 = rev2.BoundingBox.Center[0], rev2.BoundingBox.Top
      else:
         if absoluteHeight >= minHeight:xy2 = rev2.BoundingBox.Center[0], rev2.BoundingBox.Bottom
         else:xy2 = rev2.BoundingBox.Center[0], rev2.BoundingBox.Top
         xy1 = rev1.BoundingBox.Center[0], rev1.BoundingBox.Top
      self.arrowCount += 1
      arrow = self.canvas.AddArrowLine((xy1, xy2), LineWidth=1, LineColor='BLACK', ArrowHeadSize=10, InForeground=False)
      self.allArrows.append(arrow)

   # @TODO: Optimize this code a lot
   def drawArrows(self, rect1, rect2, revInt):
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
      if revInt == 1: # First rect is a revision
         if rect1.BoundingBox.Center[1] >= rect2.BoundingBox.Center[1]:
            if absoluteHeight >= minHeight:xy1 = rect1.BoundingBox.Center[0], rect1.BoundingBox.Bottom
            else:xy1 = rect1.BoundingBox.Center[0], rect1.BoundingBox.Top
         else:
            xy1 = rect1.BoundingBox.Center[0], rect1.BoundingBox.Top
      if revInt == 2: # Second rect is a revision
         if rect1.BoundingBox.Center[1] >= rect2.BoundingBox.Center[1]:
            xy2 = rect2.BoundingBox.Center[0], rect2.BoundingBox.Top
         else:
            if absoluteHeight >= minHeight:xy2 = rect2.BoundingBox.Center[0], rect2.BoundingBox.Bottom
            else:xy2 = rect2.BoundingBox.Center[0], rect2.BoundingBox.Top
      self.arrowCount += 1
      arrow = self.canvas.AddArrowLine((xy1, xy2), LineWidth=1, LineColor='BLACK', ArrowHeadSize=10, InForeground=False)
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
      self.draw()

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
            if not ((revision in self.rects[bo]._revisionRects) or (revision == self.rects[bo].rect.Name)):continue
            relationships = efbo.getFromRelationship(revision)
            for rel in relationships:
               if efrel.getTypeName(rel) == MDXUtils.REL_AD: continue
               toBo = efrel.getTo(rel)
               if toBo in self.rects: # If the object is on the screen
                  if not self.rects[bo]._revShown and not self.rects[toBo]._revShown: #both revs collapsed
                     self.drawArrows(self.rects[bo].rect, self.rects[toBo].rect, 0)
                  elif self.rects[bo]._revShown and not self.rects[toBo]._revShown: # one collapsed
                     self.drawArrows(self.rects[bo]._revisionRects[revision], self.rects[toBo].rect, 1)
                  elif not self.rects[bo]._revShown and self.rects[toBo]._revShown: # one collapsed
                     for revision in efbo.getAllRevisions(toBo, self.busObjDict):
                        self.drawArrows(self.rects[bo].rect, self.rects[toBo]._revisionRects[revision], 2)
                  else: # both not collapsed
                     for rev in efbo.getAllRevisions(toBo, self.busObjDict):
                        self.drawArrowsBetweenRevs(self.rects[bo]._revisionRects[revision], self.rects[toBo]._revisionRects[rev])

   def clearSelectedRects(self):
      if not self.selectedRects: return
      for bo in self.selectedRects:
         self.rects[bo].rect.SetLineColor(NavigatorModel.colors['BLACK'])
         if self.rects[bo]._revShown:
            for revision in self.rects[bo]._revisionRects:
               self.rects[bo]._revisionRects[revision].SetLineColor(NavigatorModel.colors['BLACK'])
      self.canvas.Draw()
      for bo in self.selectedRects:
         self.rects[bo].rect.PutInBackground()
         self.rects[bo].rect.Text.PutInBackground()
         if self.rects[bo]._revShown:
            for revision in self.rects[bo]._revisionRects:
               self.rects[bo]._revisionRects[revision].PutInBackground()
               self.rects[bo]._revisionRects[revision].Text.PutInBackground()
      self.selectedRects = []
      if self.groupBox:
         self.groupBox.UnBindAll()
         self.canvas.RemoveObject(self.groupBox)
         self.groupBox = None

   def drawGroupBox(self):
      if not self.selectedRects or len(self.selectedRects)==1: return
      left = bottom = sys.maxint
      right = top = -sys.maxint - 1
      for bo in self.selectedRects:
         left = min(left, self.rects[bo].rect.BoundingBox.Left)
         right = max(right, self.rects[bo].rect.BoundingBox.Right)
         top = max(top, self.rects[bo].rect.BoundingBox.Top)
         bottom = min(bottom, self.rects[bo].rect.BoundingBox.Bottom)
         if self.rects[bo]._revShown:
            for rev in self.rects[bo]._revisionRects:
               right = max(right, self.rects[bo]._revisionRects[rev].BoundingBox.Right)
      xy = left-5, bottom-5
      wh = right-left+10, top-bottom+10
      if self.groupBox:
         self.groupBox.UnBindAll()
         self.canvas.RemoveObject(self.groupBox)
         self.groupBox = self.canvas.AddRectangle((xy), wh, LineWidth=2, LineColor='WHITE', InForeground=False)
      else: self.groupBox = self.canvas.AddRectangle((xy), wh, LineWidth=2, LineColor='WHITE', InForeground=False)

   def inGroupBox(self, event):
      if not self.groupBox: return
      xy = self.groupBox.BoundingBox.Left, self.groupBox.BoundingBox.Top
      left, top = self.canvas.WorldToPixel((xy))
      right = left + self.groupBox.BoundingBox.Width
      bottom = top + self.groupBox.BoundingBox.Height
      if left <= event.GetPosition()[0] <= right and \
         top <= event.GetPosition()[1] <= bottom:
         return True
      return False

