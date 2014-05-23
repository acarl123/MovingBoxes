import wx


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

N_BIG_RECTS = 2500


