from setuptools import setup
import os
import io


here = os.path.abspath(os.path.dirname(__file__))

with io.open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = '\n' + f.read()

VERSION = '0.8.0'

setup(
    name='vertis_periodtask',
    description='Periodic task with timezone',
    long_description=long_description,
    version=VERSION,
    url='https://github.com/vertisfinance/periodtask',
    author='Egyed Gábor',
    author_email='gabor.egyed@vertis.com',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8'
    ],
    install_requires=[
        'pytz >= 2021.1',
        'mako == 1.2.2',
    ],
    license='MIT',
    packages=['periodtask'],
    package_data={
        '': ['templates/*', 'VERSION'],
    }
)
