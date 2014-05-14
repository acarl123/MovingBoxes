import wx
import os
import thread
global pygame

class SDLThread:
    def __init__(self,screen):
        self.m_bKeepGoing = self.m_bRunning = False
        self.screen = screen
        self.color = (255,0,0)
        self.rect = (10,10,100,100)
        self.testFrame = TestFrame(None)
        self.counter = 0

    def Start(self):
        self.m_bKeepGoing = self.m_bRunning = True
        thread.start_new_thread(self.Run, ())

    def Stop(self):
        self.m_bKeepGoing = False

    def IsRunning(self):
        return self.m_bRunning

    def Run(self):
        while self.m_bKeepGoing:
            e = pygame.event.poll()
            if e.type == pygame.MOUSEBUTTONDOWN:
                self.color = (255,0,128)
                self.rect = (e.pos[0], e.pos[1], 100, 100)
                print e.pos
                self.testFrame.m_listCtrl1.DeleteAllItems()
                self.testFrame.m_listCtrl1.InsertStringItem(0, 'thing {0}'.format(self.counter))
                self.testFrame.Show()
                self.counter += 1
            self.screen.fill((0,0,0))
            self.screen.fill(self.color,self.rect)
            pygame.display.flip()
        self.m_bRunning = False;

class SDLPanel(wx.Panel):
    def __init__(self,parent,ID,tplSize):
        global pygame
        wx.Panel.__init__(self, parent, ID, size=tplSize)
        self.Fit()
        os.environ['SDL_WINDOWID'] = str(self.GetHandle())
        os.environ['SDL_VIDEODRIVER'] = 'windib'
        import pygame # this has to happen after setting the environment variables.
        pygame.display.init()
        window = pygame.display.set_mode(tplSize)
        self.thread = SDLThread(window)
        self.thread.Start()

    def __del__(self):
        self.thread.Stop()

class MyFrame(wx.Frame):
    def __init__(self, parent, ID, strTitle, tplSize):
        wx.Frame.__init__(self, parent, ID, strTitle, size=tplSize)
        self.pnlSDL = SDLPanel(self, -1, tplSize)
        #self.Fit()

class TestFrame ( wx.Dialog ):
   def __init__( self, parent ):
      wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE )

      self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )

      bSizer1 = wx.BoxSizer( wx.VERTICAL )

      self.m_listCtrl1 = wx.ListCtrl(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_ICON)
      bSizer1.Add(self.m_listCtrl1, 0, wx.ALL, 5)

      self.btnOK = wx.Button( self, wx.ID_OK, u"OK", wx.DefaultPosition, wx.DefaultSize, 0 )
      bSizer1.Add( self.btnOK, 0, wx.ALL|wx.EXPAND, 5 )


      self.SetSizer( bSizer1 )
      self.Layout()
      bSizer1.Fit( self )

      self.Centre( wx.BOTH )

      # Connect Events
      self.btnOK.Bind( wx.EVT_BUTTON, self.btnClick )

   def __del__( self ):
      pass

# Virtual event handlers, override them in your derived class
   def btnClick( self, event ):
      print self.btnOK.Id
      event.Skip()


if __name__ == "__main__":
   app = wx.PySimpleApp()
   frame = MyFrame(None, wx.ID_ANY, "SDL Frame", (640,480))
   frame.Show()
   app.MainLoop()