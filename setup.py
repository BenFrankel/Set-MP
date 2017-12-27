#!/usr/bin/env python

from setuptools import setup, find_packages


version = '0.2.0'


with open('README.md') as f:
    long_description = f.read()


setup(
        name='Set-MP',
        version=version,

        description='Set card game',
        long_description=long_description,
        author='Ben Frankel',
        author_email='ben.frankel7@gmail.com',
        license='Apache 2.0',
        url='https://www.github.com/BenFrankel/hgf',
        download_url='https://www.github.com/BenFrankel/Set-MP/tarball/' + version,

        packages=find_packages(),
        install_requires=[
            'hgf (==0.2.0)',
        ],
        provides=[]
)
