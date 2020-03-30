from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin
from models import db, Users, Referrals


def SetupAdmin(app):

    class ExcludedModelView(ModelView):
        form_excluded_columns = ['created_at', 'updated_at']
    
    admin = Admin(app, name='Swap Profit', template_mode='bootstrap3')

    admin.add_view( ExcludedModelView( Users, db.session ))
    admin.add_view( ExcludedModelView( Referrals, db.session ))

    return admin