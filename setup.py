from setuptools import setup, find_packages

install_requires = [
    'CherryPy==7.1.0',
    'SQLAlchemy==1.0.11', 'yuicompressor==2.4.8', 'webassets==0.11.1',
    'Routes==2.2', 'mysql-connector-python==2.0.4', 'Cerberus==0.9.2',
    'python-social-auth==0.2.13', 'alembic==0.8.4', 'openpyxl==2.3.2',
]

setup(name='GDGUkraine',
      version='1.0',
      author='Svyatoslav Sydorenko',
      author_email='svyatoslav@sydorenko.org.ua',
      package_dir={'': 'src'},
      packages=find_packages('src', exclude=['test**']),
      install_requires=install_requires,
      zip_safe=False)
