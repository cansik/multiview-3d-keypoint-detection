from mediapipe.python.solution_base import SolutionBase

from detector.BaseDetector import BaseDetector
from detector.KeyPoint import KeyPoint

import mediapipe as mp
import numpy as np

mp_drawing = mp.solutions.drawing_utils


class MediaPipeBaseDetector(BaseDetector):
    def __init__(self):
        self.model: SolutionBase = None

    def create_model(self) -> SolutionBase:
        pass

    def setup(self):
        self.model = self.create_model()

    def release(self):
        self.model.close()

    def __enter__(self):
        self.setup()
        return self

    def __exit__(self, type, value, traceback):
        self.release()

    def detect(self, image: np.ndarray) -> [KeyPoint]:
        print("mediapipe pose detection...")
        return []
