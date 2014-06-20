import wx


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

   @property
   def name(self):
      return self._name

   @name.setter
   def name(self, value):
      self._name = value

   def __init__(self, name, canvas, text, xy, LineWidth, FillColor, LineColor):
      # self.rect = canvas.Canvas.AddRectangle(canvas.Canvas.PixelToWorld(xy), wh, LineWidth=LineWidth, FillColor=Fillcolor, LineColor=LineColor)
      # self.text = canvas.Canvas.AddScaledText(text, canvas.Canvas.PixelToWorld((xy[0] + wh[0]/2/canvas.scale, xy[1] - wh[1]/2/canvas.scale)),
      #                                         Size=12, Family=wx.ROMAN, Weight=wx.BOLD)
      self.text = canvas.Canvas.AddScaledText(text, canvas.Canvas.PixelToWorld(xy),
                                              Size=12, Family=wx.ROMAN, Weight=wx.BOLD)
      wh = self.text.BoundingBox.Width, self.text.BoundingBox.Height
      self.rect = canvas.Canvas.AddRectangle(canvas.Canvas.PixelToWorld((xy[0], xy[1]+wh[1]/canvas.scale)),
                                             wh, LineWidth=LineWidth, FillColor=FillColor, LineColor=LineColor)

      self.rect.Text = self.text
      self._name = name
      # self._bo = None
      self._revisions = {}
      self._revisionRects = []
      self._revisionRects = {}
      self._parents = []
      self._children = []

      self._revShown = False
      self._childrenShown = False

      self.rect.Name = self._name

      # TODO: Need to query EFS for list of parents and children


class RectDict(object):
   @property
   def rectDict(self):
      return self._rectDict

   @rectDict.setter
   def rectDict(self, value):
      self._rectDict = value

   @property
   def keys(self):
      return self._rectDict.keys()

   @property
   def values(self):
      return self._rectDict.values()

   # Class methods
   def __len__(self):
      return len(self._rectDict)

   def __getitem__(self, item):
      try:
         if isinstance(item, (int, long)):
            return self._rectDict[item]
         elif isinstance(item, basestring):
            return self._rectDict[int(item)]
         elif isinstance(item, NavRect):
            return self.__getitem__(item.name)
         else:
            print 'Key Search for type %s not supported' % item
      except KeyError:
         print 'Key Error for: ' + str(item)

   def __setitem__(self, key, value):
      if isinstance(key, (int, long)):
            myKey = key
      elif isinstance(key, basestring):
            myKey = int(key)
      self._rectDict[myKey] = value


   def __iter__(self):
      return self._rectDict.itervalues()

   def __delitem__(self, key):
      self._rectDict.__delitem__(int(self.__getitem__(key).name))

   def __init__(self):
      self._rectDict = {}

   # Custom methods to add functionality to the main dictionary
   def append(self, rectObj):
      self._rectDict[int(rectObj.rect.Name)] = rectObj