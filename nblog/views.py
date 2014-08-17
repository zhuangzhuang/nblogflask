#coding: utf-8
from flask import render_template, url_for, \
        g, request, Response, flash, redirect, \
        session
from hashlib import md5
from functools import wraps
from nblog import app
from models import User, Post

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
    print posts
    context = dict(title=u"主页",
                   posts=posts)
    return render_template("index.html",
                           **context)

@app.route('/reg', methods=['POST', 'GET'])
@checkLogin(['POST'])
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