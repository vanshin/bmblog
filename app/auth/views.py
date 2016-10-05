# -*- coding: UTF-8 -*-
from flask import render_template,flash,redirect,request,url_for,current_app
from flask_login import login_required,login_user,logout_user,current_user
from . import auth
from .forms import LoginForm,RegistrationForm,ChangePassFrom,resetPassForm,setPassForm,resetEmailForm,setEmailForm
from ..models import User
from .. import db
from ..email import send_email
from PIL import Image
from ..imageFormat import CalcMD5

# login_required保护路由，确保登陆的用户才能访问
@auth.route('/login',methods=['POST','GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user)
            return redirect(url_for('main.index'))
            # return redirect(request.args.get('next') or url_for('main.index'))
        flash("invalid password or name")
    return render_template('auth/login.html',form=form)


@auth.route('/logout',methods=['POST','GET'])
@login_required
def logout():
    logout_user()
    flash('you have logout')
    return redirect(url_for('main.index'))


@auth.route('/regi',methods=['POST','GET'])
def regi():
    form = RegistrationForm()
    if form.validate_on_submit():
        avatormd5 = CalcMD5('/var/www/flask.com/app/static/pic/kotori.jpg')
        user = User(email=form.email.data,name=form.name.data,password=form.password.data,avator=avatormd5)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email,'confirm your account','auth/mail/test',user=user,token=token)

        flash('you have regied')
        return redirect(url_for('main.index'))
    return render_template('auth/regi.html',form=form)

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('you have confirm you account')
    else:
        flash('the confirm link is invalid or has expired')
    return redirect(url_for('main.index'))

@auth.route('/confirm')
@login_required
def resend_confirm():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email,'confirm your account','auth/mail/test',user=current_user,token=token)
    flash('a new mail have been sent to you mailbox')
    return redirect(url_for('main.index'))

@auth.before_app_request
def before_request():
    if current_user.is_authenticated and not current_user.confirmed and request.endpoint[:5] != 'auth.' and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))

@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')



@auth.route('/changePassword',methods=['POST','GET'])
@login_required
def changePassword():
    form = ChangePassFrom()
    if form.validate_on_submit():
        form.old_password.data
        if current_user.verify_password(form.old_password.data):
            # 修改密码
            current_user.password = form.new_password.data
            flash('your password have been changed')
            return redirect(url_for('main.index'))
        else:
            flash('old pass is not right')
            return render_template('auth/changePassword.html',user=current_user,form=form)
    return render_template('auth/changePassword.html',user=current_user,form=form)

@auth.route('/resetPass',methods=['POST','GET'])
def resetPass():
    form = resetPassForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        token = user.generate_reset_token()
        send_email(form.email.data,'resetPass','auth/mail/reset',user=user,token=token)
        flash('email have been sent to your mail')
        return redirect(url_for('main.index'))
    return render_template('auth/reset.html',form=form)

@auth.route('/setPass/<token>',methods=['POST','GET'])
def setPass(token):
    form = setPassForm()
    if form.validate_on_submit():
        # user = User.query.filter_by(email=form.email.data).first()
        id = User().get_userid(token)
        user = User.query.filter_by(id=id).first()
        if user is not None:
            if user.change_pass(form.password.data):   
                flash('success')
                return redirect(url_for('auth.login'))
            else:
                flash('something wrong happened')
        flash('do not have this user')
        return redirect(url_for('auth.resetPass'))
    return render_template('auth/setpass.html',form=form)

@auth.route('/resetEmail',methods=['POST','GET'])
def resetEmail():
    form = resetEmailForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            flash('this user is not here')
            return redirect(url_for('auth.resetEmail'))
        token = user.generate_reset_token()
        send_email(user.email,'reset your email','auth/mail/email',token=token,user=user)
        flash('email have been sent to your emailbox')
        return redirect(url_for('main.index'))
    return render_template('auth/resetEmail.html',form=form)

@auth.route('/setEmail/<token>',methods=['POST','GET'])
@login_required
def setEmail(token):
    form = setEmailForm()
    if form.validate_on_submit():
        id = User().get_userid(token)
        user = User.query.filter_by(id=id).first()
        if user is not None:
            if user.reset_email(form.email.data):   
                flash('success')
                return redirect(url_for('auth.login'))
            else:
                flash('something wrong happened')
        flash('do not have this user')
        return redirect(url_for('auth.resetEmail'))
    return render_template('auth/setEmail.html',form=form)

