#!/usr/bin/env python
'''
This is an example for the possible setup of a library
located by default within the src/ folder.
All packages will be installed to python.site-packages
simply run:

    >>> python setup.py install

For a local installation or if you like to develop further

    >>> python setup.py develop --user


The test_suite located within the test/ folder
will be executed automatically.
'''

# Default version information
source_path = 'src'
__version__ = '0.1'


import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-samanta',
    version=__version__,
    package_dir={'': source_path},
    packages=find_packages(source_path),
    include_package_data=True,
    license='MIT License',
    description='Simple Account Management for Tools and Applications.',
    long_description=README,
    url='https://github.com/cagonza6/samanta/',
    author='Cristian A. Gonzalez Mora',
    author_email='cagonza6@gmail.com',
    install_requires=['django>=1.11.15,<1.12', 'django-simple-captcha',
                      'pillow', 'django-countries'],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)