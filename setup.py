#! -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='bytepiece',
    version='0.0.0',
    description='Smarter Bytes-based Tokenizer',
    long_description='BytePiece: https://github.com/bojone/bytepiece',
    license='Apache License 2.0',
    url='https://github.com/bojone/bytepiece',
    author='bojone',
    author_email='bojone@spaces.ac.cn',
    install_requires=['numpy', 'tqdm'],
    packages=find_packages()
)
