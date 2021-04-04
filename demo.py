import argparse
import os
import json

from detector.MediaPipeFaceDetector import MediaPipeFaceDetector
from detector.MediaPipePoseDetector import MediaPipePoseDetector
from Muke import Muke
from generator.Wrap3Generator import Wrap3Generator
from model.DetectionView import DetectionView

detectors = {
    "media-pipe-pose": MediaPipePoseDetector(),
    "media-pipe-face": MediaPipeFaceDetector()
}

generators = {
    "wrap3": Wrap3Generator()
}


def main():
    print("running muke with %s to %s..." % (args.detector, args.generator))
    output = generators[args.generator]

    with Muke(detectors[args.detector],
              resolution=args.resolution,
              display=args.display,
              debug=args.debug) as muke:
        results = muke.detect(args.input, views=[DetectionView("Test")])
        output.generate(args.input, results)


if __name__ == "__main__":
    detection_methods = list(detectors.keys())
    generator_methods = list(generators.keys())

    parser = argparse.ArgumentParser(description='Detects keypoint locations in a 3d model.')
    parser.add_argument("input", help="Input mesh to process.")
    parser.add_argument("--detector", default=detection_methods[0], choices=detection_methods,
                        help="Detection method for 2d keypoint detection (default: %s)." % detection_methods[0])
    parser.add_argument("--resolution", default=512, type=int,
                        help="Render resolution for each view pass (default: 512).")
    parser.add_argument("--generator", default=generator_methods[0], choices=generator_methods,
                        help="Generator methods for output generation (default: %s)." % generator_methods[0])
    parser.add_argument("--display", action='store_true',
                        help="Shows result rendering with keypoints (default: False)")
    parser.add_argument("--debug", action='store_true',
                        help="Shows debug frames and information (default: False)")

    args = parser.parse_args()

    main()
