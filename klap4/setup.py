#!/usr/bin/env python3

from pathlib import Path
import re
import setuptools

module_dir = Path(__file__).resolve().parent

# KLAP4 module short description.
short_description = "KMNR Music Library Interface"

# Try and read the klap4 module's version.
with (module_dir/"__init__.py").open('r') as module_file:
    try:
        module_version = re.search("^__version__ = \"((\d.?)+)\"$", module_file.read()).group(1)
    except AttributeError:
        module_version = "0.0.0"
try:  # Try and read the README.md file for the long description.
    with (module_dir.parent/"README.md").open('r') as readme_file:
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
