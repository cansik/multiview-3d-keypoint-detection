from abc import ABC, abstractmethod

from model.KeyPoint3 import KeyPoint3


class BaseGenerator(ABC):
    @abstractmethod
    def generate(self, input_path: str, keypoints: [KeyPoint3]):
        pass