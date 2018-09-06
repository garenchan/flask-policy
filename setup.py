#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup


if __name__ == '__main__':
    setup(
        name='Flask-Policy',
        version='1.0.0',
        packages=['flask_policy'],
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
