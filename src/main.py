"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
# from models import db
import requests


app = Flask(__name__)
app.url_map.strict_slashes = False
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# MIGRATE = Migrate(app, db)
# db.init_app(app)
CORS(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/mailgun', methods=['POST'])
def mailgun():
    emails = request.get_json().get('emails')
    if emails is None:
        return 'Send {"emails":[]}'

    key = os.environ.get('MAILGUN_API_KEY')
    domain = os.environ.get('MAILGUN_DOMAIN')

    logs = []
    for email in emails:
        ok = requests.post(f'https://api.mailgun.net/v3/{domain}/messages',
            auth=('api', key),
            data={
                'from': f'{domain} <mailgun@swapprofit.herokuapp.com>',
                'to': email,
                'subject': 'Testing',
                'text': 'Hello World',
                'html': '<h1>Hello World</h1>'
            }).status_code == 200
        logs.append({'email':email,'ok':ok})

    return jsonify(logs)

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
