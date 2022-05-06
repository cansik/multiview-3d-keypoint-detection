from typing import Sequence

import numpy as np
import open3d as o3d


class Lines:
    def __init__(self):
        self._points = []
        self._lines = []
        self._colors = []

    def add_line(self, start: Sequence[float], end: Sequence[float], color: Sequence[float] = (0, 255, 0)):
        self._points.append(list(start))
        self._points.append(list(end))

        line_index = len(self._points)
        self._lines.append([line_index, line_index + 1])

        self._colors.append(list(color))

    def create_line_set(self) -> o3d.geometry.LineSet:
        ls = o3d.geometry.LineSet()

        ls.points = o3d.utility.Vector3dVector(np.array(self._points))
        ls.lines = o3d.utility.Vector2iVector(np.array(self._lines))
        ls.colors = o3d.utility.Vector3dVector(np.array(self._colors) / 255.0)

        return ls
