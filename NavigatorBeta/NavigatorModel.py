import wx
import pygame


rectDict = {}
colors = {
   'BLACK' : wx.Colour(0, 0, 0),
   'BLUE' : wx.Colour(100, 223, 237),
   'GREY' : wx.Colour(173, 173, 173),
   'RED' : wx.Colour(255, 0, 0),
   'WHITE' : wx.Colour(255, 255, 255),
}

# Custom hit detection
def BB_HitTest(self, event, HitEvent):
   """ Hit Test Function for BoundingBox Based HitMap System"""
   if self.HitDict and self.HitDict[HitEvent]:
      # loop though the objects associated with this event
      objects = []  # Create object list for holding multiple objects
      object_index_list = []  # Create list for holding the indexes
      xy_p = event.GetPosition()
      xy = self.PixelToWorld(xy_p)  # Convert to the correct coords
      for key2 in self.HitDict[HitEvent].keys():
         # Get Mouse Event Position
         bb = self.HitDict[HitEvent][key2].BoundingBox
         if bb.PointInside(xy):
            Object = self.HitDict[HitEvent][key2]
            objects.append(Object)
            try:
               #First try the foreground index and add the length of the background index
               #to account for the two 'layers' that already exist in the code
               index = self._ForeDrawList.index(Object) + len(self._DrawList)
            except ValueError:
               index = self._DrawList.index(Object)  #Now check background if not found in foreground
            object_index_list.append(index)  #append the index found
         else:
            Object = self.HitDict[HitEvent][key2]
      if len(objects) > 0:  # If no objects then do nothing
         #Get the highest index object
         highest_object = objects[object_index_list.index(max(object_index_list))]
         highest_object.HitCoords = xy
         highest_object.HitCoordsPixel = xy_p
         highest_object.CallBackFuncs[HitEvent](highest_object)
         return True
      else:
         return False
   return False


class RectInfo:
   def __init__(self, color, x, y, width, height, moving=False, text=None, textFont = None, bo=None):
      self.color = color
      self.position = x, y
      self.size = width, height
      self.moving = moving
      self.text = text
      self.font = textFont
      self.bo = bo