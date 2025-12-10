"""
Setup script for development installation.
Use: pip install -e .
"""

from setuptools import setup, find_packages

setup(
    name="disco-baa-01",
    version="0.1.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
)
