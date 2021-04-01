import PIL.Image

import trimesh
import numpy as np

from muke.BaseDetector import BaseDetector


class Muke(object):
    def __init__(self, detector: BaseDetector):
        self.detector = detector

    def __enter__(self):
        self.detector.setup()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.detector.release()

    def process(self, mesh_path: str, views):
        pass