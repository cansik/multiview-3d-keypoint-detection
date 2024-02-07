import math
from typing import Optional, Sequence

import cv2
import numpy as np
import pygfx as gfx
import pylinalg as la
from open3d import geometry
from open3d.visualization import rendering
from wgpu.gui import WgpuCanvasBase
from wgpu.gui.offscreen import WgpuCanvas

from muke.model.Vertex import Vertex
from muke.rendering import gfx_utils
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
        gfx_geometry = gfx_utils.open3d_to_gfx_geometry(mesh)

        if material is not None:
            gfx_material = gfx_utils.open3d_to_gfx_material(material)
        else:
            gfx_material = gfx_utils.gfx_material_from_mesh(mesh)

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
