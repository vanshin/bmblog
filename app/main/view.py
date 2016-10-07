# -*- coding: UTF-8 -*-
from datetime import datetime
from flask import render_template,session,redirect,url_for,make_response,abort,flash,request
from flask_login import login_required,current_user,current_app
from . import main
from .. import db
from ..models import User,Role,Post,Permission,Comment
from .forms import NameForm,EditProfileForm,AdminEditProfileForm,PhotoForm,postForm,CommentForm
from ..decorators import admin_required
import os
from werkzeug.utils import secure_filename
from ..imageFormat import CalcMD5,resizeImage



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@main.route('/')
def index():
    page = request.args.get('page',1,type=int)
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed',''))
        
    if show_followed:
        query = current_user.followed_posts
        pagination = query.filter(Post.variety == 2).paginate(page,per_page=current_app.config['FLASKY_PER_PAGE'],
            error_out=False)
    else:
        query = Post.query
        pagination = query.filter(Post.variety == 1).paginate(page,per_page=current_app.config['FLASKY_PER_PAGE'],
            error_out=False)
    posts = pagination.items
    return render_template('index.html',posts=posts,
            pagination=pagination,show_followed=show_followed)

@main.route('/user/<name>')
def user(name):
    user = User.query.filter_by(name=name).first()
    if user is None:
        abort(404)
    if current_user.id == user.id:
        posts = user.post.order_by(Post.timestamp.desc()).all()
    elif user.is_following(current_user):
        posts = user.post.filter(Post.variety < 3).all()
    else:
        posts = user.post.filter(Post.variety == 1).all()
    
    return render_template('user.html',user=user,posts=posts)

@main.route('/editAvator',methods=['POST','GET'])
@login_required
def editAvator():
    form = PhotoForm()
    if form.validate_on_submit():
	filename = secure_filename(form.photo.data.filename)
        suffix = '.'+filename.split('.')[1]
        

        path = '/var/www/flask.com/app/static/pic/'
        form.photo.data.save(path + filename)
        # MD5计算
        md5 = CalcMD5(path + filename)
        photoname = md5+suffix
        # 保存
        os.rename(path+filename,path+photoname)
        current_user.avator = photoname
        db.session.add(current_user)
    return render_template('edit_avator.html',user=current_user,form=form)


@main.route('/editProfile',methods=['POST','GET'])
@login_required
def editProfileTest():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.realname = form.realname.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('个人信息更改成功')
        return redirect(url_for('main.user',name=current_user.name))
    form.realname.data = current_user.realname
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)

@main.route('/editProfileAdmin/<int:id>', methods=['POST','GET'])
@login_required
@admin_required
def editProfileAdmin(id):
    user = User.query.get_or_404(id)
    form = AdminEditProfileForm(user=user)
    
    if form.validate_on_submit():
        user.realname = form.realname.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        user.name = form.name.data
        # data里面存储了role的id，用查询找出角色
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.confirm = form.confirm.data
        db.session.add(user)
        flash( '用户的个人信息被管理重置成功')
        return redirect(url_for('main.user',name=user.name)) 
    form.email.data = user.email
    form.name.data = user.name
    form.confirm.data = user.confirm
    form.role.data = user.roles_id
    form.realname.data = user.realname
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)       

    
@main.route('/makePost',methods=['POST','GET'])
def makePost():
    form = postForm()
    if form.validate_on_submit() and current_user.can(Permission.WRITE_ARTICLES):
        post = Post(author=current_user._get_current_object(),
                body=form.post.data,
                head=form.head.data,
                variety=form.variery.data)
        db.session.add(post)
        return redirect(url_for('.index'))
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('edit_post.html',form=form)

@main.route('/post/<int:id>',methods=['POST','GET'])
def post(id):
    post = Post.query.get_or_404(id)
    user = User.query.filter_by(id = post.author_id).first()
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.comment.data,author_id=user.id,post_id=post.id)
        db.session.add(comment)
        return redirect(url_for('.post',id=post.id))
    page = request.args.get('page', 1, type=int)
    pagination = post.comment.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('post.html',form=form,posts=[post],
            comments=comments,
            pagination=pagination,
            page=page,
            endpoint='.post')

@main.route('/editPost/<int:id>',methods=['POST','GET'])
def editPost(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and not current_user.can(Permission.ADMINISTR):
        abort(403)
    form = postForm()
    
    if form.validate_on_submit():
        post.body = form.post.data
        post.head = form.head.data
        post.variety = form.variety.data
        db.session.add(post)
        flash('文章更改成功')
        return redirect(url_for('.post',id=id))
    form.post.data = post.body
    form.head.data = post.head
    form.variety.data = post.variery
    return render_template('edit_post.html',form=form)

@main.route('/follow/<username>')
def follow(username):
    user = User.query.filter_by(name=username).first()
    if user is None:
        flash('不存在的用户')
        return redirect(url_for('.user',name=username))
    if current_user.is_following(user):
        flash('已经关注此用户')
        return redirect(url_for('.user',name=username))
    if current_user.can(Permission.FOLLOW):
        current_user.follow(user)
        flash('关注%s成功' % username)
        return redirect(url_for('.user',name=username))
    flash('请先登录')
    return redirect(url_for('.user',name=username))

@main.route('/unfollow/<username>')
def unfollow(username):
    user = User.query.filter_by(name=username).first()
    if user is None:
        flash('不存在的用户')
        return redirect(url_for('.user',name=username))
    if not current_user.is_following(user):
        flash('还没有关注此用户')
        return redirect(url_for('.user',name=username))
    current_user.unfollow(user)
    flash('取消关注%s成功' %username)
    return redirect(url_for('.user',name=username))

@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(name=username).first()
    if user is None:
        flash('不存在的用户')
        return redirect(url_for('.user',name=username))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
            page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
            error_out=False)
    follows = [{'user': item.follower,
            'timestamp': item.timestamp} for item in pagination.items]
    return render_template('followers.html', user=user, title="的关注者",
            endpoint='.followers', pagination=pagination,
            follows=follows)

@main.route('/followed_by/<username>')
def followed_by(username):
    user = User.query.filter_by(name=username).first()
    if user is None:
        flash('不存在的用户')
        return redirect(url_for('.user',name=username))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
            page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
            error_out=False)
    follows = [{'user': item.follower,
            'timestamp': item.timestamp} for item in pagination.items]
    return render_template('followers.html', user=user, title="关注的人",
            endpoint='.followed_by', pagination=pagination,
            follows=follows)

@main.route('/all')
@login_required
def all():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed','',max_age=30*24*60*60)
    return resp

@main.route('/followed')
@login_required
def followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed','1',max_age=30*24*60*60)
    return resp

@main.route('/comment/<int:id>',methods=['POST','GET'])
@login_required
def comment(id):
    post = Post.query.get_or_404(id)
    user = User.query.filter_by(id = post.author_id).first()
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.comment.data,author_id=user.id,post_id=post.id)
        db.session.add(comment)
        return redirect(url_for('.post',id=post.id))
    page = request.args.get('page', 1, type=int)
    pagination = post.comment.order_by(Comment.timestamp.asc()).paginate(
            page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
            error_out=False)
    comment = pagination.items
    return render_template('post.html',form=form,posts=[post],
            comment=comment,
            pagination=pagination,
            page=page,
            endpoint='.post')
