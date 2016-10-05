# -*- coding: UTF-8 -*-
from flask_wtf import Form
from wtforms import StringField, SubmitField,TextAreaField,BooleanField,SelectField,FileField
from wtforms.validators import Required,Length,Email,Regexp
from ..models import User,Role
from flask_wtf.file import FileField
from flask_pagedown.fields import PageDownField

class NameForm(Form):
    name = StringField('what\'s you name',validators=[Required()])
    submit = SubmitField('提交')

class EditProfileForm(Form):
    realname = StringField('真实姓名',validators=[Length(1,64)])
    location = StringField('所在地')
    about_me = TextAreaField('关于自己')
    submit = SubmitField('提交')

class AdminEditProfileForm(Form):
    realname = StringField('真实姓名',validators=[Length(1,64)])
    location = StringField('所在地')
    about_me = TextAreaField('关于自己')
    submit = SubmitField('提交')
    email = StringField('邮箱',validators=[Required(),Length(1,64),Email()])
    name = StringField('用户名',validators=[Required(),Length(1,64),Regexp('^[A-Za-z][A-Za-z0-9._]*$',0,'username must have only letter,number,dot or underscores')])
    confirm = BooleanField('确认')
    # 将字段的值转换为整数
    role = SelectField('角色',coerce=int)
    submit = SubmitField('submit')
    
    def __init__(self,user,*args,**kwargs):
        super(AdminEditProfileForm,self).__init__(*args,**kwargs)
        # 构造一个表单列表，用于select下拉列表中的选项，选项必须是一个由元祖组成的列表
        # 元祖包含标识符和显示在控件中的字符串
        # 标识符由是id，字符串是角色名
        self.role.choices = [(role.id,role.username) for role in Role.query.order_by(Role.username).all()]
        # 将user引入，以方便在校验的时候使用
        self.user = user

    def validate_email(self,field):
        if self.user.email != field.data and User.query.filter_by(email=field.data):
            raise validationError("邮箱已经被使用")

    def validata_name(self,field):
        if self.user.name != field.data and User.query.filter_by(name=field.data):
            raise validationError("用户名已经被使用")

class PhotoForm(Form):
    photo = FileField('图片')
    submit = SubmitField('提交')

class postForm(Form):
    head = StringField('标题',validators=[Required(),Length(1,64)])
    post = PageDownField('文章',validators=[Required()])
    submit = SubmitField('提交')
    
class CommentForm(Form):
    comment = TextAreaField('评论',validators=[Length(1,64)])
    submit = SubmitField('提交')
