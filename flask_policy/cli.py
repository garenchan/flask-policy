# -*- coding: utf-8 -*-
"""
    flask_policy.cli
    ~~~~~~~~~~~~~~~~

    Inject policy-related commands to flask application.
    Such as, generate default policy file.

"""

import os
import json
from collections import OrderedDict

import click
from flask import current_app
from flask.cli import cli, AppGroup, with_appcontext
from policy import checks

policy_cli = AppGroup('policy')


@policy_cli.command('generate')
@click.option('-f', '--policy-file', default='policy.json',
              help='Filename of policy file (default is "policy.json")')
@click.option('--allow/--disallow', default=True,
              help='By default, all rules are allowed or not')
@click.option('--mode', type=click.Choice(['safe', 'overwrite', 'update', 'append']),
              help='When policy file already exists, do nothing or over write')
def generate_policy_file(policy_file, mode, allow):
    """Generate default policy file."""

    file_existed = os.path.exists(policy_file)
    if file_existed and mode in ['safe', None]:
        raise Exception(('Policy file %r already exists, set mode to '
                         '[overwrite/update/append] for updating it' % policy_file))

    policy_rules = OrderedDict()
    default = str(checks.TrueCheck() if allow else checks.FalseCheck())
    for rule in current_app.url_map.iter_rules():
        for method in rule.methods:
            name = ('%(endpoint)s:%(method)s' %
                    {'endpoint': rule.endpoint, 'method': method.lower()})
            policy_rules[name] = default

    if file_existed and mode in ['update', 'append']:
        if not policy_rules:
            return
        else:
            with open(policy_file, 'r') as fp:
                orig_policy_rules = json.load(fp, object_pairs_hook=OrderedDict)
            if mode == 'update':
                orig_policy_rules.update(policy_rules)
            else:
                for key, value in policy_rules.items():
                    if key in orig_policy_rules:
                        continue
                    orig_policy_rules[key] = value
            policy_rules = orig_policy_rules

    with open(policy_file, 'w') as fp:
        json.dump(policy_rules, fp, indent=4)
