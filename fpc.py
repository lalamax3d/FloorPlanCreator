import bpy
import os
import sys
import math


import sys
sys.path.append("..") # Adds higher directory to python modules path.

# Import library
from FloorplanToBlenderLib import *
#from . import FloorplanToBlenderLib as fpl

# Other necessary libraries
import cv2 # for image gathering
import numpy as np

# for visualize
#from PIL import Image
#from IPython.display import display

# Detect Contours

def detect_contour(img_path):
    # Read floorplan image
    img = cv2.imread(img_path)

    # Create blank image
    height, width, channels = img.shape
    blank_image = img.copy()

    # Grayscale image
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

    # detect outer Contours (simple floor or roof solution), paint them red on blank_image
    
    contour, c_img = detect.outer_contours(gray, blank_image, color=(255,0,0))

    # Display
    #display(Image.fromarray(blank_image))
    print ("HERE")
    # Save
    directory = os.path.dirname(img_path)
    cv2.imwrite(directory + '/step1.png', blank_image)
    print (contour)
    print (contour.dtype)
    print (contour.shape)
    print (c_img)
    print (c_img.shape)


class LoadFloorPlanImageOperator(bpy.types.Operator):
    bl_idname = "object.loadfloorplanimage"
    bl_label = "loadFloorPlanImage"

    def execute(self, context):
        return {'FINISHED'}

class ProcessFloorPlanImageOperator(bpy.types.Operator):
    bl_idname = "fpc.processfloorplanimage"
    bl_label = "processFloorPlanImage"

    def execute(self, context):
        o = context.active_object
        if o:
            if o.empty_display_type == 'IMAGE':
                print("Image")
                print(o.data.name)
                print(o.data.filepath)
                #print (bpy.path.abspath (o.data.filepath, library=tex.library))
                filepath = bpy.data.filepath
                directory = os.path.dirname(filepath)
                imgpath = bpy.path.abspath (o.data.filepath, start=None, library=None)
                print (imgpath)
                detect_contour(imgpath)

                


        return {'FINISHED'}


################
# EXTRA STUFF
################
def UpdatedFunction(self, context):
    print("Updating Function")
    print(self.fc_activeJson)
    # FF_PT_Model.testValue = self.sk_filterStr
    return
# from . ff_model import MyPropertyGroup

def state():
    return bpy.context.scene.ff_FPC_prop_grp
class FpcPropGrp(bpy.types.PropertyGroup):

    Src_Rig: bpy.props.PointerProperty(
        type=bpy.types.Object,
        poll=lambda self, obj: obj.type == 'ARMATURE' ,
        update=lambda self, ctx: state().update_source()
    )

    invalid_selected_source: bpy.props.PointerProperty(
        type=bpy.types.Object,
    )
    #source: bpy.props.PointerProperty(type=bpy.types.Object)
    targetRig: bpy.props.PointerProperty(
        type=bpy.types.Object,
        poll=lambda self, obj: obj.type == 'ARMATURE' ,
        update=lambda self, ctx: state().update_source()
    )
    drawPoints: bpy.props.BoolProperty(name="Draw Points", description="Draw points , helpful for dubugging", default=False)
    cHead: bpy.props.BoolProperty(name="Head", description="capture head rotation or not", default=False)
    sHead: bpy.props.FloatProperty(name="Smooth",default=4.5)
    cMouth: bpy.props.BoolProperty(name="Mouth", description="Mouth / Jaw", default=False)
    sMouth: bpy.props.FloatProperty(name="Smooth",default=1.5)
    cEyes: bpy.props.BoolProperty(name="Eyes", description="capture eyes", default=False)
    sEyes: bpy.props.FloatProperty(name="Smooth",default=0.5)

    cBrows: bpy.props.BoolProperty(name="Brows", description="capture brows", default=False)
    sBrows: bpy.props.FloatProperty(name="Smooth",default=2.1)

    enableStart: bpy.props.BoolProperty(name="All Good", description="Lets start", default=False)

    def update_source(self):
        print ("Update Source in PropGroup")
        if bpy.context.object.type == 'ARMATURE':
            self.targetRig = bpy.context.object
        if self.targetRig != None:
            self.enableStart = True
            return
        # else:
        #     print ("SKIPPING")
        #     self.enableStart = False
        #     return



bpy.utils.register_class(FpcPropGrp)



def register():
    bpy.utils.register_class(ProcessFloorPlanImageOperator)

def unregister():
    bpy.utils.unregister_class(ProcessFloorPlanImageOperator)

if __name__ == "__main__":
    register()