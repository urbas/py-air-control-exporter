#!/usr/bin/env python

"""The setup script."""

import packaging.version
import setuptools_scm
from pathlib import Path
from setuptools import setup

REQUIREMENTS = [
    "Flask>=1.0.0",
    "prometheus_client>=0.8.0",
    "py-air-control>=2.0.0",
]

SETUP_REQUIREMENTS = ["pytest-runner", "setuptools_scm"]

TEST_REQUIREMENTS = ["pytest"]

CHANGELOG = Path("CHANGELOG.md").read_text()

long_description = f"{Path('README.md').read_text()}\n\n{CHANGELOG}"


def get_version():
    try:
        version = setuptools_scm.get_version()
        changelog_expected_version = ".".join(
            str(el) for el in packaging.version.parse(version).release
        )
        changelog_version = CHANGELOG.splitlines()[0].strip("#").strip()
        assert changelog_version >= changelog_expected_version, (
            f"Unexpected version in CHANGELOG.md's top section. Should be greater "
            f"than or equal to {changelog_expected_version} but is "
            f"{changelog_version}. Please add a section for the upcoming release."
        )
        return version
    except LookupError:
        # NB: we could be building from a tarball.
        return "0.0.0"


setup(
    author_email="matej.urbas@gmail.com",
    author="Matej Urbas",
    include_package_data=True,
    install_requires=REQUIREMENTS,
    keywords=["py-air-control-exporter", "py-air-control", "prometheus", "exporter"],
    long_description_content_type="text/markdown",
    long_description=long_description,
    name="py-air-control-exporter",
    packages=["py_air_control_exporter"],
    setup_requires=SETUP_REQUIREMENTS,
    test_suite="test",
    tests_require=TEST_REQUIREMENTS,
    version=get_version(),
)
