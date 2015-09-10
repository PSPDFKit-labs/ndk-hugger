#!/usr/bin/env python2
from setuptools import setup

setup(name='ndkhugger',
      version="0.0.1",
      packages=['ndkhugger'],
      install_requires=['click==5.1','wheel==0.24.0'],
      entry_points={ 'console_scripts': ['nhgr=ndkhugger.hugger:run']}
)
