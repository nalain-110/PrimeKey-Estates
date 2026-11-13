"""
Auth blueprint: register, login, logout, profile
"""
from functools import wraps

from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash, session)
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app import models
from app.models import User, Role, Agent, ActivityLog
from app.forms.auth_forms import RegisterForm, LoginForm, ProfileForm

auth_bp = Blueprint('auth', __name__, template_folder='../../templates/auth')

ROLE_NAMES = {1: 'Admin', 2: 'Agent', 3: 'Client'}


# ── Helpers ──────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to continue.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


def log_activity(user_id, action, table=None, record_id=None):
    al = ActivityLog(user_id=user_id, action=action,
                     table_name=table, record_id=record_id)
    db.session.add(al)
    db.session.commit()


def count_for(model_names, value, columns):
    """
    Safely count rows where one of `columns` equals `value`.
    Tries each model name and column; returns 0 if none exist,
    so the profile page never crashes on a name mismatch.
    """
    for model_name in model_names:
        model = getattr(models, model_name, None)
        if model is None:
            continue
        for col in columns:
            if hasattr(model, col):
                try:
                    return model.query.filter(getattr(model, col) == value).count()
                except Exception:
                    db.session.rollback()
    return 0


# ── Register ──────────────────────────────────────────────
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('public.index'))
    form = RegisterForm()
    if form.validate_on_submit():
        hashed = generate_password_hash(form.password.data)
        user = User(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            password=hashed,
            role_id=form.role.data
        )
        db.session.add(user)
        db.session.flush()   # get user.id before commit
        # If registering as agent, create agent profile
        if int(form.role.data) == 2:
            agent = Agent(user_id=user.id)
            db.session.add(agent)
        db.session.commit()
        log_activity(user.id, 'User registered')
        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('auth.login'))
    # Template may use either `form` or `register_form`, so pass both.
    return render_template('auth/register.html',
                           form=form, register_form=form)


# ── Login ─────────────────────────────────────────────────
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('public.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            if not user.is_active:
                flash('Your account has been deactivated. Contact admin.', 'danger')
                return redirect(url_for('auth.login'))
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_role'] = user.role_id
            session['user_email'] = user.email
            if form.remember.data:
                session.permanent = True
            log_activity(user.id, 'User logged in')
            flash(f'Welcome back, {user.name}!', 'success')
            # Redirect based on role
            if user.role_id == 1:
                return redirect(url_for('admin.dashboard'))
            elif user.role_id == 2:
                return redirect(url_for('agent.dashboard'))
            else:
                return redirect(url_for('client.dashboard'))
        flash('Invalid email or password.', 'danger')
    # Template may use either `form` or `login_form`, so pass both.
    return render_template('auth/login.html',
                           form=form, login_form=form)


# ── Logout ────────────────────────────────────────────────
@auth_bp.route('/logout')
def logout():
    user_id = session.get('user_id')
    if user_id:
        log_activity(user_id, 'User logged out')
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('public.index'))


# ── Profile ───────────────────────────────────────────────
@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = db.get_or_404(User, session['user_id'])
    agent = None
    if user.role_id == 2:
        agent = Agent.query.filter_by(user_id=user.id).first()

    form = ProfileForm(obj=user) if request.method == 'GET' else ProfileForm()

    # Pre-fill agent fields on first load
    if request.method == 'GET' and agent:
        form.agency_name.data = getattr(agent, 'agency_name', None)
        form.license_no.data = getattr(agent, 'license_no', None)
        form.experience_years.data = getattr(agent, 'experience_years', None)

    if form.validate_on_submit():
        other = User.query.filter(User.email == form.email.data,
                                  User.id != user.id).first()
        if other:
            form.email.errors = list(form.email.errors) + ['Email is already registered.']
        else:
            user.name = form.name.data
            user.email = form.email.data
            user.phone = form.phone.data
            if agent:
                for field in ('agency_name', 'license_no', 'experience_years'):
                    if hasattr(agent, field):
                        setattr(agent, field, getattr(form, field).data)
            db.session.commit()
            session['user_name'] = user.name
            session['user_email'] = user.email
            log_activity(user.id, 'Profile updated')
            flash('Profile updated successfully.', 'success')
            return redirect(url_for('auth.profile'))

    # Stats (safe: show 0 if a model/column name differs)
    fav_count = count_for(('Favorite', 'Favourite', 'Favorites'), user.id, ('user_id', 'client_id'))
    inquiry_count = count_for(('Inquiry', 'Inquiries'), user.id, ('user_id', 'client_id'))
    offer_count = count_for(('Offer',), user.id, ('user_id', 'client_id', 'buyer_id'))
    deal_count = count_for(('Deal',), user.id, ('user_id', 'client_id', 'buyer_id'))

    listings_count = deals_count = 0
    rating = 0.0
    if agent:
        listings_count = count_for(('Property', 'Listing'), agent.id, ('agent_id',))
        deals_count = count_for(('Deal',), agent.id, ('agent_id',))
        rating = float(getattr(agent, 'rating', 0) or 0)

    return render_template(
        'auth/profile.html',
        user=user,
        profile_form=form,
        role_name=ROLE_NAMES.get(user.role_id, 'User'),
        fav_count=fav_count,
        inquiry_count=inquiry_count,
        offer_count=offer_count,
        deal_count=deal_count,
        listings_count=listings_count,
        deals_count=deals_count,
        rating=rating,
    )
