import io
from math import radians

import trimesh
import numpy as np
from PIL import Image, ImageDraw

from detector.BaseDetector import BaseDetector
from detector.KeyPoint2 import KeyPoint2
from model.DetectionView import DetectionView
from model.KeyPoint3 import KeyPoint3


class Muke(object):
    def __init__(self, detector: BaseDetector, resolution: int = 512, display=False, debug=False):
        self.detector = detector

        self.display = display
        self.debug = debug

        self.width = resolution
        self.height = resolution
        self.pixel_density = 1.0
        self.camera_distance = 1.2

    def __enter__(self):
        self.detector.setup()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.detector.release()

    def detect(self, mesh_path: str, views: [DetectionView]) -> [KeyPoint3]:
        mesh = trimesh.load(mesh_path)

        # setup scene
        scene = mesh.scene()
        scene.camera.resolution = [self.height, self.width]
        scene.camera.fov = 50 * (scene.camera.resolution /
                                 scene.camera.resolution.max())

        # could be running multi-processing
        detections = {}
        for view in views:
            keypoints = self._detect_view(scene, mesh, view)

            # add keypoints to dictionary
            for kp in keypoints:
                if kp.index not in detections:
                    detections[kp.index] = []
                detections[kp.index].append(kp)

        # combine detections
        query = trimesh.proximity.ProximityQuery(mesh)
        keypoints = []
        summed_error = 0.0
        for index in sorted(detections.keys()):
            positions = np.array([[i.x, i.y, i.z] for i in detections[index]])
            # todo: check if mean or median
            mean_position = np.mean(positions, axis=0)

            # find corresponding vertex (and calculate the delta to it)
            delta, vertex_index = query.vertex(mean_position)
            vertex = mesh.vertices[vertex_index]
            # todo: find uv coordinate
            keypoints.append(KeyPoint3(index, vertex[0], vertex[1], vertex[2], vertex_index, delta))
            summed_error += delta

            if self.debug:
                print("[%02d]:\t%d\t(error: %.4f)" % (index, vertex_index, delta))

        print("estimated %d key-points (error total: %.4f avg: %.4f)"
              % (len(keypoints), summed_error, summed_error / max(1.0, len(keypoints))))

        if self.display:
            # reset view
            self._set_scene_rotation(scene, mesh, 0)
            self._annotate_keypoints_3d(scene, mesh, keypoints)
            scene.show()

        return keypoints

    def _detect_view(self, scene, mesh, view: DetectionView) -> [KeyPoint3]:
        # apply view state
        self._set_scene_rotation(scene, mesh, view.rotation)

        # offscreen renders
        data = scene.save_image(resolution=[self.width, self.height], visible=True)
        png = Image.open(io.BytesIO(data))

        # convert png to rgb image
        image = Image.new("RGB", png.size, (255, 255, 255))
        image.paste(png, mask=png.split()[3])

        # set pixel density if necessary
        # warning: changes state (no concurrency)
        self.pixel_density = image.width / self.width

        # PIL image to numpy
        image_np = np.array(image)

        # detect keypoints
        keypoints = self.detector.detect(image_np)

        # filter keypoints
        if view.keypoints is not None:
            keypoints = list(filter(lambda kp: kp.index in view.keypoints, keypoints))

        # annotate if debug is on
        if self.debug:
            self._annotate_keypoints_2d(image, keypoints)
            image.show("%s: Key Points" % view.name)

        # get camera rays
        origins, vectors, pixels = scene.camera_rays()

        # find relevant indexes
        kp_pixel_indexes = []
        for kp in keypoints:
            # todo: filter indexes which are in view!
            x, y = self._get_transformed_coordinates(kp)
            pixel_index = self._get_pixel_index(x, y)
            kp_pixel_indexes.append(pixel_index)

        # raycast each keypoint
        origins = origins[kp_pixel_indexes]
        vectors = vectors[kp_pixel_indexes]
        pixels = pixels[kp_pixel_indexes]

        # do the actual ray-mesh queries
        points, index_ray, index_tri = mesh.ray.intersects_location(
            origins, vectors, multiple_hits=False)

        # create result keypoints 3d
        result = []
        for i, kp in enumerate(keypoints):
            position = points[i]
            result.append(KeyPoint3(kp.index, position[0], position[1], position[2]))

        # annotate 3d keypoints
        if self.debug:
            self._annotate_keypoints_3d(scene, mesh, result, color=(255, 0, 0))

        return result

    def _set_scene_rotation(self, scene, mesh, angle):
        scene.camera_transform = scene.camera.look_at(
            points=mesh.vertices,
            distance=max(mesh.bounding_box.primitive.extents) * self.camera_distance,
            rotation=trimesh.transformations.euler_matrix(0, radians(angle), 0))

    def _get_pixel_index(self, x: int, y: int) -> int:
        return round(self._get_render_height() * x + y)

    def _get_transformed_coordinates(self, keypoint: [KeyPoint2]) -> (int, int):
        return round(keypoint.x * self._get_render_width()), \
               round(keypoint.y * self._get_render_height())

    def _get_render_width(self):
        return self.width * self.pixel_density

    def _get_render_height(self):
        return self.width * self.pixel_density

    @staticmethod
    def _annotate_keypoints_3d(scene, mesh, keypoints: [KeyPoint3], size: float = 0.01, color=(0, 255, 0)):
        # calculate size
        bb = mesh.bounding_box.primitive.extents
        box_size = max(bb) * size

        for kp in keypoints:
            mat = trimesh.transformations.compose_matrix(translate=[kp.x, kp.y, kp.z])
            marker = trimesh.creation.box([box_size, box_size, box_size], mat)
            marker.visual.face_colors = color
            scene.add_geometry(marker)

    def _annotate_keypoints_2d(self, image: Image, keypoints: [KeyPoint2], size: int = 5, color=(0, 255, 0)):
        hf = size * 0.5
        draw = ImageDraw.Draw(image)
        for kp in keypoints:
            x, y = self._get_transformed_coordinates(kp)
            draw.ellipse([x - hf, y - hf, x + hf, y + hf], outline=color, width=2)
            draw.text((x + hf, y + hf), "%d" % kp.index, fill=color)
