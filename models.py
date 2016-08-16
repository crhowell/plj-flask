import datetime

from flask_bcrypt import generate_password_hash
from flask_login import UserMixin
from peewee import *

DATABASE = SqliteDatabase('journal.db')


class User(UserMixin, Model):
    username = CharField(unique=True)
    email = CharField(unique=True)
    password = CharField(max_length=120)
    created_at = DateTimeField(default=datetime.datetime.now)
    last_modified = DateTimeField(default=datetime.datetime.now)
    is_admin = BooleanField(default=False)

    class Meta:
        database = DATABASE

    @classmethod
    def create_user(cls, username, email, password, admin=False):
        try:
            cls.create(
                username=username,
                email=email,
                password=generate_password_hash(password),
                is_admin=admin)
        except IntegrityError:
            raise ValueError("User already exists")


class Entry(Model):
    title = CharField(max_length=100)
    date = DateField(default=datetime.datetime.today)
    time_spent = IntegerField()
    learned = TextField(default='')
    resources = TextField(default='')
    tags = CharField(default='')
    user = ForeignKeyField(User, related_name='entries')

    class Meta:
        database = DATABASE


def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User, Entry], safe=True)
    DATABASE.close()
