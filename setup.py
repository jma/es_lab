"""
Elasticsearch lab
-----------------
"""
from __future__ import print_function

import re
import glob

from setuptools import setup, find_packages


def match_feature_name(filename):
    return re.match(r".*requirements-(\w+).txt$", filename).group(1)


def match_egg_name_and_version(dependency_link, version='=='):
    return version.join(
        re.sub(
            r'.+://.*[@#&]egg=([^&]*)&?.*$',
            r'\1',
            dependency_link
        ).rsplit('-', 1))


def read_requirements(filename='requirements.txt'):
    req = []
    dep = []
    with open(filename, 'r') as f:
        for line in f.readlines():
            line = line.strip('\n')
            if line.startswith('#'):
                continue
            if '://' in line:
                dep.append(str(line))
                req.append(match_egg_name_and_version(str(line)))
            else:
                req.append(str(line))
    return req, dep

install_requires, dependency_links = read_requirements()

# Finds all `requirements-*.txt` files and prepares dictionary with extra
# requirements (NOTE: no links are allowed here!)
extras_require = dict(map(
    lambda filename: (match_feature_name(filename),
                      read_requirements(filename)[0]),
    glob.glob('requirements-*.txt')))

packages = find_packages(exclude=['docs'])

setup(
    name='Elasticsearch Lab',
    version='0.0.0',
    license='GPLv2',
    author='RERO',
    author_email='Johnny.Mariethoz@rero.ch',
    description='Search interface for elasticsearch',
    long_description=__doc__,
    packages=packages,
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=install_requires,
    dependency_links=dependency_links,
    extras_require=extras_require,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GPLv2 License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ]
)
