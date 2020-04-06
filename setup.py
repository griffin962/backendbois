#!/usr/bin/env python3

from pathlib import Path
import setuptools

import klap4

current_dir = Path(__file__).absolute().parent

# KLAP4 module short description.
short_description = "KMNR Music Library Interface"

try:  # Try and read the README.md file for the long description.
    with (current_dir.parent/"README.md").open('r') as readme_file:
        long_description = readme_file.read()
except FileNotFoundError:
    long_description = short_description


setuptools.setup(
    name="KLAP 4",
    version=klap4.__version__,
    description=short_description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Unix"
    ],
    python_requires=">=3.7"
)
