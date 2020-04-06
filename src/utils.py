from flask import jsonify

class APIException(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


def sort_by_date(a, b):
    a = dt.strptime(a['title'], 'Week of %b %d')
    b = dt.strptime(b['title'], 'Week of %b %d')
    if int(a.strftime('%m')) == int(b.strftime('%m')):
        return int(b.strftime('%d')) - int(a.strftime('%d'))
    else:
        return int(b.strftime('%m')) - int(a.strftime('%m'))