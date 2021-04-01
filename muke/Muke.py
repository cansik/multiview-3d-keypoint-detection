import PIL.Image

import trimesh
import numpy as np

from muke.BaseDetector import BaseDetector


class Muke(object):
    def __init__(self, detector: BaseDetector, resolution: int = 512, display=False):
        self.detector = detector
        self.display = display
        self.resolution = resolution

    def __enter__(self):
        self.detector.setup()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.detector.release()

    def process(self, mesh_path: str, views):
        mesh = trimesh.load(mesh_path)

        # setup scene
        scene = mesh.scene()
        scene.camera.resolution = [self.resolution, self.resolution]
        scene.camera.fov = 50 * (scene.camera.resolution /
                                 scene.camera.resolution.max())

        if self.display:
            scene.show()
