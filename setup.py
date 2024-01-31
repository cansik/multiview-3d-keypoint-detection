from pathlib import Path

from setuptools import setup, find_packages

NAME = "muke"

required_packages = find_packages(exclude=["test"])

with open("requirements.txt") as f:
    required = f.read().splitlines()

# read readme
current_dir = Path(__file__).parent
long_description = (current_dir / "README.md").read_text()

setup(
    name=NAME,
    version="0.3.1",
    packages=required_packages,
    url="https://github.com/cansik/multiview-3d-keypoint-detection",
    license="MIT License",
    author="Florian Bruggisser",
    author_email="github@broox.ch",
    description="A simple approach to 3D keypoint detection using 2D estimation methods and multiview rendering.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=required,
    entry_points={
        "console_scripts": [
            "muke = muke.__main__:main",
        ],
    },
)
