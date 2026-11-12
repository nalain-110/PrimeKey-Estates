"""
Admin blueprint: dashboard with Chart.js, users CRUD, locations,
payments, reports, settings, blog moderation, contact messages
"""
import json
from functools import wraps
from datetime import datetime
from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash, session)
from werkzeug.security import generate_password_hash
from app import db
from app.models import (User, Role, City, Area, Sector, Property,
                         Deal, Commission, Payment, Agent, Inquiry,
                         Offer, SiteVisit, Blog, ContactMessage,
                         NewsletterSubscriber, PropertyType, Amenity,
                         PropertyFeature, Coupon, BusinessReport,
                         Testimonial, FAQ, Setting, ActivityLog, Notification)

admin_bp = Blueprint('admin', __name__, template_folder='../../templates/admin')


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login.', 'warning')
            return redirect(url_for('auth.login'))
        if session.get('user_role') != 1:
            flash('Admin access required.', 'danger')
            return redirect(url_for('public.index'))
        return f(*args, **kwargs)
    return decorated


def last_n_months(n):
    """Return [(label_start_datetime, next_month_start_datetime), ...] oldest first."""
    now = datetime.utcnow()
    result = []
    for i in range(n - 1, -1, -1):
        month = now.month - i
        year = now.year
        while month <= 0:
            month += 12
            year -= 1
        start = datetime(year, month, 1)
        end = datetime(year + 1, 1, 1) if month == 12 else datetime(year, month + 1, 1)
        result.append((start, end))
    return result


# ── Dashboard ─────────────────────────────────────────────
@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    total_users   = User.query.count()
    total_props   = Property.query.count()
    total_deals   = Deal.query.count()
    total_agents  = Agent.query.count()
    total_revenue = db.session.query(db.func.sum(Deal.deal_price)).scalar() or 0
    total_comm    = db.session.query(db.func.sum(Commission.amount)).scalar() or 0
    pending_inq   = Inquiry.query.filter_by(status='Pending').count()
    pending_offers= Offer.query.filter_by(status='Pending').count()
    unread_msgs   = ContactMessage.query.filter_by(is_read=False).count()

    # Chart data: deals per month (last 12 months)
    chart_labels  = []
    deals_data    = []
    revenue_data  = []
    for m_start, m_end in last_n_months(12):
        chart_labels.append(m_start.strftime('%b %Y'))
        cnt = Deal.query.filter(Deal.deal_date >= m_start, Deal.deal_date < m_end).count()
        rev = db.session.query(db.func.sum(Deal.deal_price)).filter(
            Deal.deal_date >= m_start, Deal.deal_date < m_end).scalar() or 0
        deals_data.append(cnt)
        revenue_data.append(float(rev))

    # Property type distribution
    prop_types = PropertyType.query.all()
    type_labels = [pt.name for pt in prop_types]
    type_data   = [Property.query.filter_by(type_id=pt.id).count() for pt in prop_types]

    # Listing type split
    for_sale  = Property.query.filter_by(listing_type='Sale').count()
    for_rent  = Property.query.filter_by(listing_type='Rent').count()

    recent_deals  = Deal.query.order_by(Deal.deal_date.desc()).limit(5).all()
    recent_users  = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_logs   = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).limit(10).all()
    recent_props    = Property.query.order_by(Property.created_at.desc()).limit(5).all()
    recent_contacts = ContactMessage.query.order_by(ContactMessage.created_at.desc()).limit(5).all()
    total_inquiries = Inquiry.query.count()
    # Admin, Agents, Clients
    role_data = [User.query.filter_by(role_id=r).count() for r in (1, 2, 3)]

    return render_template('admin/dashboard.html',
        total_users=total_users, total_props=total_props,
        total_deals=total_deals, total_agents=total_agents,
        total_revenue=total_revenue, total_comm=total_comm,
        pending_inq=pending_inq, pending_offers=pending_offers, unread_msgs=unread_msgs,
        total_inquiries=total_inquiries,
        # Raw Python lists: the template converts them with |tojson
        chart_labels=chart_labels,
        deals_data=deals_data,
        revenue_data=revenue_data,
        prop_type_labels=type_labels,
        prop_type_data=type_data,
        role_data=role_data,
        for_sale=for_sale, for_rent=for_rent,
        recent_deals=recent_deals, recent_users=recent_users, recent_logs=recent_logs,
        recent_props=recent_props, recent_contacts=recent_contacts)


