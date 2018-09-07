#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, g, request, jsonify, abort
from flask_policy import Policy, PolicyNotAuthorized


app = Flask(__name__)
# The initial'demo.cfg' is generated using flask-policy cli.
app.config.from_pyfile('demo.cfg')
policy = Policy(app)


# simulate db
users = [
    {
        'id': '83cfbb3e6231444296288bd77410c82b',
        'name': 'lily',
        'roles': ['user', 'admin']
    },
    {
        'id': 'ad903ac3cf404279be6861cf155fe033',
        'name': 'kate',
        'roles': ['user']
    },
    {
        'id': '27973016ca404cedbcf429174cf46c1a',
        'name': 'jim',
        'roles': ['user']
    }
]

articles = [
    {
        'id': 'd45e75f27f184882afd6c5770b8e1ed8',
        'title': 'Core Python Programming',
        'user_id': 'ad903ac3cf404279be6861cf155fe033'
    }
]


@policy.register_credential_handler
def get_credential_handler():
    me = request.args.get('me')  # user id or name

    for user in users:
        if me in (user['id'], user['name']):
            return user
    else:
        return {}


@app.errorhandler(PolicyNotAuthorized)
def policy_disallow_handler(error):
    return jsonify({
        'error': str(error)
    })


@app.route('/', methods=['GET'])
def index():
    # login required
    return 'Welcome to Flask-Policy demo page!'


@app.route('/users', methods=['GET'], endpoint='user')
def list_users():
    # only admin allowed
    return jsonify({
        'users': users
    })


@app.route('/article/<article_id>', methods=['DELETE'], endpoint='article')
def delete_article(article_id):
    # only admin or article owner allowed
    article = None
    for _article in articles:
        if _article['id'] == article_id:
            article = _article
            break
    else:
        abort(404)

    # Outside of this view function, flask-policy can't know what
    # the target is to operate. So we need to enforce fine-grained
    # policy rule manually.
    policy.enforce('delete_article', article, g.policy_cred)
    # do delete here
    return "article %s deleted." % article['title']


if __name__ == '__main__':
    app.run(port=8888, debug=True)
