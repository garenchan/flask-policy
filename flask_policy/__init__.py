# -*- coding: utf-8 -*-
"""
    flask_policy
    ~~~~~~~~~~~~

    RBAC management for Flask applications.

"""

__all__ = ['Policy', 'PolicyNotAuthorized', 'register', 'Check']

from flask import Flask, g, request
from policy import Enforcer, checks
from policy.exceptions import PolicyNotAuthorized

from flask_policy import _utils


register = checks.register

Check = checks.Check


class Policy(object):
    """This class is used to integrate Flask application with Policy."""

    def __init__(self, app=None, exc=None):
        self.app = None
        self._enforcer = None

        # While access disallowed, the exception to raise, you can
        # custom it with a exception has three positional arguments,
        # (rule, target, cred).
        self._disallow_exc = exc or PolicyNotAuthorized
        # The callback used for get current credential.
        self._get_credential_handler = None

        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask):
        self.app = app
        app.before_request(self._before_request)
        policy_file = app.config.setdefault('POLICY_POLICY_FILE', 'policy.json')
        default_rule = app.config.setdefault('POLICY_DEFAULT_RULE', None)
        raise_error = app.config.setdefault('POLICY_RAISE_ERROR', True)
        # In debug mode, we enable dynamic refresh for policy file
        load_once = app.config.setdefault('POLICY_LOAD_ONCE', app.debug)
        self._enforcer = Enforcer(policy_file, default_rule=default_rule,
                                  raise_error=raise_error, load_once=load_once)

        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['policy'] = self

    @property
    def policy_file(self):
        """Get current policy file."""

        return self._enforcer.policy_file

    def _before_request(self):
        endpoint = request.endpoint
        if not endpoint:
            return

        rule = _utils.build_endpoint_rule_name(endpoint, request.method)
        cred = self._get_credential_handler()
        allowed = self.enforce(rule, {}, cred)
        # While disallow and not raise error, inject result into `g`,
        # then we can trace result from here.
        g.policy_allowed = allowed

    def enforce(self, rule: str, target, cred, exc=None, *args, **kwargs):
        """Enforce policy rule on specified target with credential.

        By default, flask-policy only works automatically outside the
        view functions. It provides a view-level access control which
        is coarse-grained. If you want a more fine-grained control, you
        may need to manually enforce rules on the points which you wish.

        :param rule: the name of a rule.
        :param target: the rule's target, a dict or other objects.
        :param cred: the credential of current user, a dict or other objects.
        :param exc: if result is disallowed, the exception to raise, only works
                    when POLICY_RAISE_ERROR is set to True.
        :param args: positional arguments of above exception.
        :param kwargs: keyword arguments of above exception.
        :return: result of the policy rule, bool type.
        """

        if not exc:
            exc = self._disallow_exc
            args = (rule, target, cred)

        return self._enforcer.enforce(rule, target, cred, exc, *args, **kwargs)

    def register_credential_handler(self, func):
        """Register a handler for get current credential."""

        def wrapper():
            """Wrapper for credential handler.

            In a request, we may enforce rules and execute handler
            multiple times.If the execution of the handler is time-consuming,
            it will have a great negative impact on performance. So
            we cache the credential in request lifetime.
            FIXME: credential may change in request lifetime.
            """
            if not hasattr(g, 'policy_cred'):
                g.policy_cred = func()

            return g.policy_cred

        self._get_credential_handler = wrapper
        return func
