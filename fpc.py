import os
import sys
import math
import bpy
import bmesh
from mathutils import Vector
import addon_utils


sys.path.append(".") # Adds higher directory to python modules path.
# Other necessary libraries
import cv2 # for image gathering
import numpy as np


sys.path.insert(0, "..")
from FloorplanToBlenderLib import (
    config,
    floorplan,
    generate,
    execution,
    IO,
    const,
)  # floorplan to blender lib


from . import FloorplanToBlenderLib as fpb
# print (fpb)
# print (fpb.detect)


door_path = os.path.abspath("Models\\Doors\\door.png")
if not os.path.isfile(door_path):
    print("File path {} does not exist. Exiting...".format(door_path))
else:
    print("File path {} exists.".format(door_path))
    rd_door = cv2.imread(door_path)
    door_img = cv2.cvtColor(rd_door, cv2.COLOR_BGR2GRAY)
    window_path = os.path.abspath("Models\\Windows\\window.png")
    rd_window = cv2.imread(window_path)
    window_img = cv2.cvtColor(rd_window, cv2.COLOR_BGR2GRAY)



   

# Detect Contours(step 1) BOUNDARY COUNTOUR
def detect_contour(img_path):
    # detecting outer most contour (big map boundary)
    # Read floorplan image
    img = cv2.imread(img_path)
    height, width, channels = img.shape[:3]
    print ("Image size: ", height, width, channels)
    blank_image = img.copy()
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    contour, c_img = fpb.detect.outer_contours(gray, blank_image, color=(255,0,0))
    # Save
    directory = os.path.dirname(img_path)
    cv2.imwrite(directory + '/step1_Countour.png', blank_image)
    # print (contour)
    # print (contour.dtype)
    # print (contour.shape)
    # print (c_img)
    # print (c_img.shape)

# Detect walls(step 2)
def detect_walls(img_path):
    ''' Detect walls in image'''

    print("running function")
    img = cv2.imread(img_path)
    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    height,width,channels = img.shape
    blank_image = img.copy()
    # wall_img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY
    wall_img = fpb.detect.wall_filter(gray_image)
    boxes,w_img = fpb.detect.precise_boxes(wall_img,blank_image,color=[0,0,255])
    print ("BOXES", boxes)
    # Save
    directory = os.path.dirname(img_path)
    cv2.imwrite(directory + '/step2_walls.png', blank_image) 
    print("done")

# Detect rooms(step 3)
def detect_rooms(img_path):
    ''' Detect rooms in image'''
    img = cv2.imread(img_path)
    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    wall_img = fpb.detect.wall_filter(gray_image)
    blank_image = img.copy()
    gray = ~wall_img # inverting colors
    rooms,colored_rooms = fpb.detect.find_rooms(gray)
    gray_rooms = cv2.cvtColor(colored_rooms, cv2.COLOR_BGR2GRAY)

    boxes, blank_image = fpb.detect.precise_boxes(
        gray_rooms,blank_image,color=(255,0,0)
    )
    # Save
    directory = os.path.dirname(img_path)
    cv2.imwrite(directory + '/step3_rooms.png', blank_image)

# Detect DoorWindows(step 4)
def detect_doorAndWindows(img_path):
    print ("FineDetails..")
    img = cv2.imread(img_path)
    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    wall_img = fpb.detect.wall_filter(gray_image)
    blank_image = img.copy()
    gray = ~wall_img
    blank_image = img.copy()
    doors, colored_doors = fpb.detect.find_details(gray.copy())
    gray_details = cv2.cvtColor(colored_doors, cv2.COLOR_BGR2GRAY)
    boxes, blank_image = fpb.detect.precise_boxes(
    gray_details, blank_image, color=(255, 0, 0)
    )
    print ("Precise Boxes")
    directory = os.path.dirname(img_path)
    cv2.imwrite(directory + '/step4_doorWindows.png', blank_image)

# FineDetails (seprating doors_n_windows) (step 5)
def detect_doors(img_path):
    '''
    ORB feature extraction
    '''
    img0 = cv2.imread(img_path)
    img1 = cv2.imread(img_path,0)
    img2 = cv2.imread(door_path,0)
    doorPatternMatchedList = fpb.find_windows_and_doors.feature_match(img1,img2)
    print (doorPatternMatchedList)
    blank_image = fpb.find_windows_and_doors.detect_windows_and_doors_boxes(img0,doorPatternMatchedList)
    # Save
    directory = os.path.dirname(img_path)
    cv2.imwrite(directory + '/step5_doorsAligned.png', blank_image) 

