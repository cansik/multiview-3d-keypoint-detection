from abc import ABC, abstractmethod

from muke.model import KeyPoint3


class BaseGenerator(ABC):
    @abstractmethod
    def generate(self, input_path: str, keypoints: [KeyPoint3]):
        pass