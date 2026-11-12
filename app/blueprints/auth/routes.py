"""
Auth blueprint: register, login, logout, profile
"""
from functools import wraps

from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash, session)
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import (User, Agent, ActivityLog, Favorite, Inquiry,
                         Offer, Deal, Property)
from app.forms.auth_forms import RegisterForm, LoginForm, ProfileForm

auth_bp = Blueprint('auth', __name__, template_folder='../../templates/auth')


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


# ── Register ──────────────────────────────────────────────
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('public.index'))
    form = RegisterForm()
    if form.validate_on_submit():
        role_id = form.role.data  # already int and limited to 2 or 3 by the form
        user = User(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            password=generate_password_hash(form.password.data),
            role_id=role_id
        )
        db.session.add(user)
        db.session.flush()   # get user.id before commit
        # If registering as agent, create agent profile
        if role_id == 2:
            db.session.add(Agent(user_id=user.id))
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
AGENT_FIELDS = ('agency_name', 'license_no', 'experience_years')


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user  = db.get_or_404(User, session['user_id'])
    agent = Agent.query.filter_by(user_id=user.id).first() if user.role_id == 2 else None

    form = ProfileForm(obj=user, user_id=user.id)

    # Pre-fill agent-only fields on first load (only if the Agent model has them)
    if request.method == 'GET' and agent:
        for field in AGENT_FIELDS:
            if hasattr(agent, field):
                getattr(form, field).data = getattr(agent, field)

    if form.validate_on_submit():
        user.name  = form.name.data
        user.email = form.email.data
        user.phone = form.phone.data
        if agent:
            for field in AGENT_FIELDS:
                if hasattr(agent, field):
                    setattr(agent, field, getattr(form, field).data)
        db.session.commit()
        session['user_name']  = user.name
        session['user_email'] = user.email
        log_activity(user.id, 'Profile updated')
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('auth.profile'))

    # Sidebar stats
    uid = user.id
    ctx = dict(
        user=user,
        profile_form=form,
        fav_count=Favorite.query.filter_by(client_id=uid).count(),
        inquiry_count=Inquiry.query.filter_by(client_id=uid).count(),
        offer_count=Offer.query.filter_by(client_id=uid).count(),
        deal_count=Deal.query.filter_by(buyer_id=uid).count(),
        listings_count=0, deals_count=0, rating=0.0,
    )
    if agent:
        ctx['listings_count'] = Property.query.filter_by(agent_id=agent.id).count()
        ctx['deals_count']    = Deal.query.filter_by(agent_id=agent.id).count()
        ctx['rating']         = float(getattr(agent, 'rating', 0) or 0)
    return render_template('auth/profile.html', **ctx)
