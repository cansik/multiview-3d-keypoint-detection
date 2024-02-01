import logging
import math
import tempfile
from pathlib import Path
from typing import Optional, Sequence

import cv2
import numpy as np
import pygfx as gfx
import pylinalg as la
import trimesh
from open3d import geometry
from open3d import io
from open3d.visualization import rendering
from trimesh import Trimesh
from wgpu.gui import WgpuCanvasBase
from wgpu.gui.offscreen import WgpuCanvas

from muke.model.Vertex import Vertex
from muke.rendering.BaseRenderer import BaseRenderer


class GfxRenderer(BaseRenderer):

    def __init__(self, width: int, height: int,
                 lights: bool = True, background_color: Optional[Sequence[float]] = None,
                 canvas: Optional[WgpuCanvasBase] = None):
        super().__init__(width, height)

        # setup canvas and scene
        if canvas is None:
            self.canvas = WgpuCanvas(size=(self.width, self.height), pixel_ratio=1)
        else:
            self.canvas = canvas
        self.renderer = gfx.renderers.WgpuRenderer(self.canvas)
        self.scene = gfx.Scene()

        # setup lights
        if lights:
            self._setup_light()

        # add background
        if background_color is not None:
            color = np.array(background_color, np.float32)
            self._setup_background(color)

        # setup camera
        self.camera = gfx.OrthographicCamera(1.1)

        # mesh
        self._gfx_mesh: Optional[gfx.Mesh] = None

        # setup handler for rendering
        self.canvas.request_draw(lambda: self.renderer.render(self.scene, self.camera))

    def add_geometry(self, mesh: geometry.TriangleMesh, material: Optional[rendering.MaterialRecord]):
        gfx_geometry = self._open3d_to_gfx_geometry(mesh)

        if material is not None:
            gfx_material = self._open3d_to_gfx_material(material)
        else:
            gfx_material = gfx.MeshBasicMaterial()

        self._gfx_mesh = gfx.Mesh(gfx_geometry, gfx_material)

        # scale mesh to fill rendering
        bbox = np.array(self._gfx_mesh.get_world_bounding_box(), np.float32)
        size = np.abs(bbox[1] - bbox[0])
        up_scale_ratio = 1 / float(np.max(size))
        self._gfx_mesh.local.scale = np.array(np.full((3,), up_scale_ratio))

        self.scene.add(self._gfx_mesh)

    def render(self) -> np.ndarray:
        self.canvas.request_draw(lambda: self.renderer.render(self.scene, self.camera))

        image_rgba = np.asarray(self.canvas.draw())
        return cv2.cvtColor(image_rgba, cv2.COLOR_BGRA2BGR)

    def rotate_scene(self, x: float, y: float, z: float):
        rot = la.quat_from_euler((math.radians(x), math.radians(y), math.radians(z)), order="XYZ")
        self._gfx_mesh.local.rotation = la.quat_mul(rot, self._gfx_mesh.local.rotation)

    def cast_ray(self, x: float, y: float) -> Optional[Vertex]:
        u = x * self.width
        v = y * self.height
        info = self.renderer.get_pick_info((u, v))

        wobject = info["world_object"]

        if wobject is None:
            return None

        # lookup hit vertex
        coords = info["face_coord"]
        face_index = info["face_index"]

        sub_index = np.argmax(coords)

        # todo: filter point picked which are not on mesh
        # maybe use info["rgba"] to detect background color

        vertex_index = int(wobject.geometry.indices.data[face_index][sub_index])
        pos = wobject.geometry.positions.data[vertex_index]

        return Vertex(vertex_index, *pos)

    def _setup_light(self):
        light = gfx.DirectionalLight(gfx.Color("#ffffff"), 1)
        light.local.x = 0.5
        light.local.y = 0.5
        light.local.z = 1.1
        self.scene.add(light)

        light = gfx.DirectionalLight(gfx.Color("#ffffff"), 1)
        light.local.x = -0.5
        light.local.y = 0.5
        light.local.z = 1.1
        self.scene.add(light)

        self.scene.add(gfx.AmbientLight(gfx.Color("#ffffff"), 0.2))

    def _setup_background(self, background_color: np.ndarray):
        # todo use: background = gfx.Background(None, gfx.BackgroundMaterial(light_gray, dark_gray))
        geo = gfx.plane_geometry(5, 5, 12, 12)
        material = gfx.MeshBasicMaterial(color=gfx.Color(background_color))
        plane = gfx.Mesh(geo, material)
        plane.local.z = -3
        self.scene.add(plane)

    @staticmethod
    def _open3d_to_gfx_geometry(o3d_mesh: geometry.TriangleMesh) -> gfx.Geometry:
        # workaround with trimesh
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file_name = Path(temp_dir).joinpath("tmp.obj")
            io.write_triangle_mesh(str(temp_file_name), o3d_mesh)
            t_mesh: Trimesh = trimesh.load_mesh(str(temp_file_name))
            t_geo = gfx.geometry_from_trimesh(t_mesh)
            return t_geo

        # todo: implement mesh loading with correct indices of indexes
        triangle_uvs = np.array(o3d_mesh.triangle_uvs, dtype=np.float32)
        triangles = np.array(o3d_mesh.triangles, dtype=np.uint32)
        # triangle_normals = np.array(o3d_mesh.triangle_normals, dtype=np.float32)

        vertex_normals = np.array(o3d_mesh.vertex_normals, dtype=np.float32)
        # vertex_colors = np.array(o3d_mesh.vertex_colors, dtype=np.float32)
        vertices = np.array(o3d_mesh.vertices, dtype=np.float32)

        # fix triangle uvs
        # triangles = triangles[:, ::-1]
        # triangle_uvs = triangle_uvs.reshape((-1, 3, 2))
        # triangle_uvs = triangle_uvs[:, ::-1, :]
        # triangle_uvs = np.roll(triangle_uvs, 2, axis=1)

        new_order = [1, 0, 2]
        # triangle_uvs = triangle_uvs[:, new_order, :]

        # triangle_uvs = triangle_uvs.reshape(-1, 2)

        triangle_uvs_wgpu = (triangle_uvs * np.array([1, -1]) + np.array([0, 1])).astype(np.float32)  # uv.y = 1 - uv.y

        return gfx.Geometry(
            indices=triangles, positions=vertices, normals=vertex_normals, texcoords=triangle_uvs_wgpu
        )

    @staticmethod
    def _open3d_to_gfx_material(o3d_material: rendering.MaterialRecord) -> gfx.Material:
        gfx_material = gfx.MeshPhongMaterial()
        gfx_material.flat_shading = False

        if o3d_material.albedo_img is not None:
            texture = np.array(o3d_material.albedo_img)

            logging.info(f"texture input format: {texture.shape} ({texture.dtype})")

            # texture = texture[::-1, :, :]  # flip texture vertically
            # texture = texture.astype(np.float32) / 255.0

            # todo: fix texture rendering
            # format=wgpu.TextureFormat.
            tex = gfx.Texture(texture, dim=2, format="3xu1")
            gfx_material.map_interpolation = "linear"
            gfx_material.side = "FRONT"
            gfx_material.map = tex

        return gfx_material
