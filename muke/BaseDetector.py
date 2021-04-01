from muke.KeyPoint import KeyPoint


class BaseDetector(object):
    def setup(self):
        pass

    def release(self):
        pass

    def extract(self) -> [KeyPoint]:
        pass
