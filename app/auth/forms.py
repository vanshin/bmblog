# -*- coding: UTF-8 -*-
from flask_wtf import Form 
from wtforms import StringField,IntegerField,BooleanField,SubmitField,PasswordField,TextAreaField
from wtforms.validators import Required,Length,Email,Regexp,EqualTo

class LoginForm(Form):
    email = StringField('邮箱',validators=[Required(),Length(1,64),Email()])
    password = PasswordField('密码',validators=[Required()])
    remember_me = BooleanField('保持登录')
    submit = SubmitField('登录')

class RegistrationForm(Form):
    email = StringField('邮箱',validators=[Required(),Email(),Length(1,64)])
    name = StringField('用户名',validators=[Required(),Length(1,64),Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,'usernames must have only letters,numbers,dots pr undersocres')])
    password = PasswordField('密码',validators=[Required(),Length(1,64),EqualTo('password2',message='passwords must match.')])
    password2 = PasswordField('确认密码',validators=[Required()])
    submit = SubmitField('注册')

    # 自定义的验证函数，以方法的方式实现，对_后面的字段名起效果 
    def validata_email(self,field):
        if User.query.filter_by(email=field.data).first():
            # 抛出异常，参数是错误消息
            raise ValidationError('这个邮箱已经被注册了')

    def validata_name(self,field):
        if User.query.filter_by(name=field.data).first():
            raise ValidationError('这个用户名已经被使用了')

class ChangePassFrom(Form):
    old_password = StringField('旧密码',validators=[Required(),Length(1,64)])
    new_password = StringField('新密码',validators=[Required(),Length(1,64)])
    submit = SubmitField('更改')

class resetPassForm(Form):
    email = StringField('邮箱',validators=[Required(),Email()])
    submit = SubmitField('重置')

class setPassForm(Form):
    # email = StringField('email',validators=[Required(),Email()])
    password = PasswordField('密码',validators=[Required(),Length(1,64),EqualTo('password2',message='passwords must match.')])
    password2 = PasswordField('确认密码',validators=[Required()])
    submit = SubmitField('设置')

class resetEmailForm(Form):
    email = StringField('邮箱',validators=[Required(),Email()])
    submit = SubmitField('重回')

class setEmailForm(Form):
    email = StringField('邮箱',validators=[Required(),Email(),EqualTo('email2',message='email must match')])
    email2 = StringField('确认邮箱',validators=[Required(),Email()])
    submit = SubmitField('设置')
