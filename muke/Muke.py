import logging
from typing import List, Sequence, Optional

import cv2
import numpy as np
import open3d as o3d
from open3d.visualization import rendering
from scipy.spatial import distance

from muke.Lines import Lines
from muke.detector.BaseDetector import BaseDetector
from muke.detector.KeyPoint2 import KeyPoint2
from muke.model.DetectionView import DetectionView
from muke.model.KeyPoint3 import KeyPoint3
from muke.rendering.BaseRenderer import BaseRenderer
from muke.rendering.GfxRenderer import GfxRenderer


class Muke:
    def __init__(self, detector: BaseDetector, resolution: int = 512, display=False, debug=False):
        self.detector: BaseDetector = detector

        self.display: bool = display
        self.debug: bool = debug

        self.width: int = resolution
        self.height: int = resolution
        self.pixel_density: float = 1.0

        self.ray_size: float = 5

        self.camera_zoom: float = 0.55
        self.camera_fov: float = -90  # by default orthographic

        # background color r, g, b [0-1]
        self.background_color: Sequence[float] = [1, 1, 1]

        self.mesh_shade_option: Optional[o3d.visualization.MeshShadeOption] = None
        self.mesh_color_option: Optional[o3d.visualization.MeshColorOption] = None
        self.light_on: bool = True

    def __enter__(self):
        self.detector.setup()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.detector.release()

    def detect_file(self, mesh_path: str, views: List[DetectionView],
                    post_processing: bool = True) -> List[KeyPoint3]:
        model: rendering.TriangleMeshModel = o3d.io.read_triangle_model(mesh_path)

        mesh_info: rendering.TriangleMeshModel.MeshInfo = model.meshes[0]
        mesh = mesh_info.mesh
        material = model.materials[mesh_info.material_idx]

        if post_processing:
            # check if mesh has colors or triangle normals -> otherwise calculate them
            if not mesh.has_triangle_normals() and not mesh.has_vertex_colors() and not mesh.has_textures():
                mesh.compute_triangle_normals()

        return self.detect(mesh, views, material=material)

    def detect(self, mesh: o3d.geometry.TriangleMesh,
               views: List[DetectionView],
               material: Optional[rendering.MaterialRecord] = None) -> List[KeyPoint3]:

        # setup renderer
        # todo: make this configurable
        renderer: BaseRenderer = GfxRenderer(self.width, self.height,
                                             self.light_on, self.background_color)
        renderer.add_geometry(mesh, material)

        # detect keypoints
        detections = {}

        # render
        for view in views:
            keypoints = self._detect_view(renderer, mesh, view)

            # add keypoints to dictionary
            for kp in keypoints:
                if kp.index not in detections:
                    detections[kp.index] = []
                detections[kp.index].append(kp)

        # setup raycasting scene
        t_mesh = o3d.t.geometry.TriangleMesh.from_legacy(mesh)
        scene = o3d.t.geometry.RaycastingScene()
        scene.add_triangles(t_mesh)

        # combine detections and select closest vertex
        keypoints = []
        summed_error = 0.0
        for index in sorted(detections.keys()):
            positions = np.array([[i.x, i.y, i.z] for i in detections[index]])
            mean_position = np.mean(positions, axis=0)

            # find corresponding vertex (and calculate the delta to it)
            query_point = o3d.core.Tensor([mean_position], dtype=o3d.core.Dtype.Float32)
            result = scene.compute_closest_points(query_point)

            # get first point of results
            position = result["points"].numpy()[0]
            vertex_index = result["primitive_ids"].numpy()[0]
            delta = distance.euclidean(mean_position, position)

            # todo: find uv coordinate
            keypoints.append(KeyPoint3(index, float(position[0]), float(position[1]), float(position[2]),
                                       vertex_index, delta, mean_position))
            summed_error += delta

            if self.debug:
                logging.info("[%02d]:\t%d\t(error: %.4f)" % (index, vertex_index, delta))

        logging.debug("estimated %d key-points (error total: %.4f avg: %.4f)"
                      % (len(keypoints), summed_error, summed_error / max(1.0, len(keypoints))))

        if self.display:
            self._annotate_keypoints_3d("Result", mesh, keypoints)

        return keypoints

    def _detect_view(self, renderer: BaseRenderer,
                     mesh: o3d.geometry.TriangleMesh,
                     view: DetectionView) -> List[KeyPoint3]:
        # apply view state
        renderer.rotate_scene(0, view.rotation, 0)

        # render
        image_np = renderer.render()

        # detect keypoints
        keypoints = self.detector.detect(image_np)

        # filter keypoints
        if view.keypoints is not None:
            keypoints = list(filter(lambda kp: kp.index in view.keypoints, keypoints))

        # annotate if debug is on
        if self.debug:
            preview_image = image_np.copy()
            preview_image = cv2.cvtColor(preview_image, cv2.COLOR_RGB2BGR)
            clean_image = preview_image.copy()
            self._annotate_keypoints_2d(preview_image, keypoints, weight=2, color=(0, 0, 255))
            combined = np.hstack((clean_image, preview_image))
            cv2.imshow(f"{view.name}: 2D Key Points", combined)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        # raycast from camera
        vertices = np.asarray(mesh.vertices)
        result = []

        for kp in keypoints:
            picked_vertex = renderer.cast_ray(kp.x, kp.y)

            if picked_vertex is None:
                continue

            result.append(KeyPoint3(kp.index, picked_vertex.x, picked_vertex.y, picked_vertex.z,
                                    vertex_index=picked_vertex.index))

        # reset view state
        renderer.rotate_scene(0, -view.rotation, 0)

        # render picked points
        if self.debug:
            meshes = []
            for p in result:
                sphere: o3d.geometry.TriangleMesh = o3d.geometry.TriangleMesh.create_sphere(radius=0.01)
                sphere.paint_uniform_color((0, 1, 0))
                sphere.translate((p.x, p.y, p.z))
                meshes.append(sphere)
            o3d.visualization.draw_geometries([mesh, *meshes], window_name="Picked Points")

        # raycast scene from backside if infinity ray is activated
        if view.infinite_ray:
            mesh_dimensions = mesh.get_max_bound() - mesh.get_min_bound()
            max_z = mesh_dimensions[2]

            # create rays (from back to front)
            rays = [[kp.x, kp.y, kp.z - max_z, 0.0, 0.0, max_z] for kp in result]

            # render test rays
            def render_rays():
                lines = Lines()
                for i, ray in enumerate(rays):
                    lines.add_line(ray[:3], [ray[0] + ray[3], ray[1] + ray[4], ray[2] + ray[5]])
                o3d.visualization.draw_geometries([mesh, lines.create_line_set()], window_name="Rays")

            if self.debug:
                render_rays()

            # shoot rays
            t_mesh = o3d.t.geometry.TriangleMesh.from_legacy(mesh)
            scene = o3d.t.geometry.RaycastingScene()
            scene.add_triangles(t_mesh)
            ans = scene.cast_rays(o3d.core.Tensor(rays, dtype=o3d.core.Dtype.Float32))

            hit_triangles = ans["primitive_ids"].numpy()
            hit_uvs = ans["primitive_uvs"].numpy()
            triangles = np.asarray(mesh.triangles)

            bad_index = pow(2, 32) - 1  # 4294967295
            bad_keypoint_ids = []  # keypoints to remove because they do not hit any triangle

            back_positions = []
            for i in range(len(hit_triangles)):
                triangle_index = hit_triangles[i]

                if triangle_index == bad_index:
                    bad_keypoint_ids.append(i)
                    continue

                triangle = triangles[hit_triangles[i]]
                barycenter = np.average(np.take(vertices, triangle, axis=0), axis=0)
                # todo: add hit uv's (but how is it rotated?)
                back_positions.append(barycenter)

            # remove bad keypoints
            for i in bad_keypoint_ids[::-1]:
                result.pop(i)

            # calculate new mean positions
            lines = Lines()
            markers = []
            for i, kp in enumerate(result):
                front_position = np.array([kp.x, kp.y, kp.z], dtype=float)
                back_position = back_positions[i]

                markers.append([front_position, back_position])
                lines.add_line(front_position, back_position)

                average_position = np.average(np.stack([front_position, back_position]), axis=0)

                kp.x = float(average_position[0])
                kp.y = float(average_position[1])
                kp.z = float(average_position[2])

            meshes = [o3d.geometry.LineSet.create_from_triangle_mesh(mesh), lines.create_line_set()]
            for ms in markers:
                color = (255, 0, 0)
                for i, m in enumerate(ms):
                    marker: o3d.geometry.TriangleMesh = o3d.geometry.TriangleMesh.create_sphere(radius=0.01,
                                                                                                resolution=5)
                    marker.translate(m)
                    marker.paint_uniform_color(np.array(list(color)) / 255.0)
                    meshes.append(marker)
                    color = (0, 0, 255)

            if self.debug:
                o3d.visualization.draw_geometries(meshes, window_name="Point Pairs")

        # annotate 3d keypoints
        if self.debug:
            pass
            # key-point annotation has to be done in a separate glwindow
            # self._annotate_keypoints_3d(f"{view.name}: 3D Key Points", mesh, result, color=(255, 0, 0))

        return result

    @staticmethod
    def _set_scene_rotation(vis: o3d.visualization.VisualizerWithVertexSelection, angle_x: float):
        ctr: o3d.visualization.ViewControl = vis.get_view_control()
        ctr.rotate(2000.0 / 360.0 * angle_x, 0)
        vis.poll_events()
        vis.update_renderer()

    def _get_pixel_index(self, x: int, y: int) -> int:
        return round(self._get_render_height() * x + y)

    def _get_transformed_coordinates(self, keypoint: [KeyPoint2]) -> (int, int):
        return round(keypoint.x * self._get_render_width()), \
            round(keypoint.y * self._get_render_height())

    def _get_render_width(self):
        return self.width * self.pixel_density

    def _get_render_height(self):
        return self.width * self.pixel_density

    def _annotate_keypoints_3d(self, title: str, mesh: o3d.geometry.TriangleMesh, keypoints: [KeyPoint3],
                               size: float = 0.005, color=(0, 255, 0)):
        # calculate size
        bb: o3d.geometry.AxisAlignedBoundingBox = mesh.get_axis_aligned_bounding_box()
        bb_size = bb.get_max_bound() - bb.get_min_bound()
        box_size = max(bb_size) * size

        meshes = [mesh]
        for kp in keypoints:
            marker: o3d.geometry.TriangleMesh = o3d.geometry.TriangleMesh.create_sphere(radius=box_size, resolution=5)
            marker.translate(np.array([kp.x, kp.y, kp.z]))
            marker.paint_uniform_color(np.array(list(color)) / 255.0)
            meshes.append(marker)

        o3d.visualization.draw_geometries(meshes, title, width=self.width, height=self.height)

    def _annotate_keypoints_2d(self, image: np.ndarray, keypoints: [KeyPoint2],
                               size: int = 15, color=(20, 255, 255), weight: int = 1):

        hs = int(round(size * 0.5))
        for kp in keypoints:
            x, y = self._get_transformed_coordinates(kp)
            cv2.drawMarker(image, (x, y), color, cv2.MARKER_TILTED_CROSS, size, weight)
            cv2.putText(image, f"{kp.index}", (x + hs, y + hs), cv2.FONT_HERSHEY_PLAIN, 1, color, weight, cv2.LINE_AA)
