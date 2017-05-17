#! /usr/bin/env python
"""GDGUkraine package setuptools installer."""
from setuptools import setup


params = dict(
    use_scm_version=True,
    package_dir={'': 'src'},
    setup_requires=['setuptools_scm>=1.15.0'],
)

if __name__ == '__main__':
    setup(**params)
