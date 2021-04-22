class KeyPoint2(object):
    def __init__(self, index: int, x: float, y: float, confidence: float):
        self.index = index
        self.x = x
        self.y = y
        self.confidence = confidence

    def __str__(self):
        return "[%d: %.2f, %.2f (%.2f)]" \
               % (self.index, self.x, self.y, self.confidence)

    def __repr__(self):
        return "i:%d" % self.index
