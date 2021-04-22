import mediapipe as mp
from mediapipe.python.solution_base import SolutionBase

from muke.detector.MediaPiperBaseDetector import MediaPipeBaseDetector

mp_drawing = mp.solutions.drawing_utils
mp_model = mp.solutions.pose


class MediaPipePoseDetector(MediaPipeBaseDetector):
    def create_model(self) -> SolutionBase:
        return mp_model.Pose(static_image_mode=True)

    def get_landmarks(self, results):
        return results.pose_landmarks
