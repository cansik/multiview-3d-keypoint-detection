import json
import os

from generator.BaseGenerator import BaseGenerator
from model.KeyPoint3 import KeyPoint3


class Wrap3Generator(BaseGenerator):
    def generate(self, input_path: str, keypoints: [KeyPoint3]):
        # create txt file besides input mesh
        keypoint_file_name = "%s_keypoints.json" % os.path.splitext(input_path)[0]
        output = json.dumps([{"x": kp.x, "y": kp.y, "z": kp.z} for kp in keypoints], indent=4, sort_keys=True)
        with open(keypoint_file_name, "w") as file:
            file.write(output)
