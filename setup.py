from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='dish',
      version=version,
      description="Distributed shared memory tools",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='distributed shared memory quorum',
      author='Matthew Desmarais',
      author_email='matthew.desmarais@gmail.com',
      url='',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'eventlet',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
