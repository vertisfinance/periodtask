from setuptools import setup
import os
import io


here = os.path.abspath(os.path.dirname(__file__))

with io.open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = '\n' + f.read()

# with io.open(os.path.join(here, 'VERSION'), encoding='utf-8') as f:
#     VERSION = f.read().strip()
VERSION = '0.5.5'

setup(
    name='periodtask',
    description='Periodic task with timezone',
    long_description=long_description,
    version=VERSION,
    url='https://github.com/vertisfinance/periodtask',
    author='Richard Bann',
    author_email='richard.bann@vertis.com',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6'
    ],
    install_requires=[
        'pytz >= 2018.5',
        'mako == 1.0.7',
    ],
    license='MIT',
    packages=['periodtask'],
    package_data={
        '': ['templates/*', 'VERSION'],
    }
)
