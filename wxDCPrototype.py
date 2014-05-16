__author__ = 'mwj'
import wx
import random
import time

app = wx.App(False)

frame = wx.Frame(None, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 1024,768 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
bSizer1 = wx.BoxSizer(wx.VERTICAL)
panel = wx.Panel(frame)
panel.SetBackgroundColour(wx.GREEN)
bSizer1.Add(panel, 1, wx.EXPAND | wx.ALL, 5)

frame.SetSizer(bSizer1)
frame.Layout()
frame.Centre(wx.BOTH)

randnum = random
randnum.seed()

N_BIG_RECTS = 500
N_SMALL_RECTS = 5*N_BIG_RECTS

statbmp = wx.StaticBitmap(panel)

draw_bmp = wx.EmptyBitmap(1024,768)
canvas_dc = wx.MemoryDC(draw_bmp)
canvas_dc.SetBackground(wx.Brush('blue'))
canvas_dc.Clear()

start_time = time.time()
for i in range(N_BIG_RECTS):
   x=10*randnum.randint(0,90)
   y=10*randnum.randint(0,90)
   rect = wx.Rect(x,y,85,35)
   canvas_dc.DrawRoundedRectangleRect(rect, 8)
   canvas_dc.SetFont(wx.SMALL_FONT)
   canvas_dc.DrawText('BigRectangle', x, y)

for i in range(N_SMALL_RECTS):
   x=10*randnum.randint(0,90)
   y=10*randnum.randint(0,90)
   rect = wx.Rect(x,y,35,35)
   canvas_dc.DrawRoundedRectangleRect(rect, 8)
   canvas_dc.DrawText('a', x, y)

canvas_dc.SelectObject(wx.NullBitmap)

statbmp.SetBitmap(draw_bmp)

frame.Show()
print time.time() - start_time, " seconds"



app.MainLoop()





