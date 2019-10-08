from flask import render_template, flash, redirect, url_for, request, session, make_response
from app import app, query_db
from app.forms import IndexForm, PostForm, FriendsForm, ProfileForm, CommentsForm
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import os
import time

# this file contains all the different routes, and the logic for communicating with the database

# home page/login/registration
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    user = query_db(
        'SELECT * FROM Users WHERE username="{}";'.format(request.cookies.get('username')), one=True)
    if session.get('login_attempts') == None:
        session['login_attempts'] = int(0)
        session['login_block'] = datetime.now()

    if user == None:
        form = IndexForm()

        if form.login.validate_on_submit() and form.login.submit.data:
            if datetime.now() > session.get('login_block'):
                if int(session.get('login_attempts')) >= 3:
                    flash(
                        'You have failed too many login attempts, try again in 30 seconds')
                    session['login_block'] = datetime.now() + \
                        timedelta(seconds=30)
                    session['login_attempts'] = int(0)
                else:
                    user = query_db(
                        'SELECT * FROM Users WHERE username="{}";'.format(form.login.username.data), one=True)
                    if user == None:
                        session['login_attempts'] = int(
                            session.get('login_attempts')+1)
                        flash('Sorry, This username or password is incorrect')
                    elif check_password_hash(user['password'], form.login.password.data):
                        session['username'] = form.login.username.data
                        session['password'] = user['password']
                        if form.login.remember_me.data == True:
                            response = make_response(
                                redirect(url_for('stream', username=form.login.username.data)))
                            response.set_cookie(
                                'username', form.login.username.data)
                            response.set_cookie('password', user['password'])
                            return response
                        return redirect(url_for('stream', username=form.login.username.data))
                    else:
                        session['login_attempts'] = int(
                            session.get('login_attempts')+1)
                        flash('Sorry, This username or password is incorrect')
            else:
                flash("you are still blocked from logging in, wait a bit longer")

        # if register form is submitted
        elif form.register.validate_on_submit() and form.register.submit.data:
            user_reg = query_db(
                'SELECT * FROM Users WHERE username="{}";'.format(form.register.username.data), one=True)
            if user_reg == None:
                query_db('INSERT INTO Users (username, first_name, last_name, password) VALUES("{}", "{}", "{}", "{}");'.format(
                    form.register.username.data,
                    form.register.first_name.data,
                    form.register.last_name.data,
                    generate_password_hash(form.register.password.data)))
                return redirect(url_for('index'))
            else:
                flash("This username is already taken")
        return render_template('index.html', title='Welcome', form=form)
    elif user['password'] == request.cookies.get('password'):
        session['username'] = request.cookies.get('username')
        session['password'] = request.cookies.get('password')
        return redirect(url_for('stream', username=request.cookies.get('username')))
    else:
        flash('Sorry, The login data in the cookie is incorrect')
        return redirect(url_for('index'))

# content stream page
@app.route('/stream/<username>', methods=['GET', 'POST'])
def stream(username):
    user = query_db(
        'SELECT * FROM Users WHERE username="{}";'.format(username), one=True)
    if user == None:
        flash('You are not logged in')
        return redirect(url_for('index'))
    elif user['password'] == session.get('password'):
        # show page
        form = PostForm()
        user = query_db(
            'SELECT * FROM Users WHERE username="{}";'.format(username), one=True)
        if form.validate_on_submit():
            if form.image.data:
                path = os.path.join(
                    app.config['UPLOAD_PATH'], form.image.data.filename)
                form.image.data.save(path)
            query_db('INSERT INTO Posts (u_id, content, image, creation_time) VALUES({}, "{}", "{}", \'{}\');'.format(
                user['id'],
                form.content.data,
                form.image.data.filename,
                datetime.now()))
            return redirect(url_for('stream', username=username))
        posts = query_db(
            'SELECT p.*, u.*, (SELECT COUNT(*) FROM Comments WHERE p_id=p.id) AS cc FROM Posts AS p JOIN Users AS u ON u.id=p.u_id WHERE p.u_id IN (SELECT u_id FROM Friends WHERE f_id={0}) OR p.u_id IN (SELECT f_id FROM Friends WHERE u_id={0}) OR p.u_id={0} ORDER BY p.creation_time DESC;'.format(user['id']))
        return render_template('stream.html', title='Stream', username=username, form=form, posts=posts)
    else:
        return redirect(url_for('stream', username=session.get('username')))

