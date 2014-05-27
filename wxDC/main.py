import wx
from MainController import MainController

def main():
   app = wx.App(None)
   mainFrame = MainController()
   mainFrame.show()
   app.MainLoop()

if __name__ == '__main__':
   main()
