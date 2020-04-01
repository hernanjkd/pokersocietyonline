import os
from flask import Flask, request, jsonify, url_for, render_template
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from admin import SetupAdmin
from utils import APIException, generate_sitemap
from models import db, Users, Referrals
import requests


app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
SetupAdmin(app)

@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code


@app.route('/payment/methods', methods=['POST'])
def payment_data():
    
    j = request.get_json()

    # Validation
    checklst = ['first_name', 'last_name', 'username','email',
        'referral_id', 'payment_types']
    for prop in checklst:
        if prop not in j:
            raise APIException('Missing property '+ prop)

    user = Users.query.filter_by( email=j['email'] ).first()
    if user is not None:
        raise APIException('This email is already in our system')

    # Arrange data
    user_data = {
        'first_name': j['first_name'],
        'last_name': j['last_name'],
        'username': j['username'],
        'email': j['email'],
        'referral_id': j['referral_id'] or None,
        'payment_types': ' '.join( j['payment_types'] )
    }

    # Send email
    key = os.environ.get('MAILGUN_API_KEY')
    domain = os.environ.get('MAILGUN_DOMAIN')

    refs = Referrals.query.filter_by( referral_id=j['referral_id'] )
    referral_emails = [x.email for x in refs]
    emails = [
        'aylinmaria2501@hotmail.com',#'play@thepokersociety.com',
        *referral_emails
    ]

    resp = requests.post(f'https://api.mailgun.net/v3/{domain}/messages',
        auth=('api', key),
        data={
            'from': 'PokerSocietyOnline<play@thepokersocietyonline.com>',
            'to': emails,
            'subject': 'PokerBros New User',
            'text': render_template('payment_methods.txt'),
            'html': render_template('payment_methods.html', 
                **user_data,
                referral_emails = ' '.join(referral_emails) \
                    if referral_emails else None
            )
        })
    if not resp.ok:
        raise APIException('There was a problem processing your information')

    # Save data
    db.session.add( Users( **user_data ))
    db.session.commit()

    return jsonify({'processed': True})


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
    app.run(debug=True)
