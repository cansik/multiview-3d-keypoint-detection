import logging
from typing import List

import cv2
import numpy as np
import open3d as o3d

from muke.Lines import Lines
from muke.detector.BaseDetector import BaseDetector
from muke.detector.KeyPoint2 import KeyPoint2
from muke.model.DetectionView import DetectionView
from muke.model.KeyPoint3 import KeyPoint3

from scipy.spatial import distance


class Muke(object):
    def __init__(self, detector: BaseDetector, resolution: int = 512, display=False, debug=False):
        self.detector = detector

        self.display = display
        self.debug = debug

        self.width = resolution
        self.height = resolution
        self.pixel_density = 1.0

        self.ray_size = 5

        self.camera_zoom = 0.55
        self.camera_fov = -90  # by default orthographic

        self.background_color = [255, 255, 255]

    def __enter__(self):
        self.detector.setup()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.detector.release()

    def detect_file(self, mesh_path: str, views: List[DetectionView], post_processing: bool = True) -> List[KeyPoint3]:
        mesh = o3d.io.read_triangle_mesh(mesh_path, enable_post_processing=post_processing)
        return self.detect(mesh, views)

    def detect(self, mesh: o3d.geometry.TriangleMesh, views: List[DetectionView]) -> List[KeyPoint3]:
        # setup scene
        vis = o3d.visualization.VisualizerWithVertexSelection()
        vis.create_window(width=self.width, height=self.height, visible=self.display)
        vis.add_geometry(mesh, reset_bounding_box=True)

        ctr: o3d.visualization.ViewControl = vis.get_view_control()
        ctr.change_field_of_view(self.camera_fov)
        ctr.set_zoom(self.camera_zoom)

        opt: o3d.visualization.RenderOption = vis.get_render_option()
        opt.background_color = np.asarray(self.background_color)
        opt.show_coordinate_frame = False

        # detect keypoints
        detections = {}
        view_stack = views[::-1]

        def render(v):
            if len(view_stack) == 0:
                v.close()
                vis.destroy_window()
                return

            view = view_stack.pop()
            keypoints = self._detect_view(vis, mesh, view)

            # add keypoints to dictionary
            for kp in keypoints:
                if kp.index not in detections:
                    detections[kp.index] = []
                detections[kp.index].append(kp)

        # run with animation callback
        vis.register_animation_callback(render)
        vis.run()

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

        logging.info("estimated %d key-points (error total: %.4f avg: %.4f)"
                     % (len(keypoints), summed_error, summed_error / max(1.0, len(keypoints))))

        if self.display:
            self._annotate_keypoints_3d("Result", mesh, keypoints)

        return keypoints

    def _detect_view(self, vis: o3d.visualization.VisualizerWithVertexSelection,
                     mesh: o3d.geometry.TriangleMesh,
                     view: DetectionView) -> List[KeyPoint3]:
        # apply view state
        self._set_scene_rotation(vis, view.rotation)

        # offscreen renders
        vis.poll_events()
        vis.update_renderer()
        data = np.asarray(vis.capture_screen_float_buffer())

        # image to numpy
        image_np = (data * 255).astype(np.uint8)

        # detect keypoints
        keypoints = self.detector.detect(image_np)

        # filter keypoints
        if view.keypoints is not None:
            keypoints = list(filter(lambda kp: kp.index in view.keypoints, keypoints))

        # annotate if debug is on
        if self.debug:
            preview_image = image_np.copy()
            preview_image = cv2.cvtColor(preview_image, cv2.COLOR_RGB2BGR)
            self._annotate_keypoints_2d(preview_image, keypoints)
            cv2.imshow(f"{view.name}: 2D Key Points", preview_image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        # raycast from camera
        vertices = np.asarray(mesh.vertices)
        result = []
        for kp in keypoints:
            x, y = self._get_transformed_coordinates(kp)
            half_ray_size = self.ray_size * 0.5

            picked_vertices = vis.pick_points(x, y, self.ray_size, self.ray_size)
            # todo: replace this with an actual position estimation (raycasting) instead of a vertex
            picked_vertices = vis.pick_points(x - half_ray_size, y - half_ray_size, self.ray_size, self.ray_size)

            if self.debug:
                vis.add_picked_points(picked_vertices)

            picked_vertices = [picked_vertices[i] for i in range(len(picked_vertices))]

            if len(picked_vertices) == 0:
                continue

            positions = np.stack([vertices[vi] for vi in picked_vertices])
            avg_position = np.mean(positions, axis=0)

            result.append(KeyPoint3(kp.index, avg_position[0], avg_position[1], avg_position[2]))

        # reset view state
        self._set_scene_rotation(vis, -view.rotation)

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

            # render_rays()

            # shoot rays
            t_mesh = o3d.t.geometry.TriangleMesh.from_legacy(mesh)
            scene = o3d.t.geometry.RaycastingScene()
            scene.add_triangles(t_mesh)
            ans = scene.cast_rays(o3d.core.Tensor(rays, dtype=o3d.core.Dtype.Float32))

            hit_triangles = ans["primitive_ids"].numpy()
            hit_uvs = ans["primitive_uvs"].numpy()
            triangles = np.asarray(mesh.triangles)

            back_positions = []
            for i in range(len(hit_triangles)):
                triangle = triangles[hit_triangles[i]]
                barycenter = np.average(np.take(vertices, triangle, axis=0), axis=0)
                # todo: add hit uv's (but how is it rotated?)
                back_positions.append(barycenter)

            # calculate new mean positions
            lines = Lines()
            markers = []
            for i, kp in enumerate(result):
                front_position = np.array([kp.x, kp.y, kp.z], dtype=np.float)
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

    def _annotate_keypoints_2d(self, image: np.ndarray, keypoints: [KeyPoint2], size: int = 15, color=(0, 255, 0)):
        for kp in keypoints:
            x, y = self._get_transformed_coordinates(kp)
            cv2.drawMarker(image, (x, y), color, cv2.MARKER_CROSS, size, 1)
            cv2.putText(image, f"{kp.index}", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)
