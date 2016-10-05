# -*- coding: UTF-8 -*-
class config:
    SECRET_KEY = 'interesting'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_ECHO = True
    PREFIX = 'flasky_vanshin'
    SENDER = 'kfx721@163.com'
    MAIL_SERVER = 'smtp.163.com'
    MAIL_PORT = 25
    MAIL_USERNAME = 'kfx721@163.com'
    MAIL_PASSWORD = 'mail520624'
    ADMIN = '415203893@qq.com'
    PATH = '/static/pic'
    FLASKY_PER_PAGE = 15
    FLASKY_FOLLOWERS_PER_PAGE = 15
    FLASKY_COMMENTS_PER_PAGE = 15
    PICPATH = '/var/www/flask.com/app/static/pic' 
    @staticmethod
    def init_app(app):
        pass

class DevelopConfig(config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:0000@127.0.0.1:3306/flaskdev'

class TestingConfig(config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:0000@127.0.0.1:3306/test'

class ProductionConfig(config):
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:0000@127.0.0.1:3306/flaskBlog'

config = {
    'development':DevelopConfig,
    'testing':TestingConfig,
    'production':ProductionConfig,
    'default':DevelopConfig
}
