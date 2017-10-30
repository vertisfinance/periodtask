from setuptools import setup
import os
import io


here = os.path.abspath(os.path.dirname(__file__))

with io.open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = '\n' + f.read()

setup(
    name='periodtask',
    description='Periodic task with timezone',
    long_description=long_description,
    version='0.2.0',
    url='https://github.com/vertisfinance/periodtask',
    author='Richard Bann',
    author_email='richard.bann@vertis.com',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6'
    ],
    install_requires=[
        'pytz >= 2017.2',
        'mako == 1.0.7',
    ],
    license='MIT',
    packages=['periodtask'],
)
