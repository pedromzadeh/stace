from setuptools import setup

setup(
   name='stace',
   version='1.0',
   description='Statistical module for cbwins',
   packages=['stace'],  #same as name
   install_requires=['numpy', 'pandas', 'plotly', 'matplotlib'], #external packages as dependencies
)