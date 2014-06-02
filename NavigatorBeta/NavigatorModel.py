import wx
import pygame


rectDict = {}


class RectInfo:
   def __init__(self, color, x, y, width, height, moving=False, text=None, textFont = None, bo=None):
      self.color = color
      self.position = x, y
      self.size = width, height
      self.moving = moving
      self.text = text
      self.font = textFont
      self.bo = bo