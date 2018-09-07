# -*- coding: utf-8 -*-
"""
    flask_policy._utils
    ~~~~~~~~~~~~~~~~~~~

    Some utils for internal use.

"""


def build_endpoint_rule_name(endpoint, method):
    """Build policy rule name for endpoint."""

    return ('%(endpoint)s:%(method)s' %
            {'endpoint': endpoint, 'method': method.lower()})
