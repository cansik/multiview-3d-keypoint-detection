from typing import Set


class DetectionView(object):
    def __init__(self, name: str, rotation: float, keypoints: Set[int] = None):
        self.name = name
        self.rotation = rotation
        self.keypoints = keypoints
