from collections import OrderedDict
import sys, pygame, random, os, time
from PopupMenu import NonBlockingPopupMenu as PopupMenu
from pygame.locals import *

# os.environ['SDL_VIDEO_CENTERED'] = '1'
pygame.init()

# Consts
black = 0, 0, 0
blue = 100, 223, 237
grey = 173,173,173
red = 255, 255, 255
white = 255, 255, 255
pos = 0,0
clock = pygame.time.Clock()

N_RECTANGLES = 20
FONT = pygame.font.Font(None, 20)
TEXT = None
TEXTPOS = 0, 0, 0, 0

menu_data = ( # TODO: move this into the rect class
   'Main',
   'Print fps',
   'Item 1',
   (
      'Things',
      'Item 0',
      'Item 1',
      'Item 2',
      (
         'More Things',
         'Item 0',
         'Item 1',
      ),
   ),
   'Quit',
)
menu = PopupMenu(menu_data)

# Extension of the pygame rect to add all of the features and attributes we need.  Add as necessary
class Rect:
   def __init__(self, surface, color, x, y, width, height, moving=False, text=None, textFont = None, TextPos=None, bo=None):
      font = pygame.font.SysFont('lucidasans, arialrounded, berlinsansfb, arial,', height/4)
      self.surface = surface
      self.color = color
      self.position = x, y
      self.size = width, height
      self.moving = moving
      self.rectText = text
      self.text = font.render(text, True, black)
      self.textPos = TextPos
      self.rect = pygame.draw.rect(self.surface, self.color, (x, y, width, height), 0)
      self.selected = False
      self.borderColour = black

   def select(self):
      if self.selected:
         self.borderColour = red
      else:
         self.borderColour = black

   def scaleFont(self, size):
      font = pygame.font.SysFont('lucidasans, arialrounded, berlinsansfb, arial,', size)
      self.text = font.render(self.rectText, True, black)


