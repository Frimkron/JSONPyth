#!/usr/bin/env python3

from setuptools import setup, find_packages


with open('requirements.txt', 'r') as f:
    requirements = [l.strip() for l in f.readlines()]

with open('README.md', 'r') as f:
    long_description = f.read()


setup(
    name='JSONPyth',
    version='0.1.0',
    py_modules=['jsonpyth'],
    author='Mark Frimston',
    author_email='mfrimston@gmail.com',
    description='A JSONPath implementation for Python',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT',
    keywords='json jsonpath xpath query',
    url='https://github.com/Frimkron/JSONPyth',
    python_requires = '>=3.5',
    install_requires = requirements,
    test_suite='tests',
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
