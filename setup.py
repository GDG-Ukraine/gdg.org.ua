#! /usr/bin/env python
"""GDGUkraine package setuptools installer."""
from setuptools import setup


params = dict(
    dependency_links=[
        'https://cdn.mysql.com/Downloads/Connector-Python/'
        'mysql-connector-python-2.0.4.zip'
        '#md5=3df394d89300db95163f17c843ef49df'
    ],
    pbr=True,
    package_dir={'': 'src'},
    setup_requires=['pbr==3.0.0'],
)

if __name__ == '__main__':
    setup(**params)
