import sys

from setuptools import find_packages
from setuptools import setup


install_requires = [
    'setuptools',
]
if sys.version_info < (3, 4):
    install_requires.append('trollius')
package_excludes = ['tests*', 'docs*']
if sys.version_info < (3, ):
    # On non-Python3 installs, avoid installing the asyncio files
    # which contain Python3 specific syntax.
    package_excludes.append(
        'osrf_pycommon.process_utils.async_execute_process_asyncio'
    )
packages = find_packages(exclude=package_excludes)

setup(
    name='osrf_pycommon',
    version='0.1.2',
    packages=packages,
    install_requires=install_requires,
    author='William Woodall',
    author_email='william@osrfoundation.org',
    maintainer='William Woodall',
    maintainer_email='william@osrfoundation.org',
    url='http://osrf-pycommon.readthedocs.org/',
    keywords=['osrf', 'utilities'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
    ],
    description="Commonly needed Python modules, "
                "used by Python software developed at OSRF",
    license='Apache 2.0',
    test_suite='tests',
)
