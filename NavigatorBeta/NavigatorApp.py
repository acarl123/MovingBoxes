import wx
from NavigatorController import NavigatorController


def _main():
   app = wx.App(None)
   frame = NavigatorController()
   app.MainLoop()


if __name__ == '__main__': _main()