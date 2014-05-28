from MainView import MainFrame
import wx
import random
import time

#----------------------------------------------------------------------
class DragShape:
    def __init__(self, bmp):
        self.bmp = bmp
        self.pos = (0,0)
        self.shown = True
        self.text = None
        self.fullscreen = False

    def HitTest(self, pt):
        rect = self.GetRect()
        return rect.InsideXY(pt.x, pt.y)

    def GetRect(self):
        return wx.Rect(self.pos[0], self.pos[1],
                      self.bmp.GetWidth(), self.bmp.GetHeight())

    def Draw(self, dc, op = wx.COPY):
        if self.bmp.Ok():
            memDC = wx.MemoryDC()
            memDC.SelectObject(self.bmp)

            dc.Blit(self.pos[0], self.pos[1],
                    self.bmp.GetWidth(), self.bmp.GetHeight(),
                    memDC, 0, 0, op, True)
            return True
        else:
            return False

#----------------------------------------------------------------------

class MainController:
   def __init__(self):

      # Initialize all lists
      self.shapes = []

      self.N_RECTS = 10

      randnum = random
      randnum.seed()

      # Setup the view
      self.mainWindow = MainFrame(None)
      self.dragCanvas = self.mainWindow.dragCanvas
      self.dragCanvas.SetBackgroundColour(wx.GREEN)

      self.dragCanvas.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
      self.dragCanvas.bg_bmp = wx.EmptyBitmap(1024,768)
      # self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
      self.dragCanvas.SetScrollbars(1, 1, 2000, 2000, 0, 0)
      self.dragImage = None
      self.dragShape = None
      self.hiliteShape = None


      startTime = time.time()
      frameRate = 0
      while frameRate < 1:
         frameRate+= 1
         for i in range(self.N_RECTS):
            # Make a shape from some text
            text = "Hello There"
            bg_colour = wx.Colour(57, 115, 57)  # matches the bg image
            font = wx.Font(8, wx.ROMAN, wx.NORMAL, wx.BOLD)
            textExtent = self.dragCanvas.GetFullTextExtent(text, font)

            x=10*randnum.randint(0,90)
            y=10*randnum.randint(0,90)
            rect = wx.Rect(0,0,85,35)

            # create a bitmap the same size as our text
            bmp = wx.EmptyBitmap(textExtent[0], textExtent[1])
            bmp = wx.EmptyBitmap(85, 35)

            # 'draw' the text onto the bitmap
            dc = wx.MemoryDC()
            dc.SelectObject(bmp)
            dc.SetBackground(wx.Brush(bg_colour, wx.SOLID))
            dc.Clear()
            dc.SetTextForeground(wx.RED)
            dc.SetFont(font)

            dc.DrawRoundedRectangleRect(rect, 8)
            dc.DrawText(text, 0, 0)
            dc.SelectObject(wx.NullBitmap)
            mask = wx.Mask(bmp, bg_colour)
            bmp.SetMask(mask)
            shape = DragShape(bmp)
            shape.pos = (x, y)
            self.shapes.append(shape)

      print time.time()-startTime

      self.dragCanvas.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
      self.dragCanvas.Bind(wx.EVT_PAINT, self.OnPaint)
      self.dragCanvas.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
      self.dragCanvas.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
      self.dragCanvas.Bind(wx.EVT_MOTION, self.OnMotion)

      self.dragCanvas.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
      self.dragCanvas.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)

   def show(self):
      self.mainWindow.Show()

   # tile the background bitmap
   def TileBackground(self, dc):
      sz = self.dragCanvas.GetClientSize()
      w = self.dragCanvas.bg_bmp.GetWidth()
      h = self.dragCanvas.bg_bmp.GetHeight()
      x = 0
      while x < sz.width:
         y = 0
         while y < sz.height:
            dc.DrawBitmap(self.dragCanvas.bg_bmp, x, y)
            y = y + h
         x = x + w

    # Go through our list of shapes and draw them in whatever place they are.
   def DrawShapes(self, dc):
      for shape in self.shapes:
         if shape.shown:
            shape.Draw(dc)

    # This is actually a sophisticated 'hit test', but in this
    # case we're also determining which shape, if any, was 'hit'.
   def FindShape(self, pt):
      for shape in self.shapes:
         if shape.HitTest(pt):
            return shape
      return None


   # Clears the background, then redraws it. If the DC is passed, then
   # we only do so in the area so designated. Otherwise, it's the whole thing.
   def OnEraseBackground(self, evt):
      dc = evt.GetDC()
      if not dc:
         dc = wx.ClientDC(self)
         rect = self.GetUpdateRegion().GetBox()
         dc.SetClippingRect(rect)
      self.TileBackground(dc)

   # Fired whenever a paint event occurs
   def OnPaint(self, evt):
      dc = wx.PaintDC(self.dragCanvas)
      self.dragCanvas.PrepareDC(dc)
      self.DrawShapes(dc)

   # Left mouse button is down.
   def OnLeftDown(self, evt):
      # Did the mouse go down on one of our shapes?
      shape = self.FindShape(evt.GetPosition())

      # If a shape was 'hit', then set that as the shape we're going to
      # drag around. Get our start position. Dragging has not yet started.
      # That will happen once the mouse moves, OR the mouse is released.
      if shape:
         self.dragShape = shape
         self.dragStartPos = evt.GetPosition()

   # Left mouse button up.
   def OnLeftUp(self, evt):
      if not self.dragImage or not self.dragShape:
         self.dragImage = None
         self.dragShape = None
         return

      # Hide the image, end dragging, and nuke out the drag image.
      self.dragImage.Hide()
      self.dragImage.EndDrag()
      self.dragImage = None

      if self.hiliteShape:
         self.dragCanvas.RefreshRect(self.hiliteShape.GetRect())
         self.hiliteShape = None

      self.dragShape.pos = (
         self.dragShape.pos[0] + evt.GetPosition()[0] - self.dragStartPos[0],
         self.dragShape.pos[1] + evt.GetPosition()[1] - self.dragStartPos[1]
         )

      self.dragShape.shown = True
      self.dragCanvas.RefreshRect(self.dragShape.GetRect())
      self.dragShape = None

   def OnRightDown(self, event):
      self.dragCanvas.scroller.Start(event.GetPosition())

   def OnRightUp(self, event):
      self.dragCanvas.scroller.Stop()

   # The mouse is moving
   def OnMotion(self, evt):
      # Ignore mouse movement if we're not dragging.
      if not self.dragShape or not evt.Dragging() or not evt.LeftIsDown():
         return

      # if we have a shape, but haven't started dragging yet
      if self.dragShape and not self.dragImage:

         # only start the drag after having moved a couple pixels
         tolerance = 2
         pt = evt.GetPosition()
         dx = abs(pt.x - self.dragStartPos.x)
         dy = abs(pt.y - self.dragStartPos.y)
         if dx <= tolerance and dy <= tolerance:
            return

         # refresh the area of the window where the shape was so it
         # will get erased.
         self.dragShape.shown = False
         self.dragCanvas.RefreshRect(self.dragShape.GetRect(), True)
         self.dragCanvas.Update()

         if self.dragShape.text:
            self.dragImage = wx.DragString(self.dragShape.text,
                                        wx.StockCursor(wx.CURSOR_HAND))
         else:
            self.dragImage = wx.DragImage(self.dragShape.bmp,
                                       wx.StockCursor(wx.CURSOR_HAND))

         hotspot = self.dragStartPos - self.dragShape.pos
         self.dragImage.BeginDrag(hotspot, self.dragCanvas, self.dragShape.fullscreen)

         self.dragImage.Move(pt)
         self.dragImage.Show()

      # if we have shape and image then move it, possibly highlighting another shape.
      elif self.dragShape and self.dragImage:
         onShape = self.FindShape(evt.GetPosition())
         unhiliteOld = False
         hiliteNew = False

         # figure out what to hilite and what to unhilite
         if self.hiliteShape:
            if onShape is None or self.hiliteShape is not onShape:
               unhiliteOld = True

         if onShape and onShape is not self.hiliteShape and onShape.shown:
            hiliteNew = True

         # if needed, hide the drag image so we can update the window
         if unhiliteOld or hiliteNew:
            self.dragImage.Hide()

         if unhiliteOld:
            dc = wx.ClientDC(self.dragCanvas)
            self.hiliteShape.Draw(dc)
            self.hiliteShape = None

         if hiliteNew:
            dc = wx.ClientDC(self.dragCanvas)
            self.hiliteShape = onShape
            self.hiliteShape.Draw(dc, wx.INVERT)

         # now move it and show it again if needed
         self.dragImage.Move(evt.GetPosition())
         if unhiliteOld or hiliteNew:
            self.dragImage.Show()
