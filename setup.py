from setuptools import setup

setup(
   name='pysmt_sim',
   description='Generate C++ simulation program for pySMT formula',
   author='Yu-Neng Wang',
   author_email='wynwyn@stanford.edu',
   packages=['pysmt_sim'],
   install_requires=['pysmt']
)