def createSplineCurve(contour):
    # Create a new curve object and add it to the scene
    curve = bpy.data.curves.new(name="Contour", type='CURVE')
    curve.dimensions = '2D'
    obj = bpy.data.objects.new(name="Contour", object_data=curve)
    bpy.context.scene.collection.objects.link(obj)

    # Create a new spline and add points to it
    spline = curve.splines.new(type='POLY')
    spline.points.add(len(contour))
    for i, point in enumerate(contour):
        x, y = point[0]
        spline.points[i].co = (x, y, 0, 1)

    # Set the curve to be closed
    spline.use_cyclic_u = True

def createContourObject(obj,cname,contour, alignbbox=False, matchScale=False):
    '''
    Create a new object with a mesh that matches the given contour
    also cname will be used to create mesh data attribute (name) mostly on vertices with value of 1
    '''
    # Get the bounding box vertices in object space
    bbox_verts = obj.bound_box

    # Convert the bounding box vertices to world space
    bbox_verts_world = [obj.matrix_world @ Vector(v) for v in bbox_verts]

    # Find the min and max coordinates of the bounding box in world space
    bbox_min = min(bbox_verts_world, key=lambda v: v[0])[0], \
            min(bbox_verts_world, key=lambda v: v[1])[1], \
            min(bbox_verts_world, key=lambda v: v[2])[2]
    bbox_max = max(bbox_verts_world, key=lambda v: v[0])[0], \
            max(bbox_verts_world, key=lambda v: v[1])[1], \
            max(bbox_verts_world, key=lambda v: v[2])[2]

    # Print the bounding box coordinates
    print("Bounding box min:", bbox_min)
    print("Bounding box max:", bbox_max)

    # Create Curve (polygon)
    # draw contour in blender

    #bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
    # Create an empty object to hold the vertices
    mesh = bpy.data.meshes.new(name=cname)
    newobj = bpy.data.objects.new(name=cname, object_data=mesh)
    bpy.context.scene.collection.objects.link(newobj)

    # Add a vertex for each point in the contour
    # for point in contour:
    #     x, y = point[0]
    #     z = 0
    #     bpy.ops.mesh.primitive_vert_add(location=(x, y, z))
    # Create a BMesh and add vertices to it
    bm = bmesh.new()
    for point in contour:
        x, y = point[0]
        z = 0
        bm.verts.new((x, y, z))
    # Call ensure_lookup_table() to update the internal index table
    bm.verts.ensure_lookup_table()

    # Connect the vertices to create edges and a closed polygon
    for i in range(len(contour)):
        bm.edges.new([bm.verts[i], bm.verts[(i+1)%len(contour)]])

    # Call ensure_lookup_table() again to update the internal index table
    bm.edges.ensure_lookup_table()

    # Update the mesh with the BMesh data
    # Update the mesh with the BMesh data
    bm.to_mesh(mesh)
    bm.free()
    # set attribute value to 1
    #attribute = mesh.attributes.new(name=cname, type="INT", domain="POINT")
    #attribute_values = [i for i in range(len(mesh.vertices))]
    #attribute.data.foreach_set('1', attribute_values)
    newobj.scale = (.008, -.008, .008)
    newobj.location = (bbox_min[0], -bbox_min[1], bbox_min[2])
    return newobj

