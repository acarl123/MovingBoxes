# Identify Background Colors
import os, sys, shelve


class Colors:
   ObjColorDict = {
      "ACADDWG"                                :  (255,255,255),
      "AIAssembly"                             :  (255,120,0), #ORANGE
      "AIDrawing"                              :  (0,0,255), #BLUE
      "AIPart"                                 :  (0,200,0), #GREEN
      "AIPresentation"                         :  (255,255,255),
      "ExtRef"                                 :  (150,75,0), #BROWN
      "Folder"                                 :  (255,255,255),
      "ProAsm"                                 :  (255,120,0), #ORANGE
      'ProDgm'                                 :  (255,255,255),
      'ProDrw'                                 :  (0,0,255), #BLUE
      'ProFrm'                                 :  (128,0,128), #PURPLE
      'ProGph'                                 :  (255,255,255),
      'ProLay'                                 :  (190,0,0), # RED
      'ProMrk'                                 :  (255,255,255),
      'ProMfg'                                 :  (255,255,255),
      'ProPrt'                                 :  (0,200,0), #GREEN
      'ProRep'                                 :  (255,255,255),
      'ProSec'                                 :  (255,255,255),
   #
      "ProE Versioned Assembly Family Table"   :  (255,150,0), #ORANGE
      "ProE Versioned Assembly Instance"       :  (245,165,0), #ORANGE
      "ProE Versioned Assembly"                :  (255,120,0), #ORANGE
      "ProE Versioned Diagram"                 :  (255,255,255),
      "ProE Versioned Drawing"                 :  (0,0,255), #BLUE
      "ProE Versioned Format"                  :  (128,0,128), #PURPLE
      "ProE Versioned Group"                   :  (255,255,255),
      "ProE Versioned Layout"                  :  (190,0,0), # RED
      "ProE Versioned Markup"                  :  (255,255,255),
      "ProE Versioned Manufacture"             :  (255,255,255),
      "ProE Versioned Part Family Table"       :  (0,200,150), #GREEN
      "ProE Versioned Part Instance"           :  (0,230,150), #GREEN
      "ProE Versioned Part"                    :  (0,200,0), #GREEN
      "ProE Versioned Report"                  :  (255,255,255),
      "ProE Versioned Sketch"                  :  (255,255,255),
      'ProE Versioned Symbol'                  :  (255,255,255),
      'ProE Versioned Table'                   :  (255,255,255),
   # major ProE obj types (for Enovia migrations
      "ProE Assembly Family Table"             :  (255,150,0), #ORANGE
      "ProE Assembly Instance"                 :  (245,165,0), #ORANGE
      "ProE Assembly"                          :  (255,120,0), #ORANGE
      "ProE Diagram"                           :  (255,255,255),
      "ProE Drawing"                           :  (0,0,255), #BLUE
      "ProE Format"                            :  (128,0,128), #PURPLE
      "ProE Group"                             :  (255,255,255),
      "ProE Layout"                            :  (190,0,0), # RED
      "ProE Markup"                            :  (255,255,255),
      "ProE Manufacture"                       :  (255,255,255),
      "ProE Part Family Table"                 :  (0,200,150), #GREEN
      "ProE Part Instance"                     :  (0,230,150), #GREEN
      "ProE Part"                              :  (0,200,0), #GREEN
      "ProE Report"                            :  (255,255,255),
      "ProE Sketch"                            :  (255,255,255),
      'ProE Symbol'                            :  (255,255,255),
      'ProE Table'                             :  (255,255,255),
   #
      "SW2Tbx"                                 :  (255,255,255),
      "SWAsm Configuration"                    :  (245,165,0), #ORANGE
      "SWAsm Family"                           :  (255,150,0), #ORANGE
      "SWAsm"                                  :  (255,120,0), #ORANGE
      "SWDrw"                                  :  (0,0,255), #BLUE
      "SWPrt Configuration"                    :  (0,230,150), #GREEN
      "SWPrt Family"                           :  (0,200,150), #GREEN
      "SWPrt"                                  :  (0,200,0), #GREEN
      'SWPTbx'                                 :  (255,255,255),
      'SWPTbx Family'                          :  (255,255,255),
      'SWPTbx Configuration'                   :  (255,255,255),
   #
      "Inventor Part"                          :  (0,200,0), #GREEN
      "Inventor iPart Factory"                 :  (0,200,150), #GREEN
      "Inventor iPart Member"                  :  (0,230,150), #GREEN
      "Inventor Assembly"                      :  (255,120,0), #ORANGE
      "Inventor iAssembly Factory"             :  (255,150,0), #ORANGE
      "Inventor iAssembly Member"              :  (245,165,0), #ORANGE
      "Inventor Drawing"                       :  (0,0,255), #BLUE
      "Inventor Presentation"                  :  (255,255,255),
   # CATIA V5 Minor Types
      "Versioned CATDrawing"                   :  (0,0,255), #BLUE
      "Versioned CATPart"                      :  (0,200,0), #GREEN
      "Versioned CATProduct"                   :  (255,255,255),
      "Versioned CATMaterial"                  :  (255,255,255),
      "Versioned CATIA Catalog"                :  (255,255,255),
   # CATIA V5 Major Types
      "CATDrawing"                             :  (0,0,255), #BLUE
      "CATPart"                                :  (0,200,0), #GREEN
      "CATProduct"                             :  (255,255,255),
      "CATMaterial"                            :  (255,255,255),
      "CATIA Catalog"                          :  (255,255,255),
   }

   if os.path.isfile('colors.inf'):
      ObjColorDict = shelve.open('colors.inf')