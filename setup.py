#!/usr/bin/env python3

from distutils.core import setup

setup( name='nullunit',
       description='MCP Agent',
       author='Peter Howe',
       version='0.1',
       author_email='peter.howe@emc.com',
       packages=[ 'nullunit', 'nullunit.scoring' ],
       )