class Main:
   def __init__(self):
      self.size = width, height = 1024, 768
      self.screen = pygame.display.set_mode(self.size, pygame.DOUBLEBUF|pygame.RESIZABLE)
      self.rects = OrderedDict()
      self.moving = False
      self.randnum = random
      self.randnum.seed()
      self.selectedRects = []

      # Draw all rects and populate a rect dict with all of them
      for i in range(N_RECTANGLES):
         self.rects[i] = Rect(self.screen,
                              blue,
                              x=self.randnum.randint(0, 900),
                              y=self.randnum.randint(0, 600),
                              width=80,
                              height=40,
                              moving=False,
                              text='rect %s' % (i+1)
         )

   def handle_menu(self, e):
      global menu
      # print 'Menu event: %s.%d: %s' % (e.name, e.item_id, e.text)
      if e.name is None:
         # print 'Hide menu'
         menu.hide()
      elif e.name == 'Main':
         if e.text == 'Quit':
            quit()
         if e.text == 'Print fps':
            print self.fps
      elif e.name == 'Things':
         pass
      elif e.name == 'More Things':
         pass

   def run(self):
      lastrel = 0, 0
      clicked = False, 0
      drawrect = False
      ctrlPressed = False
      selected = False
      moving = False
      fps=60
      DISPLAY_REFRESH = USEREVENT
      pygame.time.set_timer(DISPLAY_REFRESH, int(1000.0/fps))
      first = True
      update = False

      # ------------------------------ Main loop -------------------------------

      while 1:
         clock.tick(60)
         self.fps = clock.get_fps()
         mousepos = pygame.mouse.get_pos()
         mouserel = pygame.mouse.get_rel()
         self.screen.fill(grey)

         # for e in menu.handle_events(pygame.event.get()):
         #    if e.type == pygame.KEYDOWN:
         #       print 'Key pressed:', pygame.key.name(e.key)
         #    elif e.type == pygame.MOUSEBUTTONUP:
         #       print 'Show menu'
         #       menu.show()
         #    # elif e.type == pygame.MOUSEMOTION:
         #    #    cursor.rect.center = e.pos
         #    elif e.type == pygame.USEREVENT:
         #       if e.code == 'MENU':
         #          self.handle_menu(e)

         for event in menu.handle_events(pygame.event.get()): # the custom menu has to handle all of the events first and then it returns a list of the unhandled events that pygame can then handle
            if event.type == pygame.QUIT: sys.exit(0)
            elif event.type == VIDEORESIZE:
               update = True
               self.screen = pygame.display.set_mode(event.dict['size'], HWSURFACE | DOUBLEBUF | RESIZABLE)
               self.screen.blit(pygame.transform.scale(self.screen, event.dict['size']), (0, 0))
               pygame.display.flip()

            if event.type == pygame.KEYDOWN:
               update = True
               if pygame.key.get_mods() == 64:
                  ctrlPressed = True

            if event.type == pygame.KEYUP:
               update = False
               ctrlPressed = False

            if event.type == pygame.MOUSEBUTTONDOWN:
               update = True
               if event.button == 1:
                  for key, rectAttrs in self.rects.iteritems():
                     if rectAttrs.rect.collidepoint(mousepos):
                        rectAttrs.moving = True
                        clicked = True, key
                        if rectAttrs.selected: selected=True
                  if clicked[0]:
                     if not clicked[1] in self.selectedRects and not ctrlPressed:
                        for rects in self.selectedRects:
                           self.rects[rects].selected = False
                           self.rects[rects].select()
                        self.selectedRects = []
                     self.rects[clicked[1]].selected = True
                     self.rects[clicked[1]].select()
                     self.selectedRects.append(clicked[1])
                     self.rects[clicked[1]] = self.rects.pop(clicked[1])
                     clicked = False, 0
                     selected = True
                  else:
                     for rects in self.selectedRects:
                        self.rects[rects].selected = False
                        self.rects[rects].select()
                     self.selectedRects = []
                     if not drawrect: startPos = mousepos
                     drawrect = True
                     selected = False

               elif event.button == 3:
                  print "right click"
                  pass

               elif event.button == 2:
                  moving = True

            if event.type == pygame.MOUSEBUTTONUP:
               update = False
               if event.button == 3:
                  update = True
                  for key, rectAttrs in self.rects.iteritems():
                     if rectAttrs.rect.collidepoint(mousepos):
                        menu.show()
               elif event.button == 1:
                  for rectAttrs in self.rects.itervalues():
                     rectAttrs.moving = False
                  drawrect = False
               elif event.button == 2:
                  moving = False
               elif event.button == 4: # mousewheel up
                  update = True
                  for key, rectAttrs in self.rects.items():
                     rectAttrs.rect.inflate_ip(10, 5)
                     rectAttrs.rect.move_ip((rectAttrs.rect[0]-(mousepos[0]-rectAttrs.rect[2]/2))/5,
                                            (rectAttrs.rect[1]-(mousepos[1]-rectAttrs.rect[3]/2))/5)
                     rectAttrs.scaleFont(rectAttrs.rect[3]/4)
               elif event.button == 5: # mousewheel down
                  update = True
                  for key, rectAttrs in self.rects.items():
                     rectAttrs.rect.inflate_ip(-10, -5)
                     rectAttrs.rect.move_ip(((mousepos[0]-rectAttrs.rect[2])-rectAttrs.rect[0])/5,
                                            ((mousepos[1]-rectAttrs.rect[3])-rectAttrs.rect[1])/5)
                     rectAttrs.scaleFont(rectAttrs.rect[3] / 4)

            if event.type == USEREVENT:
               if event.code == 'MENU':
                  self.handle_menu(event)

         if update == True or first == True:
            first = False
            rectList = dict((tuple(rect.rect), key) for key, rect in self.rects.items())

            for key, rectAttrs in self.rects.items():
               if (tuple(rectAttrs.rect)) in rectList.keys():
                  rectList.pop(tuple(rectAttrs.rect))

               # Check to keep self-fixing collisions from flying scross the screen; max movement speed for smoothness
               # if abs(mouserel[0]) > 3:
               #    if mouserel[0] > 0: mouserel = 3, mouserel[1]
               #    else: mouserel = -3, mouserel[1]
               # if abs(mouserel[1]) > 3:
               #    if mouserel[1] > 0:mouserel = mouserel[0], 3
               #    else: mouserel = mouserel[0], -3

               if rectAttrs.moving:
                  origRel = pygame.mouse.get_rel()
                  for rect in self.selectedRects:
                     self.rects[rect].rect[0] += (origRel[0])
                     self.rects[rect].rect[1] += (origRel[1])

               if moving: # moves the whole canvas while holding middle click
                  rectAttrs.rect[0] += mouserel[0]
                  rectAttrs.rect[1] += mouserel[1]

               rectColList = rectAttrs.rect.collidedictall(rectList)
               if not rectColList: rectColList = []
               # collision detection shouldn't autocorrect when the rectangle isn't the focus
               if rectAttrs.selected or not selected:
                  for rectNums in xrange(len(rectColList)):
                     rectNum = rectColList[rectNums][1]
                     if lastrel == (0, 0) and self.rects[key].rect.collidedict(rectList) and (self.rects[rectNum].selected or not selected):
                        if self.fps < 60 and self.fps != 0:
                           multiplier = (60/self.fps)/2
                        else: multiplier = 1
                        if rectAttrs.rect.collidepoint(self.rects[rectNum].rect[0], self.rects[rectNum].rect[1]):
                           lastrel = 1 * multiplier, 1* multiplier
                        elif rectAttrs.rect.collidepoint(self.rects[rectNum].rect[0]+self.rects[rectNum].rect[2], self.rects[rectNum].rect[1]):
                           lastrel = -1* multiplier, 1* multiplier
                        elif rectAttrs.rect.collidepoint(self.rects[rectNum].rect[0], self.rects[rectNum].rect[1]+self.rects[rectNum].rect[3]):
                           lastrel = 1* multiplier, -1* multiplier
                        elif rectAttrs.rect.collidepoint(self.rects[rectNum].rect[0]+self.rects[rectNum].rect[2], self.rects[rectNum].rect[1] + self.rects[rectNum].rect[3]):
                           lastrel = -1* multiplier, -1* multiplier
                     else:
                        lastrel = 0,0

                     self.rects[rectNum].rect[0] += lastrel[0]
                     self.rects[rectNum].rect[1] += lastrel[1]
                     rectList[tuple(self.rects[rectNum].rect)] = key
               rectList[tuple(rectAttrs.rect)] = key

               # Drawing the text and the rectangles, must be in this order so text renders on top of rect!
               if not rectAttrs.selected and selected:opacity=128#rectAttrs.color=193,222,230
               else:opacity=255
               # pygame.draw.rect(self.screen, rectAttrs.color, rectAttrs.rect)

               # have to convert the rects to a surface in order to introduce opacity
               s = pygame.Surface((rectAttrs.rect[2], rectAttrs.rect[3]))
               s.set_alpha(opacity)
               s.fill((rectAttrs.color))
               self.screen.blit(s, (rectAttrs.rect[0], rectAttrs.rect[1]))

               pygame.draw.rect(self.screen, black, rectAttrs.rect, 2)
               rectAttrs.textPos = rectAttrs.text.get_rect()

               rectAttrs.textPos.centerx = rectAttrs.rect.centerx
               rectAttrs.textPos.centery = rectAttrs.rect.centery
               self.screen.blit(rectAttrs.text, rectAttrs.textPos)

               if key != 0:pygame.draw.line(self.screen, black,
                                              (self.rects[0].rect[0], self.rects[0].rect[1]),
                                              (rectAttrs.rect[0],rectAttrs.rect[1]))

               # Draw selection rectangle
               if drawrect:
                  selectRect = pygame.draw.rect(self.screen, red, (startPos[0], startPos[1],mousepos[0]-startPos[0], mousepos[1]-startPos[1]), 1)
                  if rectAttrs.rect.colliderect(selectRect):
                     rectAttrs.selected = True
                     rectAttrs.select()
                     self.selectedRects.append(key)
                     selected = True
               # remove problems with duplicates...
               self.selectedRects = list(set(self.selectedRects))
               # highlight selected rects
               if rectAttrs.selected: pygame.draw.rect(self.screen, white, (rectAttrs.rect[0] -2, rectAttrs.rect[1]-2, rectAttrs.rect[2]+4, rectAttrs.rect[3]+4), 2)

            menu.draw()
            pygame.display.update()

#run statement
if __name__ == '__main__':
   myGame = Main()
   myGame.run()