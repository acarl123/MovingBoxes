import sys; sys.path.append('C:\\hg\\tools_lag\\EFSUtils')
import wx
from NavigatorController import NavigatorController
from NavigatorControllerExperiment import NavigatorController

def _main():
   app = wx.App(None)
   frame = NavigatorController()
   frame.show()
   app.MainLoop()

if __name__ == '__main__': _main()