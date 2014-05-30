import pygame, sys, random, time
pygame.init()

size = width, height = 1024, 768
screen = pygame.display.set_mode(size, pygame.DOUBLEBUF | pygame.RESIZABLE)
random.seed()

N_RECTANGLES = 2500
N_FRAMES = 100
blue = 100, 223, 237
black = 0, 0, 0
need_screen_update = True
frameCounter = 0

start = time.time()

font = pygame.font.Font(None, 16)
text = font.render("Hello There", 1, (10, 10, 10))
textpos = text.get_rect()

while frameCounter < N_FRAMES:
   frameCounter += 1
   for event in pygame.event.get():
      if event.type == pygame.QUIT:
         sys.exit(0)

      if event.type == pygame.MOUSEBUTTONDOWN:
         need_screen_update = True

   if need_screen_update:
      screen.fill(black)
      # need_screen_update = False
      for i in range(N_RECTANGLES):
         x = random.randint(0, 900)
         y = random.randint(0, 600)
         pygame.draw.rect(screen,
                          blue,
                          (x,
                           y,
                           80,
                           40),
         )

         pygame.draw.rect(screen,
                          black,
                          (x,
                           y,
                           80,
                           40,),
                           2,
         )
         textpos.centerx = x + 40
         textpos.centery = y + 20
         screen.blit(text, textpos)

   pygame.display.update()

print time.time() - start
