import io

import PIL.Image

import trimesh
import numpy as np
from PIL import Image

from detector.BaseDetector import BaseDetector


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

    # todo: define the views input structure [(camera pose, relevant keypoints (weighted?))]
    def detect(self, mesh_path: str, views):
        mesh = trimesh.load(mesh_path)

        # setup scene
        scene = mesh.scene()
        scene.camera.resolution = [self.resolution, self.resolution]
        scene.camera.fov = 50 * (scene.camera.resolution /
                                 scene.camera.resolution.max())

        # could be running multi-processing
        for view in views:
            self._detect_view(scene, view)

            # todo: collect or outputs and use mean or average (see what's better)

        if self.display:
            scene.show()

    def _detect_view(self, scene, view):
        # offscreen render
        data = scene.save_image(resolution=[self.resolution, self.resolution], visible=True)
        png = Image.open(io.BytesIO(data))

        # convert png to rgb image
        image = Image.new("RGB", png.size, (255, 255, 255))
        image.paste(png, mask=png.split()[3])
        image = np.array(image)

        # detect keypoints
        keypoints = self.detector.detect(image)

        # raycast
        for kp in keypoints:
            print(kp.x)

            # todo: raycast each point
            # todo: find corresponding vertex (calculate the delta)
            # todo: return vertex mapping of kp index to vertex id's and delta

