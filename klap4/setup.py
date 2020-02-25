#!/usr/bin/env python3

import os
from pathlib import Path
import re
import setuptools

module_dir = Path(os.path.dirname(os.path.realpath(__file__)))

short_description = "KMNR Music Library Interface"

with open(module_dir/"__init__.py", 'r') as module_file:
    try:
        module_version = re.search("^__version__ = \"((\d.?)+)\"$", module_file.read()).group(1)
    except AttributeError:
        module_version = "0.0.0"
try:
    with open(module_dir.parent/"README.md", 'r') as readme_file:
        long_description = readme_file.read()
except FileNotFoundError:
    long_description = short_description

setuptools.setup(
    name="KLAP 4",
    version=module_version,
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
