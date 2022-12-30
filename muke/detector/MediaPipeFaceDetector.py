import mediapipe as mp
from mediapipe.python.solution_base import SolutionBase

from muke.detector.MediaPiperBaseDetector import MediaPipeBaseDetector

mp_drawing = mp.solutions.drawing_utils
mp_model = mp.solutions.face_mesh


class MediaPipeFaceDetector(MediaPipeBaseDetector):
    def create_model(self) -> SolutionBase:
        return mp_model.FaceMesh(static_image_mode=True)

    def get_landmarks(self, results):
        if results.multi_face_landmarks is None:
            raise Exception("No faces detected on rendering. Please check the render options.")

        return results.multi_face_landmarks[0]
