from abc import abstractmethod

import mediapipe as mp
import numpy as np
from mediapipe.python.solution_base import SolutionBase

from muke.detector.BaseDetector import BaseDetector
from muke.detector.KeyPoint2 import KeyPoint2

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

    def detect(self, image: np.ndarray) -> [KeyPoint2]:
        keypoints = []

        results = self.model.process(image)
        landmarks = self.get_landmarks(results)

        if landmarks is None:
            return keypoints

        for i, landmark in enumerate(landmarks.landmark):
            keypoints.append(KeyPoint2(
                i,
                landmark.x,
                landmark.y,
                landmark.visibility
            ))

        return keypoints
