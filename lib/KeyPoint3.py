class KeyPoint3(object):
    def __init__(self, index: int, x: float, y: float, z: float, vertex_index: int = -1, error_distance: float = 0.0):
        self.index = index
        self.x = x
        self.y = y
        self.z = z
        self.vertex_index = vertex_index
        self.error_distance = error_distance

    def __str__(self):
        return "[%d: %.2f, %.2f, %.2f (%d)]" \
               % (self.index, self.x, self.y, self.z, self.vertex_index)
