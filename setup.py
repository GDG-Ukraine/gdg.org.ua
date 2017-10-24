#! /usr/bin/env python
"""GDGUkraine package setuptools installer."""

__requires__ = ('setuptools>=36.6.0', )


from setuptools import setup


__name__ == '__main__' and setup(
    use_scm_version=True,
    setup_requires=[
        'setuptools-git',
        'setuptools-scm>=1.15.0',
    ],
)
