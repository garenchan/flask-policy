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
from flask.cli import AppGroup
from policy import checks

from flask_policy import _utils


policy_cli = AppGroup('policy')


@policy_cli.command('generate')
@click.option('-f', '--policy-file', default='',
              help='Filename of policy file (default is "policy.json")')
@click.option('--allow/--disallow', default=True,
              help='By default, all rules are allowed or not')
@click.option('-m', '--mode', type=click.Choice(['safe', 'overwrite', 'update', 'append']),
              help='When policy file already exists, do nothing or over write')
def generate_policy_file(policy_file, mode, allow):
    """Generate default policy file."""

    # If policy file option not set, we use the app's policy extension's setting.
    if not policy_file:
        policy_ext = getattr(current_app, 'extensions', {}).get('policy')
        if policy_ext:
            policy_file = policy_ext.policy_file
        if not policy_file:
            raise RuntimeError('Policy file is required!')

    file_existed = os.path.exists(policy_file)
    if file_existed and mode in ['safe', None]:
        raise Exception(('Policy file %r already exists, set mode to '
                         '[overwrite/update/append] for updating it' % policy_file))

    policy_rules = OrderedDict()
    default = str(checks.TrueCheck() if allow else checks.FalseCheck())
    for rule in current_app.url_map.iter_rules():
        for method in rule.methods:
            name = _utils.build_endpoint_rule_name(rule.endpoint, method)
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
