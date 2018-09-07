#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Extend checks with http.
"""

import json
from urllib import request

from flask_policy import register, Check


@register('http')
class HTTPCheck(Check):
    """Check rules by calling to remote http server.
    """

    def __call__(self, target, creds, enforcer, current_rule=None):
        url = ('http:' + self.match) % target

        data = {
            'rule': current_rule,
            'target': target,
            'credentials': creds
        }
        headers = {
            'Content-Type': 'application/json'
        }
        # FIXME: `target` and `creds` can be any object, so may be not jsonable.
        req = request.Request(url, data=json.dumps(data).encode('utf-8'),
                              headers=headers)
        response = request.urlopen(req)
        # If the server return a string with 'true', means allowed
        return response.read().decode().strip().lower() == 'true'