# ── Users CRUD ────────────────────────────────────────────
@admin_bp.route('/users')
@admin_required
def users():
    role_filter = request.args.get('role', 0, type=int)
    q = User.query
    if role_filter:
        q = q.filter_by(role_id=role_filter)
    users = q.order_by(User.created_at.desc()).all()
    roles = Role.query.all()
    return render_template('admin/users.html', users=users, roles=roles, role_filter=role_filter)


@admin_bp.route('/users/add', methods=['GET', 'POST'])
@admin_required
def add_user():
    roles = Role.query.all()
    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        email    = request.form.get('email', '').strip().lower()
        phone    = request.form.get('phone', '').strip()
        role_id  = request.form.get('role_id', 3, type=int)
        password = request.form.get('password', '').strip()
        if not all([name, email, password]):
            flash('Name, email and password are required.', 'danger')
            return render_template('admin/add_user.html', roles=roles)
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('admin/add_user.html', roles=roles)
        user = User(name=name, email=email, phone=phone, role_id=role_id,
                    password=generate_password_hash(password))
        db.session.add(user)
        db.session.flush()
        if role_id == 2:
            agent = Agent(user_id=user.id)
            db.session.add(agent)
        db.session.commit()
        flash('User added!', 'success')
        return redirect(url_for('admin.users'))
    return render_template('admin/add_user.html', roles=roles)


@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    user  = User.query.get_or_404(user_id)
    roles = Role.query.all()
    if request.method == 'POST':
        new_email = request.form.get('email', user.email).strip().lower()
        clash = User.query.filter(User.email == new_email, User.id != user.id).first()
        if clash:
            flash('Another user already has this email.', 'danger')
            return render_template('admin/edit_user.html', user=user, roles=roles)
        new_role = request.form.get('role_id', user.role_id, type=int)
        # Don't let an admin lock themselves out
        if user.id == session['user_id'] and (new_role != 1 or 'is_active' not in request.form):
            flash('You cannot remove your own admin access or deactivate yourself.', 'danger')
            return render_template('admin/edit_user.html', user=user, roles=roles)
        user.name     = request.form.get('name', user.name)
        user.email    = new_email
        user.phone    = request.form.get('phone', user.phone)
        user.role_id  = new_role
        user.is_active= 'is_active' in request.form
        new_pass = request.form.get('password', '').strip()
        if new_pass:
            user.password = generate_password_hash(new_pass)
        db.session.commit()
        flash('User updated!', 'success')
        return redirect(url_for('admin.users'))
    return render_template('admin/edit_user.html', user=user, roles=roles)


@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    if user_id == session['user_id']:
        flash('Cannot delete your own account.', 'danger')
        return redirect(url_for('admin.users'))
    user = User.query.get_or_404(user_id)
    try:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted.', 'info')
    except Exception:
        db.session.rollback()
        flash('Cannot delete this user because they have related records. Deactivate them instead.', 'danger')
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/<int:user_id>/toggle', methods=['POST'])
@admin_required
def toggle_user(user_id):
    if user_id == session['user_id']:
        flash('You cannot deactivate your own account.', 'danger')
        return redirect(url_for('admin.users'))
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {status}.', 'success')
    return redirect(url_for('admin.users'))


# ── Locations ─────────────────────────────────────────────
@admin_bp.route('/locations')
@admin_required
def locations():
    cities  = City.query.order_by(City.name).all()
    areas   = Area.query.order_by(Area.name).all()
    sectors = Sector.query.order_by(Sector.name).all()
    return render_template('admin/locations.html', cities=cities, areas=areas, sectors=sectors)


@admin_bp.route('/locations/city/add', methods=['POST'])
@admin_required
def add_city():
    name     = request.form.get('name', '').strip()
    province = request.form.get('province', '').strip()
    if name:
        city = City(name=name, province=province)
        db.session.add(city)
        db.session.commit()
        flash(f'City "{name}" added!', 'success')
    return redirect(url_for('admin.locations'))


@admin_bp.route('/locations/city/<int:city_id>/delete', methods=['POST'])
@admin_required
def delete_city(city_id):
    city = City.query.get_or_404(city_id)
    try:
        db.session.delete(city)
        db.session.commit()
        flash('City deleted.', 'info')
    except Exception:
        db.session.rollback()
        flash('Cannot delete this city because areas or properties use it.', 'danger')
    return redirect(url_for('admin.locations'))


