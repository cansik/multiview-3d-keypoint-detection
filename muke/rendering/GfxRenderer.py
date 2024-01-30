from typing import Optional

import numpy as np
import pygfx as gfx
import pylinalg as la
from open3d.cpu.pybind import geometry
from open3d.cpu.pybind.visualization import rendering
from wgpu.gui.offscreen import WgpuCanvas

from muke.model.DetectionView import DetectionView
from muke.rendering.BaseRenderer import BaseRenderer


class GfxRenderer(BaseRenderer):

    def __init__(self, width: int, height: int):
        super().__init__(width, height)

        # setup canvas and scene
        self.canvas = WgpuCanvas(size=(self.width, self.height), pixel_ratio=1)
        self.renderer = gfx.renderers.WgpuRenderer(self.canvas)
        self.scene = gfx.Scene()

        # setup camera
        self.camera = gfx.OrthographicCamera(4)

        # setup handler for rendering
        self.canvas.request_draw(lambda: self.renderer.render(self.scene, self.camera))

    def add_geometry(self, mesh: geometry.TriangleMesh, material: Optional[rendering.MaterialRecord]):
        gfx_mesh = self._open3d_to_gfx_geometry(mesh)
        material = gfx.MeshBasicMaterial()
        cube = gfx.Mesh(gfx_mesh, material)
        self.scene.add(cube)

        camera = gfx.OrthographicCamera(400)
        camera.local.z = 400

        rot = la.quat_from_euler((0.5, 1.0), order="XY")
        cube.local.rotation = la.quat_mul(rot, cube.local.rotation)

    def render(self, view: DetectionView) -> np.ndarray:
        return np.asarray(self.canvas.draw())

    @staticmethod
    def _open3d_to_gfx_geometry(o3d_mesh: geometry.TriangleMesh) -> gfx.Geometry:
        geo = gfx.box_geometry(200, 200, 200)

        triangle_material_ids = np.array(o3d_mesh.triangle_material_ids)
        triangle_normals = np.array(o3d_mesh.triangle_normals)
        triangle_uvs = np.array(o3d_mesh.triangle_uvs, dtype=np.float32)
        triangles = np.array(o3d_mesh.triangles, dtype=np.uint32)

        vertex_colors = np.array(o3d_mesh.vertex_colors, dtype=np.float32)
        vertex_normals = np.array(o3d_mesh.vertex_normals, dtype=np.float32)
        vertices = np.array(o3d_mesh.vertices, dtype=np.float32)

        return gfx.Geometry(
            indices=triangles, positions=vertices, normals=vertex_normals, texcoords=triangle_uvs
        )
