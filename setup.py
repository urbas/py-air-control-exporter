#!/usr/bin/env python

"""The setup script."""

from os import uname
from setuptools import setup, find_packages

REQUIREMENTS = ["Flask>=1.0.0", "philips-air-purifier>=0.0.4"]

SETUP_REQUIREMENTS = ["pytest-runner"]

TEST_REQUIREMENTS = ["pytest"]

setup(
    author="Matej Urbas",
    author_email="matej.urbas@gmail.com",
    entry_points={
        "console_scripts": [
            "philips-air-exporter=philips_air_purifier_exporter.app:main"
        ]
    },
    install_requires=REQUIREMENTS,
    include_package_data=True,
    keywords="philips_air_purifier_exporter",
    name="philips_air_purifier_exporter",
    packages=find_packages(include=["philips_air_purifier_exporter"]),
    setup_requires=SETUP_REQUIREMENTS,
    test_suite="tests",
    tests_require=TEST_REQUIREMENTS,
)
