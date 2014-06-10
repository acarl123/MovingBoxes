import wx
import pygam


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


class NavRect:
   @property
   def revisions(self):
      return self._revisions

   @revisions.setter
   def revisions(self, value):
      self._revisions = value

   @property
   def bo(self):
      return self._bo

   @bo.setter
   def bo(self, value):
      self._bo = value

   @property
   def parents(self):
      return self._parents

   @parents.setter
   def parents(self, value):
      self.parents = value

   @property
   def children(self):
      return self._children

   @children.setter
   def children(self, value):
      self.children = value

   def __init__(self, canvas, text, xy, wh, LineWidth, Fillcolor):
      self.rect = canvas.AddRectangle(canvas.PixelToWorld(xy), wh, LineWidth=LineWidth, FillColor=Fillcolor)
      self.text = canvas.AddScaledText(text, canvas.PixelToWorld((xy[0] + 40, xy[1] - 17.5)), 7, Position="cc")
      self.rect.Text = self.text
      self._bo = None
      self._revisions = []
      self._parents = []
      self._children = []

      # TODO: Need to query EFS for list of parents and children


class RectDict:
   _rectDict = {}

   @property
   def rectDict(self):
      return self._rectDict

   @rectDict.setter
   def rectDict(self, value):
      self._rectDict = value