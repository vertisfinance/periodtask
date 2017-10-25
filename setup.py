from setuptools import setup
import os
# import io


here = os.path.abspath(os.path.dirname(__file__))
# with io.open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
#     long_description = '\n' + f.read()

setup(
    name='periodtask',
    description='Periodic task with timezone',
    version='0.0.1',
    # url='https://github.com/richardbann/aiowstunnel',
    # author='Richard Bann',
    # author_email='richardbann@gmail.com',
    # classifiers=[
    #     'License :: OSI Approved :: MIT License',
    #     'Programming Language :: Python :: 3.6'
    # ],
    # keywords='tunneling TCP websocket',
    zip_safe=False,
    install_requires=[
        'pyyaml >= 3.12',
        'pytz >= 2017.2'
    ],
    package_data={'docron': ['*.html']},
    # license='MIT',
    packages=['docron'],
    entry_points={
        'console_scripts': ['docron=docron.docron:start']
    },
)
