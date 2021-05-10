from flask_login import UserMixin
from . import db, login_manager
from . import config
import base64

@login_manager.user_loader
def load_user(user_id):
    return User.objects(username=user_id).first()

class User(db.Document, UserMixin):
    username = db.StringField(required=True, unique=True)
    email = db.EmailField(required=True, unique=True)
    password = db.StringField(required=True)
    profile_pic = db.ImageField()

    def get_id(self):
        return self.username

class Receipt(db.Document):
    user = db.ReferenceField(User, required=True)
    date = db.StringField(require=True)
    receipt_img = db.ImageField(require=True)
    cost = db.FloatField(required=True)
    category = db.StringField(require=True)
    hash = db.IntField(required=True)
    description = db.StringField(required=True)

