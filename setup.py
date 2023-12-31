#!/usr/bin/env python
# This file is part of febelfin-coda.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
import codecs
import os
import re

from setuptools import find_packages, setup


def read(fname):
    return codecs.open(
        os.path.join(os.path.dirname(__file__), fname), 'r', 'utf-8').read()


def get_version():
    init = read(os.path.join('coda', '__init__.py'))
    return re.search("__version__ = '([0-9.]*)'", init).group(1)


setup(name='febelfin-coda',
    version=get_version(),
    description='A module to parse CODA files',
    long_description=read('README.rst'),
    author='Tryton',
    author_email='foundation@tryton.org',
    url='https://pypi.org/project/febelfin-coda/',
    download_url='https://downloads.tryton.org/coda/',
    project_urls={
        "Bug Tracker": 'https://bugs.tryton.org/coda',
        "Forum": 'https://discuss.tryton.org/tags/coda',
        "Source Code": 'https://code.tryton.org/coda',
        },
    keywords='CODA parser',
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
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Office/Business',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
        ],
    license='BSD',
    )
