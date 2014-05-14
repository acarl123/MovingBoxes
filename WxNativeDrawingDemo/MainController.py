import pygame
from MainView import MainFrame
import wx
import pygame.rect as rectOps
from collections import deque

BLACK = 0, 0, 0
BLUE = 100, 223, 237
GREY = 173,173,173
RED = 255, 0, 0
WHITE = 255, 255, 255


class MainController:
   def __init__(self):
      self.mainWindow = MainFrame(None)
      self.drawingPanel = self.mainWindow.drawingPanel
      self.drawingPanel.SetBackgroundColour(GREY)
      self.mouserel = 0, 0
      self.mousePositions = deque([])
      self.rects = {}

      self.drawingPanel.Bind(wx.EVT_PAINT, self.OnPaint)
      self.drawingPanel.Bind(wx.EVT_MOUSE_EVENTS, self.onMouse) # adding all the mouse events to a single bind for ease of use and easy to change later

      self.mainWindow.Bind(wx.EVT_CLOSE, self.close)
      self.mainWindow.Bind(wx.EVT_SIZE, self.onSize)

   def show(self):
      self.mainWindow.Show()

   def close(self, event):
      self.drawingPanel.Destroy()
      exit()

   def onMouse(self, event):
      # Calculate change in mouse position since last event using a queue system
      self.mousePositions.append((event.GetX(), event.GetY()))
      if len(self.mousePositions) == 2:
         self.mouserel = ((self.mousePositions[1][0] - self.mousePositions[0][0]), (self.mousePositions[1][1] - self.mousePositions[0][1]))
         self.mousePositions.popleft()

      if event.GetEventType() == wx.wxEVT_LEFT_DOWN: self.onClick(event)
      if event.GetEventType() == wx.wxEVT_RIGHT_DOWN: self.onRClick(event)
      if event.GetEventType() == wx.wxEVT_LEFT_UP: self.onLUp(event)
      if event.Dragging() == True: self.onDrag(event)

   def onRClick(self, event):
      if not hasattr(self, 'popupID1'):
         self.popupID1 = wx.NewId()

      self.drawingPanel.Bind(wx.EVT_MENU, self.onMenuItem1, id=self.popupID1)

      menu = wx.Menu()
      menu.Append(self.popupID1, 'Close Menu')
      self.drawingPanel.PopupMenu(menu)
      menu.Destroy()

   def onMenuItem1(self, event):
      pass

   def onClick(self, event):

      for rect in self.rects.itervalues():
         if rect.collidepoint((event.GetX(), event.GetY())):
            return

      rect = wx.Rect(0, 0, 80, 35)
      id = wx.NewId()

      blueColour = wx.Colour(BLACK[0], BLACK[1], BLACK[2], wx.ALPHA_OPAQUE)
      blueBrush = wx.Colour(BLUE[0], BLUE[1], BLUE[2], 200)  # last arg is for transparency

      rect.SetPosition((event.GetX(), event.GetY()))
      # self.dc.SetId(id)
      self.rects[len(self.rects)] = pygame.rect.Rect(rect)

      self.dc.SetPen(wx.Pen(blueColour))
      self.dc.SetBrush(wx.Brush(blueBrush))
      self.dc.DrawRoundedRectangleRect(rect, 8)

   def onDrag(self, event):
      self.onClick(event)

   def onLUp(self, event):
      pass

   def onSize(self, event):
      event.Skip()

   def OnPaint(self, event=None):
      if not 'pdc' in locals(): pdc = wx.PaintDC(self.drawingPanel)
      try:
         self.dc = wx.GCDC(pdc)
      except:
         self.dc = pdc
