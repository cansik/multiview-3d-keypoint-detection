import argparse
import json

from muke.model import MukeDetectors, MukeGenerators, MukeDefaultResolution
from muke.model.MukeConfiguration import MukeConfiguration
from muke.Muke import Muke


def parse_args():
    detection_methods = list(MukeDetectors.keys())
    generator_methods = list(MukeGenerators.keys())

    parser = argparse.ArgumentParser(prog="muke",
                                     description='Detects keypoint locations in a 3d model.')
    parser.add_argument("input", help="Input mesh to process.")
    parser.add_argument("--detector", default=detection_methods[0], choices=detection_methods,
                        help="Detection method for 2d keypoint detection (default: %s)." % detection_methods[0])
    parser.add_argument("--resolution", default=MukeDefaultResolution, type=int,
                        help="Render resolution for each view pass (default: %d)." % MukeDefaultResolution)
    parser.add_argument("--generator", default=generator_methods[0], choices=generator_methods,
                        help="Generator methods for output generation (default: %s)." % generator_methods[0])
    parser.add_argument("--config", required=False, help="Path to the configuration JSON file.")
    parser.add_argument("--display", action='store_true',
                        help="Shows result rendering with keypoints (default: False)")
    parser.add_argument("--debug", action='store_true',
                        help="Shows debug frames and information (default: False)")

    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    print("running muke with %s to %s..." % (args.detector, args.generator))

    # create config
    # todo: make it possible to overwrite json settings from args
    if args.config is None:
        config = MukeConfiguration.from_args(args)
    else:
        with open(args.config) as json_file:
            data = json.load(json_file)
        config = MukeConfiguration.from_json(data)

    output = config.generator

    with Muke(config.detector,
              resolution=config.resolution,
              display=args.display,
              debug=args.debug) as muke:

        results = muke.detect_file(args.input, views=config.views)
        output.generate(args.input, results)


if __name__ == "__main__":
    main()
