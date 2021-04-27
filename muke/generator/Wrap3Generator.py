import json
import os

from muke.generator.BaseGenerator import BaseGenerator
from muke.model import KeyPoint3


class Wrap3Generator(BaseGenerator):
    def generate(self, input_path: str, keypoints: [KeyPoint3]):
        # create txt file besides input mesh
        keypoint_file_name = "%s_keypoints.txt" % os.path.splitext(input_path)[0]
        output = json.dumps([{"x": kp.x, "y": kp.y, "z": kp.z} for kp in keypoints], indent=4, sort_keys=True)
        with open(keypoint_file_name, "w") as file:
            file.write(output)
