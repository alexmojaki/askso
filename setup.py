#!/usr/bin/env python
from codecs import open
from setuptools import setup

with open('README.rst', encoding='utf8') as readme_file:
    readme = readme_file.read()

setup(
    name='ask-so',
    version='1.0.4',
    description='AskSO - StackOverflow Python Question Assistant',
    long_description=readme,
    author='Alex Hall',
    author_email='alex.mojaki@gmail.com',
    license='MIT (Expat)',
    url='https://github.com/alexmojaki/askso',
    packages=['askso'],
    package_data={'': ['static/*']},
    include_package_data=True,
    entry_points={
        'console_scripts': ['askso=askso.server:main'],
    },
    install_requires=[
        'Flask >= 0.10.0, < 1.0.0',
    ],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
