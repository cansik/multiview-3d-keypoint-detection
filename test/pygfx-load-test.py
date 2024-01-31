import numpy as np
import open3d
import pygfx as gfx
import trimesh
from open3d.cpu.pybind import geometry
from open3d.cpu.pybind.visualization import rendering
from trimesh import Trimesh

from muke.rendering.GfxRenderer import GfxRenderer

t_mesh: Trimesh = trimesh.load_mesh("assets/woman-old2-small/woman-old2.obj", process=False)

model: rendering.TriangleMeshModel = open3d.io.read_triangle_model("assets/woman-old2-small/woman-old2.obj")
mesh_info: rendering.TriangleMeshModel.MeshInfo = model.meshes[0]
o3d_mesh: geometry.TriangleMesh = mesh_info.mesh
material = model.materials[mesh_info.material_idx]

o3d_mesh = open3d.io.read_triangle_mesh("assets/woman-old2-small/woman-old2.obj", enable_post_processing=False)

t_geo = gfx.geometry_from_trimesh(t_mesh)
o3d_geo = GfxRenderer._open3d_to_gfx_geometry(o3d_mesh)


def is_same(attribute: str):
    t_data = getattr(t_geo, attribute).data
    o3d_data = getattr(o3d_geo, attribute).data

    t_data_sorted = np.sort(t_data, 0)
    o3d_data_sorted = np.sort(o3d_data, 0)

    if not np.array_equal(t_data, o3d_data):
        print(f"Attribute {attribute} is not equal!")

    if not np.array_equal(t_data_sorted, o3d_data_sorted):
        print(f"Sorted Attribute {attribute} is not equal!")


is_same("indices")
is_same("positions")
is_same("normals")
is_same("texcoords")

# wgpu_uv = mesh.visual.uv * np.array([1, -1]) + np.array([0, 1])  # uv.y = 1 - uv.y

print("done")
