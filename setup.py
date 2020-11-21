#!/usr/bin/env python

"""The setup script."""

from pathlib import Path
from setuptools import setup, find_packages

REQUIREMENTS = [
    "Flask>=1.0.0",
    "prometheus_client>=0.8.0",
    "py-air-control>=2.0.0",
]

SETUP_REQUIREMENTS = ["pytest-runner", "setuptools_scm"]

TEST_REQUIREMENTS = ["pytest"]

long_description = (
    f"{Path('README.md').read_text()}\n\n{Path('CHANGELOG.md').read_text()}"
)

setup(
    author_email="matej.urbas@gmail.com",
    author="Matej Urbas",
    include_package_data=True,
    install_requires=REQUIREMENTS,
    keywords=["py-air-control-exporter", "py-air-control", "prometheus", "exporter"],
    long_description_content_type="text/markdown",
    long_description=long_description,
    name="py-air-control-exporter",
    packages=find_packages(include=["py_air_control_exporter"]),
    setup_requires=SETUP_REQUIREMENTS,
    test_suite="test",
    tests_require=TEST_REQUIREMENTS,
    use_scm_version=True,
)
