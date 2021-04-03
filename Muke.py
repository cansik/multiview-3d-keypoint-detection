import io

import trimesh
import numpy as np
from PIL import Image, ImageDraw

from detector.BaseDetector import BaseDetector
from detector.KeyPoint import KeyPoint
from lib.DetectionView import DetectionView


class Muke(object):
    def __init__(self, detector: BaseDetector, resolution: int = 512, display=False):
        self.detector = detector
        self.display = display
        self.width = resolution
        self.height = resolution

    def __enter__(self):
        self.detector.setup()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.detector.release()

    # todo: define the views input structure [(camera pose, relevant keypoints (weighted?))]
    def detect(self, mesh_path: str, views: [DetectionView]):
        mesh = trimesh.load(mesh_path)

        # setup scene
        scene = mesh.scene()
        scene.camera.resolution = [self.height, self.width]
        scene.camera.fov = 50 * (scene.camera.resolution /
                                 scene.camera.resolution.max())

        # could be running multi-processing
        for view in views:
            self._detect_view(scene, view)

            # todo: collect or outputs and use mean or average (see what's better)

        if self.display:
            scene.show()

    def _detect_view(self, scene, view: DetectionView):
        # offscreen renders
        data = scene.save_image(visible=True)
        png = Image.open(io.BytesIO(data))

        # convert png to rgb image
        image = Image.new("RGB", png.size, (255, 255, 255))
        image.paste(png, mask=png.split()[3])
        image_np = np.array(image)

        # detect keypoints
        keypoints = self.detector.detect(image_np)

        # annotate
        if self.display:
            self._annotate(image, keypoints)
            image.show("%s: Key Points" % view.name)

        # get camera rays
        origins, vectors, pixels = scene.camera_rays()

        # raycast
        for kp in keypoints:
            x, y = self._get_transformed_coordinates(kp)
            pixel_index = self._get_pixel_index(x, y)

            print(kp.x)

            # todo: raycast each point
            # todo: find corresponding vertex (calculate the delta)
            # todo: return vertex mapping of kp index to vertex id's and delta

    def _get_pixel_index(self, x: int, y: int) -> int:
        return self.height * y + ((self.width - 1) - x)

    def _get_transformed_coordinates(self, keypoint: [KeyPoint]) -> (int, int):
        return round(keypoint.x * self.width), round(keypoint.y * self.height)

    def _annotate(self, image: Image, keypoints: [KeyPoint], size: int = 5):
        hf = size * 0.5
        draw = ImageDraw.Draw(image)
        for kp in keypoints:
            x, y = self._get_transformed_coordinates(kp)
            draw.ellipse([x - hf, y - hf, x + hf, y + hf], outline=(0, 255, 0), width=2)
            draw.text((x + hf, y + hf), "%d" % kp.index, fill=(0, 255, 0))
