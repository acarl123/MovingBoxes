from NavigatorView import NavigatorFrame
import NavigatorModel
import wx
from collections import deque
from wx.lib.floatcanvas import NavCanvas, FloatCanvas, Resources


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

      # Bind events to FloatCanvas
      self.canvas.Bind(wx.EVT_MOUSE_EVENTS, self.onMouse) # Add all mouse events to a single bind

      # Initialize member variables
      self.rects = {}
      self.selectedRects = []
      self.collidedRects = []
      self.mousePositions = deque([])
      self.mouseRel = 0, 0

      self.show()

      # @TODO: Remove this in the future, but for now populate the screen for prototyping
      self.populateScreen()

   #--------------------------------------------------------------------------------------#
   # Bindings
   #--------------------------------------------------------------------------------------#
   def onExit(self, event):
      self.mainWindow.Destroy()
      exit()

   # Handles all mouse events
   def onMouse(self, event):
      # Calculate change in mouse position since last event using a queue system
      print event.GetEventType()
      self.mousePositions.append((event.GetX(), event.GetY()))
      if len(self.mousePositions) == 2:
         self.mouseRel = ((self.mousePositions[1][0] - self.mousePositions[0][0]), (self.mousePositions[1][1] - self.mousePositions[0][1]))
         self.mousePositions.popleft()

      if event.GetEventType() == FloatCanvas.EVT_LEFT_DOWN: self.onClick(event)
      if event.GetEventType() == FloatCanvas.EVT_RIGHT_DOWN: self.onRClick(event)
      if event.GetEventType() == FloatCanvas.EVT_LEFT_UP: self.onLUp(event)
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

   #--------------------------------------------------------------------------------------#
   # Initialize Methods
   #--------------------------------------------------------------------------------------#
   def show(self):
      self.mainWindow.Show()

   def populateScreen(self):
      # self.canvas.AddRectangle(self.canvas.PixelToWorld((20, 20)), (80, 35), lineWidth=2, FILLColor=wx.Colour('BLUE'))
      print 'foo'
