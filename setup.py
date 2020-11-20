#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

REQUIREMENTS = [
    "Flask>=1.0.0",
    "prometheus_client>=0.9.0",
    "py-air-control>=2.0.0",
]

SETUP_REQUIREMENTS = ["pytest-runner"]

TEST_REQUIREMENTS = ["pytest"]

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("CHANGELOG.md", "r") as fh:
    long_description += "\n\n" + fh.read()

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
    test_suite="tests",
    tests_require=TEST_REQUIREMENTS,
    version="0.1.1",
)
