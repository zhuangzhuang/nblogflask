import os

mongo_param = {
    'db': 'nblog',
    #'host': '127.0.0.1',
    #'port': 123
}

basedir = os.path.dirname(__file__)

UPLOAD_FOLDER = os.path.join(basedir, 'upload')
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])