# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import bpy
from bpy import context as context

from . fpc import state
from . fpc import TestFpCvStepsBreakdown, GenerateFloorPlanImageOperator, FpcPropGrp

bl_info = {
    "name" : "FloorPlanCreator",
    "author" : "haseeb",
    "description" : "floor plan 3d mesh generator",
    "blender" : (3, 50, 0),
    "version" : (0, 0, 1),
    "location" : "View3D",
    "warning" : "",
    "category" : "Generic"
}




# SPECIAL LINE
bpy.types.Scene.ff_FPC_prop_grp = bpy.props.PointerProperty(type=FpcPropGrp)

# MAIN PANEL CONTROL
class FPC_PT_Panel(bpy.types.Panel):
    bl_idname = "FPC_PT_Panel"
    bl_label = "FloorPlanCreator"
    bl_category = "FF_Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    def draw(self,context):
        layout = self.layout
        s = state()
        # Modeling
        box_rg = layout.box()
        col = box_rg.column(align = True)
        col.label(text='Floor Plan Options')
        row = col.row(align = True)
        row.operator("fpc.testfpcvstepsbreakdown", text="Test FP CV Steps")
        row = col.row(align = True)
        row.operator("fpc.generatefloorplanimage", text="Generate Floor Plan")
        # row.operator("ffgen.re_mirror", text="Re-Mirror ")
        


classes = (
        TestFpCvStepsBreakdown,
        GenerateFloorPlanImageOperator,
        FPC_PT_Panel)
register,unregister = bpy.utils.register_classes_factory(classes)

# from . import auto_load

# auto_load.init()



# def register():
#     auto_load.register()

# def unregister():
#     auto_load.unregister()
