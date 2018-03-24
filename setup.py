from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.txt'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='prettypandas',

    version='0.0.4',

    description='Pandas Styler for Report Quality Tables.',
    long_description=long_description,

    url='https://github.com/HHammond/PrettyPandas',

    author='Henry Hammond',
    author_email='henryhhammond92@gmail.com',

    license='MIT',

    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    keywords='pandas pretty display tables reporting',

    packages=["prettypandas"],

    install_requires=[
        "babel",
        "numpy",
        "pandas >= 0.17.1"
    ],
)
