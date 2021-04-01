import mediapipe as mp
from mediapipe.python.solution_base import SolutionBase

from detector.MediaPiperBaseDetector import MediaPipeBaseDetector

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose


class MediaPipePoseDetector(MediaPipeBaseDetector):
    def create_model(self) -> SolutionBase:
        print("create pose model...")
        return mp_pose.Pose(static_image_mode=True)
