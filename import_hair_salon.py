bl_info = {
  "name": "USC-HairSalon",
  "author": "Shankar Sivarajan",
  "blender": (3,2,0),
  "version": (0, 0, 1),
  "location": "File > Import-Export",
  "description": "Import USC-HairSalon hairstyles",
  "category": "Import-Export",
}

import bpy

import math
from mathutils import Vector

import struct
import array

from pathlib import Path

from bpy_extras.io_utils import ImportHelper

def addStrand(verts, edges, strand_data_xyz):
    
    # add first vertex of strand
    xyz_idx = 0 
    vec =  Vector((strand_data_xyz[xyz_idx], strand_data_xyz[xyz_idx+1], strand_data_xyz[xyz_idx+2]))
    verts.append(vec) 
    
    num_verts_to_add = int(len(strand_data_xyz)/3)
    edge_vidx = len(verts)
    
    for i in range(1, num_verts_to_add):
        xyz_idx += 3
        vec =  Vector((strand_data_xyz[xyz_idx], strand_data_xyz[xyz_idx+1], strand_data_xyz[xyz_idx+2]))
        verts.append(vec) 
        
        edges.append((edge_vidx-1, edge_vidx))
        edge_vidx += 1
        
class ImportHair(bpy.types.Operator, ImportHelper):
    bl_idname = "import_hair_salon.data"
    bl_label = "Import USC-HairSalon hairstyle"
    
    bl_description = "Import USC-HairSalon hairstyle"
    # bl_options = {'UNDO'}
  
    filename_ext = ".data";
  
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
  
    filter_glob: bpy.props.StringProperty(
        default="*.data",
        options={"HIDDEN"},
    )
  
    @classmethod
    def poll(cls, context):
      return True
  
    def execute(self, context):
        
        filename = self.filepath
        name = Path(filename).stem
        
        verts = []
        edges = []
        faces = []

        with open(filename, "rb") as file:

            num_strands = struct.unpack('<i', file.read(4))[0]
            print(f"num_strands = {num_strands}")
            assert num_strands == 10000, f"expected 10000 strands, got {num_strands} strands"
    
            strand_idx = 0
            while (strand_idx < num_strands):
    
                # read num of verts of strand
                strand_idx = strand_idx + 1    
                num_verts = struct.unpack('<i', file.read(4))[0]
                assert num_verts == 1 or num_verts == 100, f"num_verts should be 1 or 100, got: {num_verts}"
                
                # read strand
                strand_data_xyz = array.array('f') 
                strand_data_xyz.fromfile(file, 3 * num_verts) # vert's XYZ corrds
    
                if (num_verts < 2):  # skip empty roots
                    continue
                
                addStrand(verts, edges, strand_data_xyz.tolist())

        print("Data read, creating hairstyle…")

        # create the mesh
        hair_mesh = bpy.data.meshes.new(name)
        hair_mesh.from_pydata(verts, edges, faces)
        hair_mesh.update()

        # create object from mesh
        hair_object = bpy.data.objects.new(name, hair_mesh)
        # get collection
        collection_name = 'USC-HairSalon'
        hair_collection = bpy.data.collections.get(collection_name)
        if hair_collection is None:
            hair_collection = bpy.data.collections.new(collection_name)
            bpy.context.scene.collection.children.link(hair_collection)
        # add object to scene collection
        hair_collection.objects.link(hair_object)

        # fix rotation (90° X-axis)
        hair_object.rotation_euler[0] = math.radians(90)
        #select object & apply rotation
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = hair_object
        hair_object.select_set(True)
        bpy.ops.object.transform_apply(rotation=True)
          
        return {'FINISHED'}
  
    def draw(self, context):
        pass


def menu_import(self, context):
    self.layout.operator(ImportHair.bl_idname, text="USC-HairSalon (.data)")
    
def register():
    bpy.utils.register_class(ImportHair)
    
    bpy.types.TOPBAR_MT_file_import.append(menu_import)

def unregister():
    
    bpy.utils.unregister_class(ImportHair)
    
    bpy.types.TOPBAR_MT_file_import.remove(menu_import)
  
if __name__ == "__main__":
  register()
