import os
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user
from itsdangerous import URLSafeTimedSerializer, BadSignature
from datetime import datetime

from ..models import User
from ..extensions import db, login_manager, limiter
from . import auth_bp
from .forms import LoginForm, ResetRequestForm, ResetPasswordForm

try:
    from authlib.integrations.flask_client import OAuth
    oauth = OAuth()
    google = oauth.register(
        name='google',
        client_id=os.environ.get('GOOGLE_CLIENT_ID'),
        client_secret=os.environ.get('GOOGLE_CLIENT_SECRET'),
        access_token_url='https://oauth2.googleapis.com/token',
        authorize_url='https://accounts.google.com/o/oauth2/auth',
        client_kwargs={'scope': 'openid email profile'},
    )
except Exception:  # pragma: no cover - optional dependency
    oauth = None
    google = None
from ..utils.email_sender import send_reset_email


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit('5 per minute')
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            if user.mfa_enabled:
                if not form.token.data or not user.verify_totp(form.token.data):
                    flash('Código de 2FA inválido')
                    return render_template('auth/login.html', form=form, title='Entrar', login_page=True)
            user.last_login = datetime.utcnow()
            db.session.commit()
            login_user(user, remember=form.remember.data)
            return redirect(url_for('library.list_libraries'))
        flash('Credenciais inválidas')
    return render_template('auth/login.html', form=form, title='Entrar', login_page=True)


@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth_bp.route('/login/google')
def google_login():
    if not google:
        flash('Google OAuth não configurado')
        return redirect(url_for('auth.login'))
    redirect_uri = url_for('auth.google_authorized', _external=True)
    return google.authorize_redirect(redirect_uri)


@auth_bp.route('/login/google/authorized')
def google_authorized():
    if not google:
        flash('Google OAuth não configurado')
        return redirect(url_for('auth.login'))
    token = google.authorize_access_token()
    resp = google.get('userinfo')
    user_info = resp.json()
    user = User.query.filter_by(email=user_info['email']).first()
    if not user:
        user = User(name=user_info['name'], email=user_info['email'])
        user.set_password(os.urandom(16).hex())
        db.session.add(user)
        db.session.commit()
    login_user(user, remember=True)
    return redirect(url_for('library.list_libraries'))


def _token_serializer():
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'], salt='pwd-reset')


@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_request():
    form = ResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = _token_serializer().dumps(user.id)
            send_reset_email(current_app, user, token)
        flash('Se o email estiver cadastrado, enviaremos instruções.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_request.html', form=form, title='Recuperar senha')


@auth_bp.route('/reset/<token>', methods=['GET', 'POST'])
def reset_with_token(token):
    form = ResetPasswordForm()
    try:
        user_id = _token_serializer().loads(token, max_age=3600)
    except BadSignature:
        flash('Link inválido ou expirado')
        return redirect(url_for('auth.login'))
    user = User.query.get(user_id)
    if not user:
        flash('Usuário não encontrado')
        return redirect(url_for('auth.login'))
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Senha atualizada')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form, title='Definir nova senha')