@admin_bp.route('/locations/area/add', methods=['POST'])
@admin_required
def add_area():
    name    = request.form.get('name', '').strip()
    city_id = request.form.get('city_id', 0, type=int)
    if name and city_id:
        area = Area(name=name, city_id=city_id)
        db.session.add(area)
        db.session.commit()
        flash(f'Area "{name}" added!', 'success')
    else:
        flash('Area name and city are required.', 'danger')
    return redirect(url_for('admin.locations'))


# ── Properties ────────────────────────────────────────────
@admin_bp.route('/properties')
@admin_required
def properties():
    props = Property.query.order_by(Property.created_at.desc()).all()
    return render_template('admin/properties.html', props=props)


@admin_bp.route('/properties/<int:prop_id>/verify', methods=['POST'])
@admin_required
def verify_property(prop_id):
    prop = Property.query.get_or_404(prop_id)
    prop.is_verified = not prop.is_verified
    db.session.commit()
    flash('Property verification status updated.', 'success')
    return redirect(url_for('admin.properties'))


@admin_bp.route('/properties/<int:prop_id>/featured', methods=['POST'])
@admin_required
def toggle_featured(prop_id):
    prop = Property.query.get_or_404(prop_id)
    prop.is_featured = not prop.is_featured
    db.session.commit()
    flash('Featured status updated.', 'success')
    return redirect(url_for('admin.properties'))


@admin_bp.route('/properties/<int:prop_id>/delete', methods=['POST'])
@admin_required
def delete_property(prop_id):
    prop = Property.query.get_or_404(prop_id)
    try:
        db.session.delete(prop)
        db.session.commit()
        flash('Property deleted.', 'info')
    except Exception:
        db.session.rollback()
        flash('Cannot delete this property because it has related records (deals, offers, etc.).', 'danger')
    return redirect(request.referrer or url_for('admin.properties'))


# ── Payments ──────────────────────────────────────────────
@admin_bp.route('/payments')
@admin_required
def payments():
    commissions = Commission.query.order_by(Commission.id.desc()).all()
    payments    = Payment.query.order_by(Payment.payment_date.desc()).all()
    return render_template('admin/payments.html', commissions=commissions, payments=payments)


@admin_bp.route('/commissions/<int:comm_id>/mark-paid', methods=['POST'])
@admin_required
def mark_commission_paid(comm_id):
    comm = Commission.query.get_or_404(comm_id)
    comm.status    = 'Paid'
    comm.paid_date = datetime.utcnow()
    db.session.commit()
    flash('Commission marked as paid!', 'success')
    return redirect(url_for('admin.payments'))


# ── Deals ─────────────────────────────────────────────────
@admin_bp.route('/deals')
@admin_required
def deals():
    deals = Deal.query.order_by(Deal.deal_date.desc()).all()
    return render_template('admin/deals.html', deals=deals)


@admin_bp.route('/deals/<int:deal_id>/close', methods=['POST'])
@admin_required
def close_deal(deal_id):
    deal = Deal.query.get_or_404(deal_id)
    deal.status    = 'Completed'
    deal.closed_at = datetime.utcnow()
    db.session.commit()
    flash('Deal marked as completed.', 'success')
    return redirect(url_for('admin.deals'))


# ── Reports ───────────────────────────────────────────────
@admin_bp.route('/reports')
@admin_required
def reports():
    # Monthly revenue (last 12 months)
    rev_labels, rev_data = [], []
    for m_start, m_end in last_n_months(12):
        rev = db.session.query(db.func.sum(Deal.deal_price)).filter(
            Deal.deal_date >= m_start, Deal.deal_date < m_end).scalar() or 0
        rev_labels.append(m_start.strftime('%b'))
        rev_data.append(float(rev))

    # Top agents by deals
    agents = Agent.query.all()
    agent_names   = [a.user.name for a in agents]
    agent_deals   = [Deal.query.filter_by(agent_id=a.id).count() for a in agents]
    agent_revenue = [float(db.session.query(db.func.sum(Deal.deal_price)).filter(Deal.agent_id == a.id).scalar() or 0) for a in agents]

    # Status distribution
    completed  = Deal.query.filter_by(status='Completed').count()
    in_progress= Deal.query.filter_by(status='In Progress').count()
    cancelled  = Deal.query.filter_by(status='Cancelled').count()

    total_revenue  = db.session.query(db.func.sum(Deal.deal_price)).scalar() or 0
    total_comm_paid= db.session.query(db.func.sum(Commission.amount)).filter(Commission.status == 'Paid').scalar() or 0

    return render_template('admin/reports.html',
        # Raw Python lists: the template converts them with |tojson
        rev_labels=rev_labels,
        rev_data=rev_data,
        agent_names=agent_names,
        agent_deals=agent_deals,
        agent_revenue=agent_revenue,
        completed=completed, in_progress=in_progress, cancelled=cancelled,
        total_revenue=total_revenue, total_comm_paid=total_comm_paid)


