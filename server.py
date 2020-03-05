import base64
import os
import datetime
import json
import time
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify



import urllib


app = Flask(__name__)

client_id = 'bb7c475418484e7784d9cd25b5f9f52c'
client_secret = 'b0da0baeeab1499884912aea11f4ca58'


@app.route('/login/')


def credentials():
     client_id = 'bb7c475418484e7784d9cd25b5f9f52c'
     client_secret = 'b0da0baeeab1499884912aea11f4ca58'
     auth_header = base64.b64encode(six.text_type(client_id + ":" + client_secret).encode("ascii"))
     return render_template('index.html')




if __name__ == '__main__':  # ensure function only runs if executed from the python interpreter
    app.secret_key = 'super_secret_key2'
    app.debug = True        # server will reload itself whenever a change is made
    app.run(host = '0.0.0.0' , port = 5000)

