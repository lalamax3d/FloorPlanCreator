import bpy
import os
import sys
import math


import sys
sys.path.append("..") # Adds higher directory to python modules path.

# Import library
from FloorplanToBlenderLib import *
from FloorplanToBlenderLib.find_windows_and_doors import *
# from FloorplanToBlenderLib import find_windows_and_doors
#from . import FloorplanToBlenderLib as fpl

# Other necessary libraries
import cv2 # for image gathering
import numpy as np

# for visualize
#from PIL import Image
#from IPython.display import display


door_path = os.path.abspath("D:\\FloorplanToBlender3d\\Images\\Models\\Doors\\door.png")
rd_door = cv2.imread(door_path)
door_img = cv2.cvtColor(rd_door, cv2.COLOR_BGR2GRAY)
window_path = os.path.abspath("D:\\FloorplanToBlender3d\\Images\\Models\\Windows\\window.png")
rd_window = cv2.imread(window_path)
window_img = cv2.cvtColor(rd_window, cv2.COLOR_BGR2GRAY)


# Detect Contours
def precise_boxes(detect_img, output_img=None, color=[100, 100, 0]):
    """
    Detect corners with boxes in image with high precision
    @Param detect_img image to detect from @mandatory
    @Param output_img image for output
    @Param color to set on output
    @Return corners(list of boxes), output image
    @source https://stackoverflow.com/questions/50930033/drawing-lines-and-distance-to-them-on-image-opencv-python
    """
    res = []
    
    contours, hierarchy = cv2.findContours(detect_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE )
    print ("TOTAL CONTOURS:", len(contours))
    for cnt in contours:
        print ("CONTOUR points before optimization: ", cnt.shape)
        epsilon = const.PRECISE_BOXES_ACCURACY * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)
        print ("CONTOUR points after optimization: ", approx.shape)
        if output_img is not None:
            output_img = cv2.drawContours(output_img, [approx], 0, color,5)
        res.append(approx)

    return res, output_img

def detect_rooms(img_path):
    img = cv2.imread(img_path)
    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    wall_img = detect.wall_filter(gray_image)
    blank_image = img.copy()
    gray = ~wall_img
    rooms,colored_rooms = detect.find_rooms(gray)
    gray_rooms = cv2.cvtColor(colored_rooms, cv2.COLOR_BGR2GRAY)

    boxes, blank_image = detect.precise_boxes(
        gray_rooms,blank_image,color=(255,0,0)
    )
    # Save
    directory = os.path.dirname(img_path)
    cv2.imwrite(directory + '/step3.png', blank_image) 

    blank_image = img.copy()
    doors, colored_doors = detect.find_details(gray.copy())
    gray_details = cv2.cvtColor(colored_doors, cv2.COLOR_BGR2GRAY)
    boxes, blank_image = detect.precise_boxes(
    gray_details, blank_image, color=(255, 0, 0)
    )
        # Save
    directory = os.path.dirname(img_path)
    cv2.imwrite(directory + '/step4.png', blank_image)

    img0 = cv2.imread(img_path)
    img1 = cv2.imread(img_path,0)
    img2 = cv2.imread(door_path,0)
    blank_image = detect_windows_and_doors_boxes(img0,feature_match(img1,img2))
        # Save
    # directory = os.path.dirname(img_path)
    # cv2.imwrite(directory + '/step5.png', blank_image) 

def detect_walls(img_path):
    print("running function")
    img = cv2.imread(img_path)
    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    height,width,channels = img.shape
    blank_image = img.copy()
    # wall_img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY
    wall_img = detect.wall_filter(gray_image)
    boxes,w_img = detect.precise_boxes(wall_img,blank_image,color=[0,0,255])
    print ("BOXES", boxes)
    

    # Save
    directory = os.path.dirname(img_path)
    cv2.imwrite(directory + '/step2.png', blank_image) 
    print("done")

    


def detect_contour(img_path):
    # Read floorplan image
    img = cv2.imread(img_path)
    height, width, channels = img.shape[:3]
    blank_image = img.copy()
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    contour, c_img = detect.outer_contours(gray, blank_image, color=(255,0,0))
    # Save
    directory = os.path.dirname(img_path)
    cv2.imwrite(directory + '/step1.png', blank_image)
    # print (contour)
    # print (contour.dtype)
    # print (contour.shape)
    # print (c_img)
    # print (c_img.shape)


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
                detect_walls(imgpath)
                detect_rooms(imgpath)
                


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