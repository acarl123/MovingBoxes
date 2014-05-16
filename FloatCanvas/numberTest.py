import wx, random, time
from wx.lib.floatcanvas import NavCanvas

app = wx.App(False)
N_RECTANGLES = 500
blue = 100, 223, 237
start = time.time()

frame = wx.Frame(None, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 1024,768 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
bSizer1 = wx.BoxSizer(wx.VERTICAL)
NC = NavCanvas.NavCanvas(frame,
                         Debug=0,
                         BackgroundColor=(173, 173, 173))
Canvas = NC.Canvas
bSizer1.Add(NC, 1, wx.EXPAND | wx.ALL, 5)
frame.SetSizer(bSizer1)
frame.Layout()
frame.Centre(wx.BOTH)

for i in range(N_RECTANGLES):
   x = random.randint(0, 900)
   y = random.randint(0, 600)
   Canvas.AddRectangle(Canvas.PixelToWorld((x,y)), (80, 40), LineWidth=2, FillColor=blue)
   Canvas.AddText('Hello There', Canvas.PixelToWorld((x+1, y-30)), 8)

frame.Show()
print time.time() - start
app.MainLoop()
