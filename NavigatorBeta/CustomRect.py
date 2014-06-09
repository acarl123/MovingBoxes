from wx.lib.floatcanvas import FloatCanvas
import wx

class NavRect:
   def __init__(self, canvas, text, xy, wh, LineWidth, Fillcolor):
      self.rect = canvas.AddRectangle(canvas.PixelToWorld(xy), wh, LineWidth=LineWidth, FillColor=Fillcolor)
      self.text = canvas.AddScaledText(text, canvas.PixelToWorld((xy[0] + 40, xy[1] - 17.5)), 7, Position="cc")
      self.rect.Text = self.text
