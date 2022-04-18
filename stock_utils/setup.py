from setuptools import setup

setup(
   name='stock_utils',
   version='1.0',
   description='Utilities for the services of the project',
   author='Leo',
   author_email='leonardolg95m@gmail.com',
   packages=['models'],
   install_requires=['sqlalchemy', 'alembic']
)