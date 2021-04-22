from abc import ABC, abstractmethod

from muke.detector.KeyPoint2 import KeyPoint2
import numpy as np


class BaseDetector(ABC):
    @abstractmethod
    def setup(self):
        pass

    @abstractmethod
    def release(self):
        pass

    @abstractmethod
    def detect(self, image: np.ndarray) -> [KeyPoint2]:
        pass
