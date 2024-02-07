import numpy as np
import pygfx as gfx
from open3d import geometry
from open3d.visualization import rendering


def open3d_to_gfx_geometry(o3d_mesh: geometry.TriangleMesh) -> gfx.Geometry:
    # create geometry
    triangle_uvs = np.array(o3d_mesh.triangle_uvs, dtype=np.float32)
    triangles = np.array(o3d_mesh.triangles, dtype=np.uint32)

    vertex_normals = np.array(o3d_mesh.vertex_normals, dtype=np.float32)
    # vertex_colors = np.array(o3d_mesh.vertex_colors, dtype=np.float32)
    vertices = np.array(o3d_mesh.vertices, dtype=np.float32)

    vertex_uvs = np.zeros((len(vertices), 2), np.float32)
    vertex_uvs[triangles.flat] = triangle_uvs

    vertex_uvs_wgpu = (vertex_uvs * np.array([1, -1]) + np.array([0, 1])).astype(np.float32)  # uv.y = 1 - uv.y

    return gfx.Geometry(indices=triangles, positions=vertices,
                        normals=vertex_normals, texcoords=vertex_uvs_wgpu)


def open3d_to_gfx_material(o3d_material: rendering.MaterialRecord) -> gfx.Material:
    gfx_material = gfx.MeshPhongMaterial()
    gfx_material.flat_shading = False

    if o3d_material.albedo_img is not None:
        texture = np.array(o3d_material.albedo_img).astype("float32") / 255
        tex = gfx.Texture(texture, dim=2)
        gfx_material.map_interpolation = "linear"
        gfx_material.side = "FRONT"
        gfx_material.map = tex

    return gfx_material
