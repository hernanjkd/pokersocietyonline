import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from models import db, Users
import requests


app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)

@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code


@app.route('/payment/data', methods=['POST'])
def payment_data():

    j = request.get_json()

    return jsonify(j)


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
                'from': 'PokerSocietyOnline<play@thepokersocietyonline.com>',
                'to': email,
                'subject': 'Play Online',
                'text': 'Hello World',
                'html': '<h1>Mr Lou</h1><p>This is an automated generated email from your new app ;) reaching your hotmail and any other email address we send it to!</p><p>Send me later the email you want the players to receive with the title you want, and also what to write instead of "PokerSocietyOnline"</p>'
            }).status_code == 200
        logs.append({'email':email,'ok':ok})

    return jsonify(logs)


if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
