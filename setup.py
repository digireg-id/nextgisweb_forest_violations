from setuptools import setup, find_packages
import sys, os

version = '0.0'

requires = (
    'nextgisweb',
)

entry_points = {
    'nextgisweb.packages': [
        'nextgisweb_forest_violations = nextgisweb_forest_violations:pkginfo',
    ],
}

setup(
    name='nextgisweb_forest_violations',
    version=version,
    description="",
    long_description="",
    classifiers=[],
    keywords='',
    author='',
    author_email='',
    url='',
    license='',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    entry_points=entry_points,
)
