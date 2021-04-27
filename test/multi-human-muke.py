import argparse

import glob
import os

from tqdm import tqdm

from muke.Muke import Muke
from muke.detector.MediaPipePoseDetector import MediaPipePoseDetector
from muke.generator.Wrap3Generator import Wrap3Generator
from muke.model.MukeConfiguration import MukeConfiguration


def get_files_in_path(path: str, extensions: [str] = ["*.*"]):
    return sorted([f for ext in extensions for f in glob.glob(os.path.join(path, ext))])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Detects keypoint locations in multiple 3d models.')
    parser.add_argument("input", help="Input folder to process.")

    args = parser.parse_args()

    meshes = get_files_in_path(args.input, ["*.obj"])

    config = MukeConfiguration()
    config.detector = MediaPipePoseDetector()
    config.generator = Wrap3Generator()

    output = config.generator

    with Muke(config.detector,
              resolution=config.resolution,
              display=False,
              debug=False) as muke:

        with tqdm(total=len(meshes)) as pbar:
            for mesh_path in meshes:
                results = muke.detect(mesh_path, views=config.views)
                output.generate(mesh_path, results)
                pbar.update(1)

    print("done!")
