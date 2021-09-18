#!/usr/bin/env python
# This file is part of febelfin-coda.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
import os
import re
import codecs
from setuptools import setup, find_packages


def read(fname):
    return codecs.open(
        os.path.join(os.path.dirname(__file__), fname), 'r', 'utf-8').read()


def get_version():
    init = read(os.path.join('coda', '__init__.py'))
    return re.search("__version__ = '([0-9.]*)'", init).group(1)


setup(name='febelfin-coda',
    version=get_version(),
    author='B2CK',
    author_email='info@b2ck.com',
    url='https://coda.b2ck.com/',
    description='A module to parse CODA files',
    long_description=read('README'),
    packages=find_packages(),
    package_data={
        'coda': ['CODA.txt'],
        },
    python_requires='>=3.5',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Office/Business',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
        ],
    license='BSD',
    test_suite='coda.test',
    )
