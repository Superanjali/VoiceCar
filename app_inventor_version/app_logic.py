# -*- coding: utf-8 -*-
"""
Created on Sun Jan  6 13:42:10 2019

@author: Sophia
"""

import flask
app = flask.Flask(__name__)
app.secret_key = 'voicy'

@app.route('/', methods=['POST','GET'])
#@app.route('/')
def page():
    with open('command.txt') as f:
        command = f.read()
    
    new_command = flask.request.args.get('key', None)
    if new_command is not None:
        command = new_command
        with open('command.txt','w') as f:
            f.write(new_command)

    return command
    