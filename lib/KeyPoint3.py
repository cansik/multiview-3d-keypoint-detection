class KeyPoint3(object):
    def __init__(self, index: int, x: float, y: float, z: float, triangle_index: int, vertex_index: int = -1):
        self.index = index
        self.x = x
        self.y = y
        self.z = z
        self.triangle_index = triangle_index
        self.vertex_index = vertex_index

    def __str__(self):
        return "[%d: %.2f, %.2f, %.2f (%d, %d)]" \
               % (self.index, self.x, self.y, self.z, self.triangle_index, self.vertex_index)
