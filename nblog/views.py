#coding: utf-8
from flask import render_template, url_for, \
        g, request, Response, flash, redirect, \
        session, send_from_directory
from mongoengine import Q
from hashlib import md5
from functools import wraps
from markdown import markdown
import os
from nblog import app
from models import User, Post
import datetime

def checkLogin(methods=['POST']):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            method = request.method
            if method not in methods:
                return f(*args, **kwargs)
            user = session.get('user', None)
            if user:
                return f(*args, **kwargs)
            else:
                flash(u'未登录!', u'error')
                return redirect(url_for('index'))
        return decorated_function
    return decorator

def checkNotLogin(methods=['POST']):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            method = request.method
            if method not in methods:
                return f(*args, **kwargs)
            user = session.get('user', None)
            if not user:
                return f(*args, **kwargs)
            else:
                flash(u'已登录!', u'error')
                return redirect(url_for('index'))
        return decorated_function
    return decorator

@app.route('/')
def index():
    posts = Post.objects()
    for post in posts:
        post.post = markdown(post.post)
    context = dict(title=u"主页",
                   posts=posts)
    return render_template("index.html",
                           **context)

@app.route('/reg', methods=['POST', 'GET'])
@checkNotLogin(['POST'])
def reg():
    if request.method == 'GET':
        context = dict(title=u"注册")
        return render_template("reg.html",
                               **context)
    else:
        name = request.form['name']
        password = request.form['password']
        password_re = request.form['password-repeat']
        email = request.form['email']
        if password != password_re:
            flash(u'两次输入的密码不一致!', u'error')
            return redirect(url_for('reg'))
        m = md5()
        m.update(password)
        password = m.hexdigest()
        password = unicode(password)
        user = User()
        user.name = name
        user.password = password
        user.email = email

        res = User.objects(name=user.name)
        if res:
            flash(u'用户已存在!', u'error')
            return redirect(url_for('reg'))
        res = user.save()
        if res:
            session['user'] = user
            flash(u'注册成功!', u'success')
            return redirect(url_for('index'))
        else:
            flash(u'保存错误!', u'error')
            return redirect(url_for('reg'))

@app.route('/login', methods=['POST', 'GET'])
@checkNotLogin(['POST', 'GET'])
def login():
    if request.method == 'GET':
        context = dict(title=u"登录")
        return render_template('login.html', **context)
    else:
        name = request.form['name']
        password = request.form['password']
        m = md5()
        m.update(password)
        password = m.hexdigest()
        password = unicode(password)
        res = User.objects(name=name)
        if not res:
            flash(u'用户不存在!', u'error')
            return redirect(url_for('login'))
        user = res[0]
        if user.password != password:
            flash(u'密码错误!', u'error')
            return redirect(url_for('login'))
        session['user'] = user
        flash(u'登陆成功!', u'success')
        return redirect(url_for('index'))

@app.route('/post', methods=['POST', 'GET'])
@checkLogin(['POST', 'GET'])
def post():
    if request.method == 'GET':
        context = dict(title=u'发表')
        return render_template("post.html", **context)
    else:
        user = session['user']
        title = request.form['title']
        post_txt = request.form['post']
        post = Post()
        post.name = user.name
        post.title = title
        post.post = post_txt
        if post.save():
            flash(u'发布成功!', u'success')
        else:
            flash(u'发布失败', u'error')
        return redirect(url_for('index'))

@app.route('/logout')
@checkLogin(['GET'])
def logout():
    session['user'] = None
    flash(u'登出成功!', u'success')
    return redirect(url_for('index'))

@app.route('/upload', methods=['GET', 'POST'])
@checkLogin(['GET', 'POST'])
def upload():
    if request.method == 'GET':
        context=dict(title=u'文件上传')
        return render_template('upload.html', **context)
    else:
        for field in request.files:
            file = request.files[field]
            if file.filename == "":
                continue
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)

        flash(u'文件上传成功!', u'success')
        return redirect(url_for('upload'))

@app.route('/uploads/<path:filename>')
def uploads(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/u/<name>')
def user_posts(name):
    user = User.objects(name=name)
    if not user:
        flash(u'用户不存在!', u'error')
        return redirect(url_for('index'))
    posts = Post.objects(name=name)
    for post in posts:
        post.post = markdown(post.post)
    content = dict(title=session['user'].name,
                   posts=posts)
    return render_template('user.html', **content)

@app.route('/u/<name>/<day>/<title>')
def user_day_post(name, day, title):
    days = day.split('-')
    day = datetime.datetime(year=int(days[0]), month=int(days[1]), day=int(days[2]))
    day_next = datetime.datetime(day.year, day.month, day.day+1)
    query = Q(name=name) & Q(title=title) & Q(time__gte=day) & Q(time__lte=day_next)
    posts = Post.objects(query)
    if not posts:
        flash(u'文件不存在', u'error')
        return redirect(url_for('index'))
    post = posts[0]
    post.post = markdown(post.post)
    context = dict(title='article',
                   post=post)
    return render_template('article.html', **context)

@app.route('/edit/<name>/<day>/<title>', methods=['GET', 'POST'])
@checkLogin(['POST', 'GET'])
def edit_post(name, day, title):
    currentUser=session['user']
    days = day.split('-')
    date = datetime.datetime(year=int(days[0]), month=int(days[1]), day=int(days[2]))
    date_next = datetime.datetime(date.year, date.month, date.day+1)
    name = currentUser.name
    query = Q(name=name) & Q(title=title) & Q(time__gte=date) & Q(time__lte=date_next)
    posts = Post.objects(query)
    if request.method == 'GET':
        if not posts:
            flash(u'文章不存在', u'error')
            return redirect(url_for('index'))
        post = posts[0]
        #post.post = markdown(post.post)
        context = dict(title=u'编辑',
                       post=post)
        return render_template('edit.html', **context)
    else:
        if not posts:
            flash(u'文章不存在', u'error')
            return redirect(request.url)
        post = posts[0]
        post.post = request.form['post']
        post.save()

        url = '/'.join(['/u', name, day, title])
        return redirect(url)

@app.route('/remove/<name>/<day>/<title>', methods=['GET'])
@checkLogin(['GET'])
def remove_post(name, day, title):
    currentUser=session['user']
    days = day.split('-')
    date = datetime.datetime(year=int(days[0]), month=int(days[1]), day=int(days[2]))
    date_next = datetime.datetime(date.year, date.month, date.day+1)
    name = currentUser.name
    query = Q(name=name) & Q(title=title) & Q(time__gte=date) & Q(time__lte=date_next)
    posts = Post.objects(query)

    if not posts:
        flash(u'文章不存在', u'error')
        return redirect(url_for('index'))
    post = posts[0]

    post.delete()
    flash(u'删除成功!', u'success')
    return redirect(url_for('index'))





