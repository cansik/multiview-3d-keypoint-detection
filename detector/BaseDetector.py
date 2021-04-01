from abc import ABC, abstractmethod

from detector.KeyPoint import KeyPoint
import numpy as np


class BaseDetector(ABC):
    @abstractmethod
    def setup(self):
        pass

    @abstractmethod
    def release(self):
        pass

    @abstractmethod
    def detect(self, image: np.ndarray) -> [KeyPoint]:
        pass
