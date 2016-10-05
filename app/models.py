# -*- coding: UTF-8 -*-
from . import db
from werkzeug.security import generate_password_hash,check_password_hash
from . import login_manager
from flask_login import UserMixin,AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from datetime import datetime
from markdown import markdown
import bleach

class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTR = 0x80

class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer,primary_key=True)
    body = db.Column(db.Text)
    author_id = db.Column(db.Integer,db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer,db.ForeignKey('posts.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class User(UserMixin,db.Model):
    __tablename__ = 'users'
    id  = db.Column(db.Integer,primary_key=True)
    email = db.Column(db.String(64),unique=True,index=True)
    name = db.Column(db.String(64),unique=True,index=True)
    password_hash = db.Column(db.String(128))
    roles_id = db.Column(db.Integer,db.ForeignKey('roles.id'))
    confirmed = db.Column(db.Boolean,default=False)
    realname = db.Column(db.String(64),index=True)
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(),default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(),default=datetime.utcnow)
    avator = db.Column(db.String(64))
    post = db.relation('Post',backref='author',lazy='dynamic')
    comment = db.relation('Comment',backref='author',lazy='dynamic')

    followed = db.relationship('Follow',foreign_keys=[Follow.follower_id],
                                backref=db.backref('follower',lazy='joined'),
                                lazy='dynamic',
                                cascade='all,delete-orphan')
    followers = db.relationship('Follow',foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed',lazy='joined'),
                                lazy='dynamic',
                                cascade='all,delete-orphan')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['ADMIN']:
                self.role = Role.query.filter_by(permission=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    @property
    def password(self):
        raise AttributeError('can not read password')

    @password.setter
    def password(self,password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)
    # 回调函数，使用指定的标识符加载用户
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    def generate_confirmation_token(self,expiration=3600):
        # 生成一个加密的类的实例
        s = Serializer(current_app.config['SECRET_KEY'],expiration)
        # 对id进行加密
        return s.dumps({'confirm':self.id})
    
    def confirm(self,token):
        # 生成实例
        s = Serializer(current_app.config['SECRET_KEY'])
        # 用token进行解密
        try:
            data = s.loads(token)
            
        # 过期的话就直接返回 False 
        except:
            return False
        # 比较id是否相同
        if data.get('confirm') != self.id:
            return False
        else:
            self.confirmed = True
        # 对数据库进行改动
        db.session.add(self)    
        return True

    def generate_reset_token(self,expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'],expiration)
        return s.dumps({'reset':self.id})
    
    def gengerate_resetEmail_token(self,expitation=3600):
        s = Serializer(current_app.config['SECRET_KEY'],expiration)
        return s.dumps({'email':self.email})

    def reset_password(self,token,new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def change_pass(self,new_password):
        self.password = new_password
        db.session.add(self)
        return True

    def get_userid(self,token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        return data.get('reset')

    def reset_email(self,new_email):
        self.email = new_email
        db.session.add(self)
        return True
    
    def can(self, permission):
        return self.role is not None and (self.role.permission & permission) == permission

    def is_administrator(self):
        return self.can(Permission.ADMINISTR)
    @staticmethod
    def generate_fake(count):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py
        seed()
        for i in range(count):
            u = User(email=forgery_py.internet.email_address(),
                name=forgery_py.internet.user_name(True),
                password=forgery_py.lorem_ipsum.word(),
                confirmed=True,
                realname=forgery_py.name.full_name(),
                location=forgery_py.address.city(),
                about_me=forgery_py.lorem_ipsum.sentence(),
                member_since=forgery_py.date.date(True))
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
    def is_following(self,user):
        return self.followed.filter_by(followed_id=user.id).first() is not None

    def is_followed_by(self,user):
        return self.followers.filter_by(follower_id=user.id).first() is not None

    def follow(self,user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)
    
    def unfollow(self,user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)

    @property
    def followed_posts(self):
        return Post.query.join(Follow,Follow.followed_id == Post.author_id).filter(Follow.follower_id == self.id)

    def __repr__(self):
        return '<User %r>' % self.name



class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer,primary_key=True)
    body = db.Column(db.Text)
    head = db.Column(db.String(64))
    author_id = db.Column(db.Integer,db.ForeignKey('users.id'))
    timestamp = db.Column(db.DateTime(),index=True,default=datetime.utcnow)
    body_html = db.Column(db.Text)
    comment = db.relationship('Comment',backref='post',lazy='dynamic')
    @staticmethod
    def generate_fake(count):
        from random import seed, randint
        import forgery_py
        seed()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0, user_count - 1)).first()
            p = Post(body=forgery_py.lorem_ipsum.sentences(randint(1, 3)),
                timestamp=forgery_py.date.date(True),
                author=u,
                head=forgery_py.lorem_ipsum.title())
        db.session.add(p)
        db.session.commit()

    @staticmethod
    def onchange_html(target,value,old_value,initiator):
        allow_tag = [
            'a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
            'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
            'h1', 'h2', 'h3', 'p'
        ]
        target.body_html = bleach.linkify(
            bleach.clean(markdown(value,output_format='html'),tags=allow_tag,strip=True))
# 每次有body添加到数据库，都会被自动转换成html格式
db.event.listen(Post.body,'set',Post.onchange_html)

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(64),unique=True)
    # 定义到User类的视角，此属性返回所有与当前role所关联的所有users
    users = db.relationship('User',backref='role',lazy='dynamic')
    permission = db.Column(db.Integer)
    default = db.Column(db.Boolean,default=False,index=True)
    def __repr__(self):
        return '<Role %r>' % self.username
    
    @staticmethod
    def insert_role():
        roles = {
            'User': (Permission.FOLLOW | Permission.COMMENT | Permission.WRITE_ARTICLES,True),
            'Moderator':(Permission.FOLLOW | Permission.COMMENT | Permission.WRITE_ARTICLES | Permission.MODERATE_COMMENTS,False),
            'Administrator':(0xff,False)

        }
        for r in roles:
            role = Role.query.filter_by(username=r).first()
            if role is None:
                role = Role(username=r)
            role.permission = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)    
        db.session.commit()
    




class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False
    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
