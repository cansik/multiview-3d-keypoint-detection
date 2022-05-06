from typing import Set


class DetectionView(object):
    def __init__(self, name: str, rotation: float, keypoints: Set[int] = None, infinite_ray: bool = False):
        self.name = name
        self.rotation = rotation
        self.keypoints = keypoints
        self.infinite_ray = infinite_ray
