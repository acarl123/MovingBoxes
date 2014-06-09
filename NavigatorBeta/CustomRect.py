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

   @property
   def children(self):
      return self._children

   def __init__(self, canvas, text, xy, wh, LineWidth, Fillcolor):
      self.rect = canvas.AddRectangle(canvas.PixelToWorld(xy), wh, LineWidth=LineWidth, FillColor=Fillcolor)
      self.text = canvas.AddScaledText(text, canvas.PixelToWorld((xy[0] + 40, xy[1] - 17.5)), 7, Position="cc")
      self.rect.Text = self.text
      self._bo = None
      self._revisions = []
      self._parents = []
      self._children = []

      # TODO: Need to query EFS for list of parents and children