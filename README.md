# Multiview 3D Keypoint Detection (Muke)
A simple approach to detect 3d keypoints by using 2d estimation methods and multiview rendering. The idea is based on the blender project for [automatic keypoint retopology](https://github.com/cansik/auto-keypoint-retopology).
Basically the 3d model is rendered from various angles (views) and a 2d key-point detection is applied. For each detected keypoint a ray-cast is performed to detect the intersection point with the mesh surface. In the end all intersection of the different views are combined to calculate the actual 3d position of the keypoint inside the mesh. It is possible to define view dependent keypoint indices to extract only the ones that are visible in the current rendering. Muke return a list of 3d keypoints containing the position as well as the closest vertex index.

![Visualisation](documentation/visualisation.png)
*Muke Process*

The project was originally implemented to have a simple and fast solution for 3D keypoints detection for retopology purposes. However, it can also be used for any other application where 3D keypoints are needed, such as rigging, animation, etc.

### Installation

To install the package use the following pip command:

```bash
pip install muke
```

### Usage
Muke can be used as a command line tool to extract the keypoints in a specific format (f.e. [Wrap3](https://www.russian3dscanner.com/)). For that a configuration has to be created which defines the detection parameters as well as the rendering views.

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

```bash
python -m muke assets/person.ply --display --resolution 1024
```

```bash
python -m muke temp/AlexedWrapped.obj --display --resolution 1024 --detector media-pipe-face
```

```bash
python -m muke temp/AlexedWrapped.obj --display --config config/media-pipe-face.json
```

#### Help

```bash
usage: muke [-h] [--detector {media-pipe-pose,media-pipe-face}] [--resolution RESOLUTION] [--generator {wrap3}]
            [--config CONFIG] [--display] [--debug]
            input

Detects keypoint locations in a 3d model.

positional arguments:
  input                 Input mesh to process.

optional arguments:
  -h, --help            show this help message and exit
  --detector {media-pipe-pose,media-pipe-face}
                        Detection method for 2d keypoint detection (default: media-pipe-pose).
  --resolution RESOLUTION
                        Render resolution for each view pass (default: 512).
  --generator {wrap3}   Generator methods for output generation (default: wrap3).
  --config CONFIG       Path to the configuration JSON file.
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

### About
MIT License - Copyright (c) 2022 Florian Bruggisser