# comment page for a given post and user.
@app.route('/comments/<username>/<int:p_id>', methods=['GET', 'POST'])
def comments(username, p_id):
    user = query_db(
        'SELECT * FROM Users WHERE username="{}";'.format(username), one=True)
    if user == None:
        flash('You are not logged in')
        return redirect(url_for('index'))
    elif user['password'] == session.get('password'):
        form = CommentsForm()
        if form.is_submitted():
            user = query_db(
                'SELECT * FROM Users WHERE username="{}";'.format(username), one=True)
            query_db('INSERT INTO Comments (p_id, u_id, comment, creation_time) VALUES({}, {}, "{}", \'{}\');'.format(
                p_id, user['id'], form.comment.data, datetime.now()))
        post = query_db(
            'SELECT * FROM Posts WHERE id={};'.format(p_id), one=True)
        all_comments = query_db(
            'SELECT DISTINCT * FROM Comments AS c JOIN Users AS u ON c.u_id=u.id WHERE c.p_id={} ORDER BY c.creation_time DESC;'.format(p_id))
        return render_template('comments.html', title='Comments', username=username, form=form, post=post, comments=all_comments)
    else:
        return redirect(url_for('stream', username=session.get('username')))

# page for seeing and adding friends
@app.route('/friends/<username>', methods=['GET', 'POST'])
def friends(username):
    user = query_db(
        'SELECT * FROM Users WHERE username="{}";'.format(username), one=True)
    if user == None:
        flash('You are not logged in')
        return redirect(url_for('index'))
    elif user['password'] == session.get('password'):
        form = FriendsForm()
        user = query_db(
            'SELECT * FROM Users WHERE username="{}";'.format(username), one=True)
        if form.is_submitted():
            friend = query_db(
                'SELECT * FROM Users WHERE username="{}";'.format(form.username.data), one=True)
            if friend is None:
                flash('User does not exist')
            else:
                query_db('INSERT INTO Friends (u_id, f_id) VALUES({}, {});'.format(
                    user['id'], friend['id']))

        all_friends = query_db(
            'SELECT * FROM Friends AS f JOIN Users as u ON f.f_id=u.id WHERE f.u_id={} AND f.f_id!={} ;'.format(user['id'], user['id']))
        return render_template('friends.html', title='Friends', username=username, friends=all_friends, form=form)
    else:
        return redirect(url_for('stream', username=session.get('username')))

# see and edit detailed profile information of a user
@app.route('/profile/<username>', methods=['GET', 'POST'])
def profile(username):
    user = query_db(
        'SELECT * FROM Users WHERE username="{}";'.format(session.get('username')), one=True)
    if user == None:
        flash('You are not logged in')
        return redirect(url_for('index'))
    elif user['password'] == session.get('password'):
        form = ProfileForm()
        if form.is_submitted():
            user = query_db(
                'SELECT * FROM Users WHERE username="{}";'.format(username), one=True)
            if user == None:
                flash(
                    'you are not logged in, every error shouldnt happen, this error extra shouldnt happen')
                return redirect(url_for('index'))
            elif user['password'] == session.get('password'):
                query_db('UPDATE Users SET education="{}", employment="{}", music="{}", movie="{}", nationality="{}", birthday=\'{}\' WHERE username="{}" ;'.format(
                    form.education.data,
                    form.employment.data,
                    form.music.data,
                    form.movie.data,
                    form.nationality.data,
                    form.birthday.data,
                    username))
            else:
                flash('You are not logged in')
                return redirect(url_for('index'))
            return redirect(url_for('profile', username=username))
        user = query_db(
            'SELECT * FROM Users WHERE username="{}";'.format(username), one=True)
        return render_template('profile.html', title='profile', username=username, user=user, form=form)
    else:
        flash('You are not logged in')
        return redirect(url_for('index'))


@app.route("/logout")
def logout():
    response = make_response(redirect(url_for('index')))
    response.set_cookie('username', "", expires=0)
    response.set_cookie('password', "", expires=0)
    session.pop("username")
    session.pop("password")
    return response
