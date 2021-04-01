class KeyPoint(object):
    def __init__(self, index: int, x: int, y: int, z: int, confidence):
        self.index = index
        self.x = x
        self.y = y
        self.z = z
        self.confidence = confidence

    def __str__(self):
        return "[%d: %.2f, %.2f, %.2f (%.2f)]" \
               % (self.index, self.x, self.y, self.z, self.confidence)