# ── Contact Messages ──────────────────────────────────────
@admin_bp.route('/messages')
@admin_required
def messages():
    msgs = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    # Mark all as read
    ContactMessage.query.filter_by(is_read=False).update({'is_read': True})
    db.session.commit()
    return render_template('admin/messages.html', msgs=msgs)


@admin_bp.route('/contacts')
@admin_required
def contacts():
    """Alias: templates that link to admin.contacts land on the messages page."""
    return redirect(url_for('admin.messages'))


# ── Blog Moderation ───────────────────────────────────────
@admin_bp.route('/blogs')
@admin_required
def blogs():
    posts = Blog.query.order_by(Blog.created_at.desc()).all()
    return render_template('admin/blogs.html', posts=posts)


@admin_bp.route('/blogs/<int:blog_id>/publish', methods=['POST'])
@admin_required
def publish_blog(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    blog.is_published = not blog.is_published
    blog.published_at = datetime.utcnow() if blog.is_published else None
    db.session.commit()
    flash('Blog status updated.', 'success')
    return redirect(url_for('admin.blogs'))


@admin_bp.route('/blogs/<int:blog_id>/delete', methods=['POST'])
@admin_required
def delete_blog(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    db.session.delete(blog)
    db.session.commit()
    flash('Blog deleted.', 'info')
    return redirect(url_for('admin.blogs'))


# ── Settings ──────────────────────────────────────────────
@admin_bp.route('/settings', methods=['GET', 'POST'])
@admin_required
def settings():
    settings = Setting.query.all()
    if request.method == 'POST':
        for s in settings:
            val = request.form.get(f'setting_{s.id}')
            if val is not None:
                s.value = val
        db.session.commit()
        flash('Settings saved!', 'success')
        return redirect(url_for('admin.settings'))
    return render_template('admin/settings.html', settings=settings)


# ── Property Types & Amenities ────────────────────────────
@admin_bp.route('/property-types')
@admin_required
def property_types():
    types    = PropertyType.query.all()
    amenities= Amenity.query.all()
    features = PropertyFeature.query.all()
    return render_template('admin/property_types.html', types=types, amenities=amenities, features=features)


@admin_bp.route('/property-types/add', methods=['POST'])
@admin_required
def add_property_type():
    name = request.form.get('name', '').strip()
    icon = request.form.get('icon', '').strip()
    if name:
        pt = PropertyType(name=name, icon=icon)
        db.session.add(pt)
        db.session.commit()
        flash(f'Property type "{name}" added!', 'success')
    return redirect(url_for('admin.property_types'))


# ── Coupons ───────────────────────────────────────────────
@admin_bp.route('/coupons')
@admin_required
def coupons():
    coupons = Coupon.query.order_by(Coupon.id.desc()).all()
    return render_template('admin/coupons.html', coupons=coupons)


@admin_bp.route('/coupons/add', methods=['POST'])
@admin_required
def add_coupon():
    code  = request.form.get('code', '').strip().upper()
    disc  = request.form.get('discount_pct', 10, type=float)
    maxu  = request.form.get('max_uses', 100, type=int)
    valid = request.form.get('valid_until')
    if not code:
        flash('Coupon code is required.', 'danger')
        return redirect(url_for('admin.coupons'))
    try:
        exp = datetime.strptime(valid, '%Y-%m-%d') if valid else None
    except ValueError:
        flash('Invalid date format.', 'danger')
        return redirect(url_for('admin.coupons'))
    c = Coupon(code=code, discount_pct=disc, max_uses=maxu, valid_until=exp)
    db.session.add(c)
    db.session.commit()
    flash(f'Coupon "{code}" created!', 'success')
    return redirect(url_for('admin.coupons'))
