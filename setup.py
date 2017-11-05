from setuptools import setup, find_packages


setup(
    name='cncparser',
    version='0.2',
    description='Python package to parse and process prima power cnc reports',
    author='Dmitriy Bychkov',
    author_email='isumenam@gmail.com',
    packages=find_packages(exclude=('tests',)),
    install_requires=['lxml>=3.7'],
)
