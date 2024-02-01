from abc import ABC, abstractmethod
from typing import Optional

import numpy as np
from open3d import geometry
from open3d.visualization import rendering

from muke.model.Vertex import Vertex


class BaseRenderer(ABC):

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

    @abstractmethod
    def add_geometry(self, mesh: geometry.TriangleMesh, material: Optional[rendering.MaterialRecord]):
        pass

    @abstractmethod
    def rotate_scene(self, x: float, y: float, z: float):
        pass

    @abstractmethod
    def render(self) -> np.ndarray:
        pass

    @abstractmethod
    def cast_ray(self, x: float, y: float) -> Optional[Vertex]:
        pass
