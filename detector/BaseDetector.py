from detector.KeyPoint import KeyPoint
import numpy as np


class BaseDetector(object):
    def setup(self):
        pass

    def release(self):
        pass

    def detect(self, image: np.ndarray) -> [KeyPoint]:
        pass
