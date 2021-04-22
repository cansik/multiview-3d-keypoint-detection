from setuptools import setup, find_packages

NAME = 'muke'

required_packages = find_packages()

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name=NAME,
    version='1.0.0',
    packages=required_packages,
    url='https://github.com/cansik/multiview-3d-keypoint-detection',
    license='MIT License',
    author='Florian Bruggisser',
    author_email='github@broox.ch',
    description='A simple approach to detect 3d keypoints by using 2d estimation methods and multiview rendering.',
    install_requires=required,
)
