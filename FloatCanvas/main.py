import wx
from mainController import Main

# comment to push

def main():
   app = wx.App(None)
   mainFrame = Main()
   mainFrame.show()
   app.MainLoop()

if __name__ == '__main__': main()