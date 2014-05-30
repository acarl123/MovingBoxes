from NavigatorView import NavigatorFrame
import wx


class NavigatorController:
   def __init__(self):
      self.mainWindow = NavigatorFrame(None)
      self.mainWindow.Show()

      #Bindings
      self.mainWindow.Bind(wx.EVT_MENU, self.onExit, self.mainWindow.menuExit)


   def onExit(self, event):
      self.mainWindow.Destroy()
      exit()