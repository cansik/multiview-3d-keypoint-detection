# Multiview 3D Keypoint Detection (Muke) [![PyPI](https://img.shields.io/pypi/v/muke)](https://pypi.org/project/muke/)
A simple approach to 3D keypoint detection using 2D estimation methods and multiview rendering, based on the blender project for [automatic keypoint retopology](https://github.com/cansik/auto-keypoint-retopology).

Basically, the 3D model is rendered from different angles (views) and a 2D keypoint detection is performed. For each detected keypoint, a ray-cast is performed to determine the intersection point with the mesh surface. In the end, all intersection points of the different views are combined to calculate the current 3D position of the keypoint within the mesh. It is possible to define view-dependent keypoint indices to extract only the points that are visible in the current rendering. Muke returns a list of 3D keypoints containing both the position and the nearest vertex index.

![Visualisation](documentation/visualisation.png)

*Muke Process*

The project was originally implemented to have a simple and fast solution for 3D keypoints detection for retopology purposes. However, it can also be used for any other application where 3D keypoints are needed, such as rigging, animation, etc.

![Head Example](documentation/head.png)

*3D Facial Landmark Estimation (Human Head by [VistaPrime](https://sketchfab.com/3d-models/human-head-f46d952886ae4a8c8851341b810bba43) [CC Attribution](https://creativecommons.org/licenses/by/4.0/))*

### Installation

To install the package use the following pip command:

```bash
pip install muke
```

### Usage
Muke can be used as a command line tool to extract the keypoints in a specific format (e.g. [Wrap3](https://www.russian3dscanner.com/)). For that a configuration has to be created which defines the detection parameters as well as the rendering views.

#### Configuration

Example configuration:

```json
{
  "description": "MP Face",
  "detector": "media-pipe-face",
  "resolution": 1024,
  "generator": "wrap3",
  "views": [
    {
      "name": "frontal",
      "rotation": 0,
      "keypoints": [
        4,
        76,
        306
      ]
    }
  ]
}
```

To select a range of keypoint indices, it is possible to define a `start` and `end` (included) index. It is also possible to skip certain indices in that range. Here an example on how to create a range (`skip` is optional):

```json
{
  "start": 10,
  "end": 15,
  "skip": [13, 14]
}
```

#### Demo
Quickly try out Muke by using the following commands.

```bash
python -m muke assets/person.ply --display --resolution 1024
```

```bash
python -m muke assets/human_head.obj --display --resolution 1024 --detector media-pipe-face
```

```bash
python -m muke assets/human_head.obj --config config/media-pipe-face.json --display
```

#### Help

```bash
usage: muke [-h] [--detector {media-pipe-pose,media-pipe-face}]
            [--resolution RESOLUTION] [--generator {wrap3}] [--config CONFIG]
            [--load-raw] [--display] [--debug]
            input

Detects keypoint locations in a 3d model.

positional arguments:
  input                 Input mesh to process.

optional arguments:
  -h, --help            show this help message and exit
  --detector {media-pipe-pose,media-pipe-face}
                        Detection method for 2d keypoint detection (default:
                        media-pipe-pose).
  --resolution RESOLUTION
                        Render resolution for each view pass (default: 512).
  --generator {wrap3}   Generator methods for output generation (default:
                        wrap3).
  --config CONFIG       Path to the configuration JSON file.
  --load-raw            Load mesh raw without post-processing (default: False)
  --display             Shows result rendering with keypoints (default: False)
  --debug               Shows debug frames and information (default: False)
```

### Library
It is also possible to use Muke as a library to detect keypoints on an existing 3d mesh.

```python
import open3d as o3d

from muke.Muke import Muke
from muke.detector.MediaPipePoseDetector import MediaPipePoseDetector
from muke.model.DetectionView import DetectionView

# load mesh from filesystem
mesh = o3d.io.read_triangle_mesh("assets/person.ply")

# define rendered views
keypoint_indexes = {28, 27, 26, 25, 24, 23, 12, 11, 14, 13, 16, 15, 5, 2, 0}
views = [
    DetectionView("front", 0, keypoint_indexes),
    DetectionView("back", 180, keypoint_indexes),
]

# detect keypoints
with Muke(MediaPipePoseDetector()) as m:
    result = m.detect(mesh, views)

# present results
for kp in result:
    print(f"KP {kp.index}: {kp.x:.2f} {kp.y:.2f} {kp.z:.2f}")
```

### Detectors
It is possible to implement custom keypoint detectors. The custom detector has to implement the `BaseDetector` interface as shown in the following example.

```python
import numpy as np

from muke.detector.BaseDetector import BaseDetector
from muke.detector.KeyPoint2 import KeyPoint2


class CustomDetector(BaseDetector):
    def setup(self):
        # todo: initialize the custom detector
        pass

    def detect(self, image: np.ndarray) -> [KeyPoint2]:
        # todo: implement the custom 2d keypoint detection 
        pass

    def release(self):
        # todo: clean up allocated resources
        pass
```

### Renderer
The current version uses [Open3D](https://github.com/isl-org/Open3D) for rendering and raycasting. Initially, [trimesh](https://github.com/mikedh/trimesh) was used, which is archived in the [trimesh-renderer branch](https://github.com/cansik/multiview-3d-keypoint-detection/tree/trimesh-renderer). In the future it would be interesting to use [pygfx](https://github.com/pygfx/pygfx) as a lightweight alternative to Open3D.

### About
MIT License - Copyright (c) 2022 Florian Bruggisser
