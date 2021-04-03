import argparse
import os
import json

from detector.MediaPipePoseDetector import MediaPipePoseDetector
from Muke import Muke
from lib.DetectionView import DetectionView

detectors = {
    "media-pipe-pose": MediaPipePoseDetector()
}


def main():
    with Muke(detectors[args.method],
              resolution=args.resolution,
              display=args.display,
              debug=args.debug) as muke:
        results = muke.detect(args.input, views=[DetectionView("Test")])

        # create txt file besides input mesh
        keypoint_file_name = "%s_keypoints.txt" % os.path.splitext(args.input)[0]
        output = json.dumps([{"x": kp.x, "y": kp.y, "z": kp.z} for kp in results])
        with open(keypoint_file_name, "w") as file:
            file.write(output)


if __name__ == "__main__":
    detection_methods = list(detectors.keys())

    parser = argparse.ArgumentParser(description='Detects keypoint locations in a 3d model.')
    parser.add_argument("input", help="Input mesh.")
    parser.add_argument("--method", default=detection_methods[0], choices=detection_methods,
                        help="Detection methods [%s]." % (", ".join(detection_methods)))
    parser.add_argument("--resolution", default=512, type=int, help="Render resolution for each view pass.")
    parser.add_argument("--display", action='store_true', help="Shows result rendering with keypoints.")
    parser.add_argument("--debug", action='store_true', help="Shows debug frames and information.")

    args = parser.parse_args()

    main()
