from setuptools import setup, find_packages

install_requires = ['SQLAlchemy', 'yuicompressor', 'webassets', 'Routes', 'oursql']

setup(name='GDGUkraine',
      version='1.0',
      author='Svyatoslav Sydorenko',
      author_email='svyatoslav@sydorenko.org.ua',
      package_dir={'': 'src'},
      packages=find_packages('src', exclude=["test**"]),
      install_requires=install_requires,
      zip_safe=False)