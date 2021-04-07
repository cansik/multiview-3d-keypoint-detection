# Multiview 3D Keypoint Detection (Muke)
A simple approach to detect 3d keypoints by using 2d estimation methods and multiview rendering.

### Installation

### Running

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

Example on how to create a range (`skip` is optional):

```json
{
  "start": 10,
  "end": 15,
  "skip": [13, 14]
}
```

#### Demo

```
python demo.py assets/person.ply --display --resolution 1024
```

```bash
python demo.py temp/AlexedWrapped.obj --display --resolution 1024 --detector media-pipe-face
```

```bash
python demo.py temp/AlexedWrapped.obj --display --config config/media-pipe-face.json
```

#### Help

```bash
usage: demo.py [-h] [--detector {media-pipe-pose,media-pipe-face}]
               [--resolution RESOLUTION] [--generator {wrap3}] [--display]
               [--debug]
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
  --display             Shows result rendering with keypoints (default: False)
  --debug               Shows debug frames and information (default: False)
```

### Idea

### About
Developed by cansik @ 2021