from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user

from ..models import User
from ..extensions import db, login_manager
from . import auth_bp
from .forms import LoginForm


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('library.list_libraries'))
        flash('Invalid credentials')
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
