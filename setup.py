#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Flask-Policy
--------------

Access control management for Flask applications.
Simple, flexible, plug and play.
"""
from setuptools import setup


def get_classifiers():
    return [
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ]


if __name__ == '__main__':
    setup(
        name='Flask-Policy',
        version='1.0.0',
        description='Access control management for Flask applications.',
        long_description=__doc__,
        author='garenchan',
        author_email='1412950785@qq.com',
        url='https://github.com/garenchan/flask-policy',
        license='http://www.apache.org/licenses/LICENSE-2.0',
        classifiers=get_classifiers(),
        packages=['flask_policy'],
        zip_safe=False,
        platforms='any',
        install_requires=[
            'Flask>=0.10',
            'policy'
        ],
        entry_points={
            'flask.commands': [
                'policy=flask_policy.cli:policy_cli'
            ]
        }
    )
