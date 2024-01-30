from abc import ABC, abstractmethod
from typing import Optional

import numpy as np
from open3d.cpu.pybind import geometry
from open3d.cpu.pybind.visualization import rendering

from muke.model.DetectionView import DetectionView


class BaseRenderer(ABC):

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

    @abstractmethod
    def add_geometry(self, mesh: geometry.TriangleMesh, material: Optional[rendering.MaterialRecord]):
        pass

    @abstractmethod
    def render(self, view: DetectionView) -> np.ndarray:
        pass
