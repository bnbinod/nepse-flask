import os


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'afjaofeijaf8(*J(C**EC*('
    # Postgres username, password, and database name
    POSTGRES_ADDRESS = '202.45.146.72'
    POSTGRES_PORT = '8995'
    POSTGRES_USERNAME = 'warehouse'
    POSTGRES_PASSWORD = 'Qw23@E#R'
    POSTGRES_DBNAME = 'history'
    # A long string that contains the necessary Postgres login information
    SQLALCHEMY_DATABASE_URI = ("postgresql://{username}:{password}@{ipaddress}:{port}/{dbname}".format(username=POSTGRES_USERNAME,
                                                                                            password=POSTGRES_PASSWORD,
                                                                                            ipaddress=POSTGRES_ADDRESS,
                                                                                            port=POSTGRES_PORT,
                                                                                            dbname=POSTGRES_DBNAME))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ITEMS_PER_PAGE = 20

    MAIL_SERVER = os.environ.get('MAIL_SERVER') or "smtp.googlemail.com"
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 465)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or "visit.signup@gmail.com"
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or "1@dangerous"
    ADMINS = ['visit.binod@gmail.com']
    LANGUAGES = ['en', 'es']
    MS_TRANSLATOR_KEY = os.environ.get('MS_TRANSLATOR_KEY') or ""
