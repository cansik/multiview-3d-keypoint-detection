from abc import abstractmethod

import mediapipe as mp
import numpy as np
from mediapipe.python.solution_base import SolutionBase

from detector.BaseDetector import BaseDetector
from detector.KeyPoint import KeyPoint

mp_drawing = mp.solutions.drawing_utils


class MediaPipeBaseDetector(BaseDetector):
    def __init__(self):
        self.model: SolutionBase = None

    @abstractmethod
    def create_model(self) -> SolutionBase:
        pass

    @abstractmethod
    def get_landmarks(self, results):
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
        keypoints = []

        results = self.model.process(image)
        landmarks = self.get_landmarks(results)

        if landmarks is None:
            return keypoints

        for landmark in landmarks.landmark:
            keypoints.append(KeyPoint(
                landmark.x,
                landmark.y,
                landmark.z,
                landmark.visibility
            ))

        return keypoints
