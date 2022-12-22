import numpy as np

from muke.detector.BaseDetector import BaseDetector
from muke.detector.KeyPoint2 import KeyPoint2


class CustomDetector(BaseDetector):
    def setup(self):
        pass

    def detect(self, image: np.ndarray) -> [KeyPoint2]:
        # todo: implement the custom 2d keypoint detection
        pass

    def release(self):
        pass
