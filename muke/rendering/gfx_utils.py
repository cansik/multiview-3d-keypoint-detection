import numpy as np
import pygfx as gfx
from open3d import geometry
from open3d.visualization import rendering


def open3d_to_gfx_geometry(o3d_mesh: geometry.TriangleMesh) -> gfx.Geometry:
    # create geometry
    triangle_uvs = np.array(o3d_mesh.triangle_uvs, dtype=np.float32)
    triangles = np.array(o3d_mesh.triangles, dtype=np.uint32)

    vertex_normals = np.array(o3d_mesh.vertex_normals, dtype=np.float32)
    vertices = np.array(o3d_mesh.vertices, dtype=np.float32)

    mesh_inputs = {
        "indices": triangles,
        "positions": vertices,
    }

    # remove vertex normals if not there
    if len(vertex_normals) > 0:
        mesh_inputs["normals"] = vertex_normals

    # calculate vertex uvs
    if len(triangle_uvs) > 0:
        vertex_uvs = np.zeros((len(vertices), 2), np.float32)
        vertex_uvs[triangles.flat] = triangle_uvs

        vertex_uvs_wgpu = (vertex_uvs * np.array([1, -1]) + np.array([0, 1])).astype(np.float32)  # uv.y = 1 - uv.y
        mesh_inputs["texcoords"] = vertex_uvs_wgpu

    return gfx.Geometry(**mesh_inputs)


def open3d_to_gfx_material(o3d_material: rendering.MaterialRecord) -> gfx.Material:
    gfx_material = gfx.MeshPhongMaterial()
    gfx_material.flat_shading = False

    if o3d_material.albedo_img is not None:
        gfx_material.map = create_gfx_texture(np.array(o3d_material.albedo_img))

    return gfx_material


def gfx_material_from_mesh(o3d_mesh: geometry.TriangleMesh) -> gfx.Material:
    gfx_material = gfx.MeshPhongMaterial()
    gfx_material.flat_shading = False

    if o3d_mesh.has_textures():
        flipped_texture = np.array(o3d_mesh.textures[0])[::-1, :, :]
        gfx_material.map = create_gfx_texture(flipped_texture)

    # vertex_colors = np.array(o3d_mesh.vertex_colors, dtype=np.float32)

    return gfx_material


def create_gfx_texture(image: np.ndarray) -> gfx.Texture:
    texture = image
    return gfx.Texture(texture, dim=2, format="3xu1")
