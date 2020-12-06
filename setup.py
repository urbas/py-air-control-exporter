#!/usr/bin/env python

"""The setup script."""

from pathlib import Path
from setuptools import setup

REQUIREMENTS = [
    "click>=7.0.0",
    "Flask>=1.0.0",
    "prometheus_client>=0.8.0",
    "py-air-control>=2.0.0",
]

SETUP_REQUIREMENTS = ["pytest-runner"]

TEST_REQUIREMENTS = ["pytest"]

CHANGELOG = Path("CHANGELOG.md").read_text()

long_description = f"{Path('README.md').read_text()}\n\n{CHANGELOG}"

setup(
    author_email="matej.urbas@gmail.com",
    author="Matej Urbas",
    entry_points={
        "console_scripts": [
            "py-air-control-exporter = py_air_control_exporter.main:main"
        ]
    },
    include_package_data=True,
    install_requires=REQUIREMENTS,
    keywords=["py-air-control-exporter", "py-air-control", "prometheus", "exporter"],
    license="MIT license",
    long_description_content_type="text/markdown",
    long_description=long_description,
    name="py-air-control-exporter",
    packages=["py_air_control_exporter"],
    setup_requires=SETUP_REQUIREMENTS,
    test_suite="test",
    tests_require=TEST_REQUIREMENTS,
    url="https://github.com/urbas/sgp30-exporter",
    version="0.1.6",
)
