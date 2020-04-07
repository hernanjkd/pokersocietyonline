from flask import Flask, request, jsonify, url_for, render_template
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from admin import SetupAdmin
from datetime import datetime as dt
from functools import cmp_to_key
from models import db, Users, Referrals
from utils import APIException
import utils as ut
import re
import os
import cloudinary
import cloudinary.uploader
import requests


app = Flask(__name__)
app.secret_key = os.environ['FLASK_KEY']
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

    email = j['email'].lower()

    user = Users.query.filter_by( email=j['email'] ).first()
    if user is not None:
        raise APIException('This email is already in our system')

    # Arrange data
    user_data = {
        'first_name': j['first_name'].title(),
        'last_name': j['last_name'].title(),
        'username': j['username'],
        'email': email,
        'referral_id': j['referral_id'] or None,
        'payment_types': ' '.join( j['payment_types'] )
    }

    # Send email
    key = os.environ.get('MAILGUN_API_KEY')
    domain = os.environ.get('MAILGUN_DOMAIN')

    refs = Referrals.query.filter_by( referral_id=j['referral_id'] )
    referral_emails = [x.email for x in refs]
    emails = [
        'play@thepokersociety.com',
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


@app.route('/upload/files', methods=['GET','POST'])
def handle_images():

    if request.method == 'GET':
        return render_template('file_upload.html')

    img = request.files['image']

    public_id = img.filename[ : img.filename.index('.') ]
    tag = public_id[ public_id.index('- ')+1 : ]
    
    result = cloudinary.uploader.upload(
        img,
        public_id = public_id,
        crop = 'scale',
        tags = [ tag ]
    )
    
    return jsonify({'message':'Image processed'})


@app.route('/tournament/results')
def get_images():
    
    key = os.environ['CLOUDINARY_API_KEY']
    secret = os.environ['CLOUDINARY_API_SECRET']
    url = lambda tag: \
        f'https://api.cloudinary.com/v1_1/hvd3ubzle/resources/image/tags/{tag}?max_results=1000'
    

    data = { 'results': [], 'leaderboard': [], 'flyer': {} }
    
    for tag in data.keys():
        
        # requests cloudinary
        r = requests.get(url(tag), auth=(key, secret))
        if not r.ok:
            raise APIException('Problem requesting from cloudinary')
        
        # prepare data
        lst = r.json()['resources']
        for img in lst:
            n = img['public_id']
            title = n[ : n.index(' -') ]

            if tag == 'flyer':
                data[tag][title] = img['secure_url']
            else:
                data[tag].append({
                    'url': img['secure_url'],
                    'title': title
                })

        # sort data
        if tag != 'flyer':
            data[tag] = sorted( data[tag], 
                key = cmp_to_key( ut.sort_by_date ) )


    return jsonify(data)



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
