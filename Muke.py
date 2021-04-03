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
            self._detect_view(scene, mesh, view)

            # todo: collect or outputs and use mean or average (see what's better)

        if self.display:
            scene.show()

    def _detect_view(self, scene, mesh, view: DetectionView):
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
            self._annotate_keypoints_2d(image, keypoints)
            image.show("%s: Key Points" % view.name)

        # get camera rays
        origins, vectors, pixels = scene.camera_rays()

        # find relevant indexes
        kp_indexes = []
        for kp in keypoints:
            # todo: filter indexes which are in view!
            x, y = self._get_transformed_coordinates(kp)
            pixel_index = self._get_pixel_index(x, y)
            kp_indexes.append(pixel_index)

        # raycast
        origins = origins[kp_indexes]
        vectors = vectors[kp_indexes]
        pixels = pixels[kp_indexes]

        print("raytracing...")
        # do the actual ray- mesh queries
        points, index_ray, index_tri = mesh.ray.intersects_location(
            origins, vectors, multiple_hits=False)

        print(len(points))

        # debug
        if self.display:
            self._annotate_keypoints_3d(scene, points)

        # todo: raycast each point
        # todo: find corresponding vertex (calculate the delta)
        # todo: return vertex mapping of kp index to vertex id's and delta

    def _get_pixel_index(self, x: int, y: int) -> int:
        return self.height * x + y

    def _get_transformed_coordinates(self, keypoint: [KeyPoint]) -> (int, int):
        return round(keypoint.x * self.width), round(keypoint.y * self.height)

    @staticmethod
    def _annotate_keypoints_3d(scene, points, size: float = 0.02):
        for point in points:
            mat = trimesh.transformations.compose_matrix(translate=point)
            marker = trimesh.creation.box([size, size, size], mat)
            marker.visual.face_colors = [0, 255, 0]
            scene.add_geometry(marker)

    def _annotate_keypoints_2d(self, image: Image, keypoints: [KeyPoint], size: int = 5):
        hf = size * 0.5
        draw = ImageDraw.Draw(image)
        for kp in keypoints:
            x, y = self._get_transformed_coordinates(kp)
            draw.ellipse([x - hf, y - hf, x + hf, y + hf], outline=(0, 255, 0), width=2)
            draw.text((x + hf, y + hf), "%d" % kp.index, fill=(0, 255, 0))
