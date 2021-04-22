from muke.model import MukeDetectors, MukeGenerators, MukeDefaultResolution
from muke.model.DetectionView import DetectionView


class MukeConfiguration(object):
    def __init__(self):
        detection_methods = list(MukeDetectors.keys())
        generator_methods = list(MukeGenerators.keys())

        self.detector = detection_methods[0]
        self.generator = generator_methods[0]
        self.resolution = MukeDefaultResolution
        self.views = [DetectionView("Front", rotation=0)]

    @staticmethod
    def from_args(args):
        config = MukeConfiguration()
        MukeConfiguration.copy_single_params(config, args)
        return config

    @staticmethod
    def from_json(data):
        config = MukeConfiguration()
        MukeConfiguration.copy_single_params(config, data)

        views = []
        for view_data in data["views"]:
            view = DetectionView(view_data["name"],
                                 view_data["rotation"],
                                 keypoints=set())

            for value in view_data["keypoints"]:
                if isinstance(value, int):
                    view.keypoints.add(value)
                else:
                    # parse a range
                    start = value["start"]
                    end = value["end"]
                    skip = set(value.get("skip", []))
                    [view.keypoints.add(i) for i in range(start, end + 1) if i not in skip]

            views.append(view)

        if len(views) > 0:
            config.views = views

        return config

    @staticmethod
    def copy_single_params(config, data):
        MukeConfiguration._set_value_if_available(data, config, "detector", method=lambda x: MukeDetectors[x])
        MukeConfiguration._set_value_if_available(data, config, "generator", method=lambda x: MukeGenerators[x])
        MukeConfiguration._set_value_if_available(data, config, "resolution")

    @staticmethod
    def _set_value_if_available(source, target, name: str, method=lambda x: x):
        if MukeConfiguration._has_value(source, name):
            setattr(target, name, method(MukeConfiguration._get_value(source, name)))

    @staticmethod
    def _has_value(obj, name: str) -> bool:
        if hasattr(obj, name):
            return True
        else:
            if name in obj:
                return True
        return False

    @staticmethod
    def _get_value(obj, name: str):
        if hasattr(obj, name):
            return getattr(obj, name)
        else:
            return obj[name]
