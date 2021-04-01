import argparse
import PIL.Image

import trimesh
import numpy as np


class Muke(object):
    def __init__(self):
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Detects keypoint locations in a 3d model.')
    parser.add_argument("input", help="Input mesh.")
    parser.add_argument("--method", default="pose", choices=["pose", "face"],
                        help="Detection method.")

    args = parser.parse_args()
