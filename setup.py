#!/usr/bin/env python
import setuptools
from distutils.core import setup

LONG_DESC = \
"""sostore is a straightforward storage engine for storing and retrieving 
dictionaries from an SQLite database.  Much of the terminology is taken
from MongoDB as this engine was originally designed to replace a PyMongo
implementation.

This library may seem trivial because it very much is.  However, some 
others may need a super-lightweight dictionary store.  Linking of 
objects within the database is not supported unless explicitly handled 
by the developer.

sostore is almost certainly not performant.  It can be thread-safe as 
long as Collection objects aren't passed around between threads as they
contain sqlite3.Connection objects.
"""

setup(name='sostore',
      version='0.4',
      description='SQLite Object Store - An absurdly simple object "database" for Python',
      long_description=LONG_DESC,
      author='Jeffrey Armstrong',
      author_email='jeffrey.armstrong@approximatrix.com',
      url='https://github.com/ArmstrongJ/sostore',
      packages=['sostore',],
      test_suite='tests.suite',
      
      license='GPL3',
      classifiers=[
          'Topic :: Database',
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
      ],
      
     )
     
