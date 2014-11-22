from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(
    name='ckanext-more-facets',
    version=version,
    description="Shows Organizations by Government Level",
    long_description='''
    ''',
    classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='',
    author='Julio Acuna',
    author_email='urkonn@gmail.com',
    url='',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=['ckanext', 'ckanext.govtypes'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
    ],
    entry_points='''
        [ckan.plugins]
        # Add plugins here, e.g.
        # myplugin=ckanext.govtypes.plugin:PluginClass
        gov_type=ckanext.govtypes.plugin:GovLevelVocabPlugin
    ''',
)
