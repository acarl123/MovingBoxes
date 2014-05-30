from NavigatorView import NavigatorFrame


class NavigatorController:
   def __init__(self):
      self.mainWindow = NavigatorFrame(None)
      self.mainWindow.Show()

      #Bindings