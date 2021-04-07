from detector.MediaPipeFaceDetector import MediaPipeFaceDetector
from detector.MediaPipePoseDetector import MediaPipePoseDetector
from generator.Wrap3Generator import Wrap3Generator

MukeDetectors = {
    "media-pipe-pose": MediaPipePoseDetector(),
    "media-pipe-face": MediaPipeFaceDetector()
}

MukeGenerators = {
    "wrap3": Wrap3Generator()
}

MukeDefaultResolution = 512
