import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='horizon-openfoam',
    version='1.0',
    packages=find_packages(),
    include_package_data=True,
    license='BSD License',
    description='OpenFOAM horizon dashboard app.',
    long_description=README,
    url='https://www.xlab.si/',
    author='XLAB d.o.o.',
    author_email='pypi@xlab.si',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=[
        'boto==2.43.0',
        'Django==1.8.16',
        'setuptools==20.7.0',
        'requests==2.12.1',
        'horizon==2012.2',
    ]
)