def detector_AIO(obj,img_path):

    
    
    # Read floorplan image
    img = cv2.imread(img_path)
    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    height, width, channels = img.shape[:3]
    #height,width,channels = img.shape
    print ("Image size: ", height, width, channels)


    # STEP 1 outer countour
    contourImage = img.copy()
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    contour, c_img = fpb.detect.outer_contours(gray, contourImage, color=(255,0,0))
    print ("Step1: Contour \t>>\t", len(contour))
    # createContourObject(obj,"Step1_OuterContour",contour)
    
    # STEP 2 Walls
    
    wallImage = img.copy()
    wall_img = fpb.detect.wall_filter(gray_image)
    walls,w_img = fpb.detect.precise_boxes(wall_img,wallImage,color=[0,0,255])
    print ("Step2: Walls \t>>\t", len(walls))
    wallObjs = []
    for i, wall in enumerate(walls):
        name = "wall_{:02d}".format(i+1)
        wallobj = createContourObject(obj, name, wall)
        wallObjs.append(wallobj)
    # combine (join) all walls to single obj
    bpy.ops.object.select_all(action='DESELECT')
    for wall in wallObjs:
        wall.select_set(True)
    bpy.context.view_layer.objects.active = wallObjs[0]
    bpy.ops.object.join()
    bpy.ops.object.select_all(action='DESELECT')


    # STEP 3 ROOMS
    # wall_img = fpb.detect.wall_filter(gray_image)
    roomImage = img.copy()
    gray = ~wall_img # inverting colors
    rooms,colored_rooms = fpb.detect.find_rooms(gray)
    gray_rooms = cv2.cvtColor(colored_rooms, cv2.COLOR_BGR2GRAY)
    rooms, roomImage = fpb.detect.precise_boxes(gray_rooms,roomImage,color=(255,0,0))
    print ("Step3: Rooms \t>>\t", len(rooms))
    roomObjs = []
    for i, room in enumerate(rooms):
        name = "room_{:02d}".format(i+1)
        roomobj = createContourObject(obj, name, room)
        roomObjs.append(roomobj)
    # combine (join) all walls to single obj
    bpy.ops.object.select_all(action='DESELECT')
    for room in roomObjs:
        room.select_set(True)
    bpy.context.view_layer.objects.active = roomObjs[0]
    bpy.ops.object.join()
    bpy.ops.object.select_all(action='DESELECT')


    # STEP 4 (DOORS AND WINDOWS)
    
    doon_n_windows = img.copy()
    gray = ~wall_img
    doon_n_windows = img.copy()
    doors, colored_doors = fpb.detect.find_details(gray.copy())
    gray_details = cv2.cvtColor(colored_doors, cv2.COLOR_BGR2GRAY)
    door_window_contourBoxes, doon_n_windows = fpb.detect.precise_boxes(gray_details, doon_n_windows, color=(255, 0, 0))
    print ("Step4: Doors and Windows \t>>\t", len(door_window_contourBoxes))

    # Refine Doors and Windows(separation)
    img0 = cv2.imread(img_path)
    img1 = cv2.imread(img_path,0) # read as grayscale mode
    img2 = cv2.imread(door_path,0)
    doorPatternMatchedList = fpb.find_windows_and_doors.feature_match(img1,img2)
    classified_boxes,door_windowsImage = fpb.find_windows_and_doors.detect_windows_and_doors_boxes(img0,doorPatternMatchedList)
    print ("Step5: Refined \t>>\t", len(classified_boxes))
    for box in classified_boxes:
        print (box["type"],box)
    

class TestFpCvStepsBreakdown(bpy.types.Operator):
    bl_idname = "fpc.testfpcvstepsbreakdown"
    bl_label = "testFpCvStepsBreakdown"

    def execute(self, context):
        o = context.active_object
        if o:
            # get obj materil and texture
            m = o.active_material
            n = m.node_tree.nodes
            tex = n.get('Image Texture')
            img = tex.image
            relpath = img.filepath
            abs_path = bpy.path.abspath(img.filepath)
            # check file exists
            if not os.path.isfile(abs_path):
                print("File path {} does not exist. Exiting...".format(abs_path))
            else:
                print ("File path {} exists.".format(abs_path))
                print("Image")
                directory = os.path.dirname(abs_path)
                # imgpath = bpy.path.abspath (o.data.filepath, start=None, library=None)
                print (abs_path)
                print ("Detecting Outer Contours")
                detect_contour(abs_path)
                print ("Detecting Walls")
                detect_walls(abs_path)
                print ("Detecting Rooms")
                detect_rooms(abs_path)
                print ("Detecting Doors and Windows")
                detect_doorAndWindows(abs_path)
                print ("Detecting Doors Improved")
                detect_doors(abs_path)
                # DETECTION LOGIC ENDS HERE
                ## NEXT GENERATE STORAGE DATA via generate module in fpb

                


        return {'FINISHED'}
# from file.file_handler import FileHandler
# fh = FileHandler()

class GenerateFloorPlanImageOperator(bpy.types.Operator):
    bl_idname = "fpc.generatefloorplanimage"
    bl_label = "generateFloorPlanImage"

    


    def execute(self, context):
        o = context.active_object
        if o:
            m = o.active_material
            n = m.node_tree.nodes
            tex = n.get('Image Texture')
            img = tex.image
            relpath = img.filepath
            abs_path = bpy.path.abspath(img.filepath)
            # check file exists
            if not os.path.isfile(abs_path):
                print ("File path {} does not exist. Exiting...".format(abs_path))
            else:
                # proceeding with file
                # fpb.generate.generate_all_files(abs_path, True)
                # fpb.execution.simple_single(abs_path)
                config_path = None
                f = floorplan.new_floorplan(config_path)
                f.image_path = abs_path
                #data_paths = list()
                #data_paths = [execution.simple_single(f, False)]
                detector_AIO(o,abs_path)

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
    bpy.utils.register_class(TestFpCvStepsBreakdown,GenerateFloorPlanImageOperator)

def unregister():
    bpy.utils.unregister_class(TestFpCvStepsBreakdown,GenerateFloorPlanImageOperator)

if __name__ == "__main__":
    register()