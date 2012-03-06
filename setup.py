#!/usr/bin/env python
#-*- coding: utf-8 -*-

from setuptools import setup
from setuptools import find_packages

setup (
        name = 'chiup',
        version = '0.1',
        description = 'chiup is a upload tool for chishop to upload the pre-compile egg file to local repository.',
        packages = find_packages (),
        long_description = open ('README.rst').read(),
        author = 'Kerberos Zhang',
        author_email = 'kerberos.zhang@gmail.com',
        license = 'BSD License',
        keywords = ['egg', 'pypi', 'chishop'],
        platform = 'Independant',
        url = 'https://github.com/imkerberos/chiup',
        classifiers = [
            "Programming Language :: Python",
            "Development Status :: 3 - Alpha",
            "Environment :: Console"
        ],
        zip_safe = True,
        install_requires = ['pkgtools'],
        entry_points  = """
            [console_scripts]
            chiup = chiup.chiup:main
        """
)
