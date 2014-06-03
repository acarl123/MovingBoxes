from NavigatorView import NavigatorFrame
import NavigatorModel
import wx
from collections import deque
from wx.lib.floatcanvas import NavCanvas, FloatCanvas, Resources
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

      # Bind events to FloatCanvas
      self.canvas.Bind(FloatCanvas.EVT_LEFT_DOWN, self.onClick)
      self.canvas.Bind(FloatCanvas.EVT_LEFT_UP, self.onLUp)
      self.canvas.Bind(FloatCanvas.EVT_RIGHT_DOWN, self.onRClick)

      # Initialize member variables
      self.rects = {}
      self.selectedRects = []
      self.collidedRects = []
      self.mousePositions = deque([])
      self.mouseRel = 0, 0

      self.show()

      # @TODO: Remove this in the future, but for now populate the screen for prototyping
      self.populateScreen()
      self.canvas.AddRectangle((5, 5), (80, 35), LineWidth=2, FillColor=NavigatorModel.colors['BLUE'])

   #--------------------------------------------------------------------------------------#
   # Bindings
   #--------------------------------------------------------------------------------------#
   def onExit(self, event):
      self.mainWindow.Destroy()
      exit()

   # Handles all mouse events
   # def onMouse(self, event):
   #    # Calculate change in mouse position since last event using a queue system
   #    self.mousePositions.append((event.GetX(), event.GetY()))
   #    if len(self.mousePositions) == 2:
   #       self.mouseRel = ((self.mousePositions[1][0] - self.mousePositions[0][0]), (self.mousePositions[1][1] - self.mousePositions[0][1]))
   #       self.mousePositions.popleft()
   #
   #    if event.GetEventType() == FloatCanvas.EVT_LEFT_DOWN: self.onClick(event)
   #    if event.GetEventType() == FloatCanvas.EVT_RIGHT_DOWN: self.onRClick(event)
   #    if event.GetEventType() == FloatCanvas.EVT_LEFT_UP: self.onLUp(event)
   #    if event.GetEventType() == wx.wxEVT_MOUSEWHEEL: self.onScroll(event)
   #    if event.Dragging() == True: self.onDrag(event)

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

   def onScroll(self, event):
      scrollFactor = event.GetWheelRotation()
      if scrollFactor < 0:
         print 'scrolling out'
         scrollFactor = 0.5
      elif scrollFactor > 0:
         print 'scrolling in'
         scrollFactor = 2

      self.canvas.Zoom(scrollFactor, event.GetPositionTuple(), 'pixel')

   #--------------------------------------------------------------------------------------#
   # Initialize Methods
   #--------------------------------------------------------------------------------------#
   def show(self):
      self.mainWindow.Show()

   def populateScreen(self):
      # self.canvas.AddRectangle(self.canvas.PixelToWorld((20, 20)), (80, 35), lineWidth=2, FILLColor=wx.Colour('BLUE'))
      print 'foo'
