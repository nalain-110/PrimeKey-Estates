"""
Agent blueprint: dashboard, listings CRUD, site visits, token receipts,
installment plans, commissions, blog management
"""
import os
import uuid
from functools import wraps
from datetime import datetime, timedelta
from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash, session, current_app)
from werkzeug.utils import secure_filename
from app import db
from app.models import (User, Agent, Property, PropertyImage, PropertyType,
                         City, Area, Location, SiteVisit, Deal, TokenReceipt,
                         InstallmentPlan, InstallmentRecord, Commission,
                         Notification, Inquiry, Offer, Blog, PriceHistory)
from app.forms.property_forms import PropertyForm
from app.forms.deal_forms import (TokenReceiptForm, InstallmentPlanForm,
                                   CommissionForm, DealForm)
from app.forms.blog_forms import BlogForm

agent_bp = Blueprint('agent', __name__, template_folder='../../templates/agent')

ALLOWED = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED


def save_image(file):
    """Save uploaded image and return filename."""
    ext      = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    path     = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(path)
    return filename


def last_n_months(n):
    """Return [(month_start, next_month_start), ...] oldest first."""
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


def agent_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login.', 'warning')
            return redirect(url_for('auth.login'))
        if session.get('user_role') not in [2, 1]:
            flash('Agent access required.', 'danger')
            return redirect(url_for('public.index'))
        return f(*args, **kwargs)
    return decorated


def get_agent():
    return Agent.query.filter_by(user_id=session['user_id']).first()


# ── Dashboard ─────────────────────────────────────────────
@agent_bp.route('/dashboard')
@agent_required
def dashboard():
    agent = get_agent()
    if not agent:
        flash('Agent profile not found.', 'danger')
        return redirect(url_for('public.index'))

    # Stat cards
    listing_count = Property.query.filter_by(agent_id=agent.id, status='Available').count()
    inq_count     = Inquiry.query.join(Property).filter(
        Property.agent_id == agent.id, Inquiry.status == 'Pending').count()
    offer_count   = Offer.query.join(Property).filter(
        Property.agent_id == agent.id, Offer.status == 'Pending').count()
    deal_count    = Deal.query.filter_by(agent_id=agent.id, status='Completed').count()
    total_commission = db.session.query(db.func.sum(Commission.amount)).filter(
        Commission.agent_id == agent.id).scalar() or 0
    visit_count   = SiteVisit.query.filter_by(agent_id=agent.id).count()

    # Chart: this agent's deals per month (last 12 months)
    chart_labels, chart_data = [], []
    for m_start, m_end in last_n_months(12):
        chart_labels.append(m_start.strftime('%b %Y'))
        chart_data.append(Deal.query.filter(
            Deal.agent_id == agent.id,
            Deal.deal_date >= m_start, Deal.deal_date < m_end).count())

    # Recent lists
    recent_inquiries = Inquiry.query.join(Property).filter(
        Property.agent_id == agent.id).order_by(Inquiry.created_at.desc()).limit(5).all()
    recent_listings  = Property.query.filter_by(agent_id=agent.id).order_by(
        Property.created_at.desc()).limit(5).all()

    return render_template('agent/dashboard.html',
        agent=agent,
        listing_count=listing_count, inq_count=inq_count,
        offer_count=offer_count, deal_count=deal_count,
        total_commission=total_commission, visit_count=visit_count,
        chart_labels=chart_labels, chart_data=chart_data,
        recent_inquiries=recent_inquiries, recent_listings=recent_listings)


# ── Listings ──────────────────────────────────────────────
@agent_bp.route('/listings')
@agent_required
def listings():
    agent = get_agent()
    props = Property.query.filter_by(agent_id=agent.id).order_by(Property.created_at.desc()).all()
    return render_template('agent/listings.html', props=props, agent=agent)


@agent_bp.route('/listings/add', methods=['GET', 'POST'])
@agent_required
def add_listing():
    agent = get_agent()
    form  = PropertyForm()
    form.set_type_choices()
    form.set_city_choices()
    if form.validate_on_submit():
        # Create or find location
        loc = Location(
            city_id=form.city_id.data if form.city_id.data else None,
            area_id=form.area_id.data if form.area_id.data else None,
            address=form.address.data,
            map_lat=form.map_lat.data or 0,
            map_lng=form.map_lng.data or 0
        )
        db.session.add(loc)
        db.session.flush()

        prop = Property(
            title       = form.title.data,
            description = form.description.data,
            price       = form.price.data,
            size        = form.size.data,
            size_unit   = form.size_unit.data,
            bedrooms    = form.bedrooms.data or 0,
            bathrooms   = form.bathrooms.data or 0,
            floors      = form.floors.data or 1,
            year_built  = form.year_built.data,
            type_id     = form.type_id.data,
            location_id = loc.id,
            agent_id    = agent.id,
            listing_type= form.listing_type.data,
            status      = form.status.data,
            is_featured = form.is_featured.data,
            is_verified = form.is_verified.data
        )
        db.session.add(prop)
        db.session.flush()

        # Handle image uploads
        files = request.files.getlist('images')
        is_first = True
        for f in files:
            if f and f.filename and allowed_file(f.filename):
                fname = save_image(f)
                img = PropertyImage(property_id=prop.id, image_url=fname, is_primary=is_first)
                db.session.add(img)
                is_first = False

        db.session.commit()
        flash('Property listing added successfully!', 'success')
        return redirect(url_for('agent.listings'))
    return render_template('agent/add_listing.html', form=form, agent=agent)


@agent_bp.route('/listings/<int:prop_id>/edit', methods=['GET', 'POST'])
@agent_required
def edit_listing(prop_id):
    agent = get_agent()
    prop  = Property.query.get_or_404(prop_id)
    if prop.agent_id != agent.id and session.get('user_role') != 1:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('agent.listings'))
    form = PropertyForm(obj=prop)
    form.set_type_choices()
    form.set_city_choices()
    if form.validate_on_submit():
        old_price = prop.price
        prop.title       = form.title.data
        prop.description = form.description.data
        prop.price       = form.price.data
        prop.size        = form.size.data
        prop.size_unit   = form.size_unit.data
        prop.bedrooms    = form.bedrooms.data or 0
        prop.bathrooms   = form.bathrooms.data or 0
        prop.floors      = form.floors.data or 1
        prop.year_built  = form.year_built.data
        prop.type_id     = form.type_id.data
        prop.listing_type= form.listing_type.data
        prop.status      = form.status.data
        prop.is_featured = form.is_featured.data
        prop.is_verified = form.is_verified.data

        # Log price change
        if old_price != form.price.data:
            ph = PriceHistory(property_id=prop.id, old_price=old_price,
                              new_price=form.price.data, changed_by=session['user_id'])
            db.session.add(ph)

        # New images
        files = request.files.getlist('images')
        for f in files:
            if f and f.filename and allowed_file(f.filename):
                fname = save_image(f)
                img = PropertyImage(property_id=prop.id, image_url=fname)
                db.session.add(img)

        db.session.commit()
        flash('Listing updated successfully!', 'success')
        return redirect(url_for('agent.listings'))
    # add_listing.html handles both add and edit (it switches on `prop`)
    return render_template('agent/add_listing.html', form=form, prop=prop, agent=agent)


@agent_bp.route('/listings/<int:prop_id>/delete', methods=['POST'])
@agent_required
def delete_listing(prop_id):
    agent = get_agent()
    prop  = Property.query.get_or_404(prop_id)
    if prop.agent_id != agent.id and session.get('user_role') != 1:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('agent.listings'))
    # Delete associated images from disk
    for img in prop.images:
        img_path = os.path.join(current_app.config['UPLOAD_FOLDER'], img.image_url)
        if os.path.exists(img_path):
            os.remove(img_path)
    db.session.delete(prop)
    db.session.commit()
    flash('Listing deleted.', 'info')
    return redirect(url_for('agent.listings'))


@agent_bp.route('/listings/image/<int:img_id>/delete', methods=['POST'])
@agent_required
def delete_image(img_id):
    agent = get_agent()
    img   = PropertyImage.query.get_or_404(img_id)
    prop  = Property.query.get_or_404(img.property_id)
    if prop.agent_id != agent.id and session.get('user_role') != 1:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('agent.listings'))
    img_path = os.path.join(current_app.config['UPLOAD_FOLDER'], img.image_url)
    if os.path.exists(img_path):
        os.remove(img_path)
    db.session.delete(img)
    db.session.commit()
    flash('Image removed.', 'info')
    return redirect(url_for('agent.edit_listing', prop_id=prop.id))


# ── Site Visits ───────────────────────────────────────────
@agent_bp.route('/visits')
@agent_required
def visits():
    agent  = get_agent()
    visits = SiteVisit.query.filter_by(agent_id=agent.id).order_by(SiteVisit.scheduled_date.asc()).all()
    return render_template('agent/visits.html', visits=visits, agent=agent)


@agent_bp.route('/visits/<int:visit_id>/update', methods=['POST'])
@agent_required
def update_visit(visit_id):
    visit  = SiteVisit.query.get_or_404(visit_id)
    status = request.form.get('status')
    if status in ['Completed', 'Cancelled', 'Scheduled']:
        visit.status = status
        db.session.commit()
        flash(f'Visit status updated to {status}.', 'success')
    return redirect(url_for('agent.visits'))


# ── Inquiries ─────────────────────────────────────────────
@agent_bp.route('/inquiries')
@agent_required
def inquiries():
    agent = get_agent()
    inqs  = Inquiry.query.join(Property).filter(Property.agent_id == agent.id).order_by(Inquiry.created_at.desc()).all()
    return render_template('agent/inquiries.html', inqs=inqs, agent=agent)


@agent_bp.route('/inquiries/<int:inq_id>/reply', methods=['POST'])
@agent_required
def reply_inquiry(inq_id):
    inq   = Inquiry.query.get_or_404(inq_id)
    reply = request.form.get('reply', '').strip()
    if reply:
        inq.reply  = reply
        inq.status = 'Replied'
        notif = Notification(user_id=inq.client_id,
                             message=f'Your inquiry for "{inq.property.title}" has been replied.',
                             link=url_for('client.inquiries'))
        db.session.add(notif)
        db.session.commit()
        flash('Reply sent!', 'success')
    return redirect(url_for('agent.inquiries'))


# ── Offers ────────────────────────────────────────────────
@agent_bp.route('/offers')
@agent_required
def offers():
    agent = get_agent()
    ofs   = Offer.query.join(Property).filter(Property.agent_id == agent.id).order_by(Offer.created_at.desc()).all()
    return render_template('agent/offers.html', ofs=ofs, agent=agent)


@agent_bp.route('/offers/<int:offer_id>/update', methods=['POST'])
@agent_required
def update_offer(offer_id):
    offer  = Offer.query.get_or_404(offer_id)
    status = request.form.get('status')
    counter= request.form.get('counter_price', type=float)
    if status in ['Accepted', 'Rejected', 'Countered']:
        offer.status = status
        if counter:
            offer.counter_price = counter
        notif = Notification(user_id=offer.client_id,
                             message=f'Your offer for "{offer.property.title}" has been {status.lower()}.',
                             link=url_for('client.offers'))
        db.session.add(notif)
        db.session.commit()
        flash(f'Offer {status}.', 'success')
    return redirect(url_for('agent.offers'))


# ── Deals ─────────────────────────────────────────────────
@agent_bp.route('/deals')
@agent_required
def deals():
    agent = get_agent()
    deals = Deal.query.filter_by(agent_id=agent.id).order_by(Deal.deal_date.desc()).all()
    return render_template('agent/deals.html', deals=deals, agent=agent)


@agent_bp.route('/deals/create/<int:prop_id>', methods=['GET', 'POST'])
@agent_required
def create_deal(prop_id):
    agent = get_agent()
    prop  = Property.query.get_or_404(prop_id)
    form  = DealForm()
    form.set_buyer_choices()
    if form.validate_on_submit():
        deal = Deal(
            property_id = prop_id,
            buyer_id    = form.buyer_id.data,
            agent_id    = agent.id,
            deal_price  = form.deal_price.data,
            deal_type   = form.deal_type.data
        )
        db.session.add(deal)
        db.session.flush()
        # Auto-create commission at 2%
        comm = Commission(deal_id=deal.id, agent_id=agent.id,
                          amount=deal.deal_price * 0.02, rate=2.0)
        db.session.add(comm)
        # Update property status
        prop.status = 'Sold' if form.deal_type.data == 'Sale' else 'Rented'
        db.session.commit()
        flash('Deal created successfully!', 'success')
        return redirect(url_for('agent.deals'))
    form.deal_price.data = prop.price
    return render_template('agent/create_deal.html', form=form, prop=prop, agent=agent)


# ── Token Receipts ────────────────────────────────────────
@agent_bp.route('/receipts')
@agent_required
def receipts():
    agent    = get_agent()
    deal_ids = [d.id for d in Deal.query.filter_by(agent_id=agent.id).all()]
    receipts = TokenReceipt.query.filter(TokenReceipt.deal_id.in_(deal_ids)).order_by(TokenReceipt.receipt_date.desc()).all()
    return render_template('agent/receipts.html', receipts=receipts, agent=agent)


@agent_bp.route('/receipts/issue/<int:deal_id>', methods=['GET', 'POST'])
@agent_required
def issue_receipt(deal_id):
    deal = Deal.query.get_or_404(deal_id)
    form = TokenReceiptForm()
    if form.validate_on_submit():
        receipt = TokenReceipt(
            deal_id    = deal_id,
            amount     = form.amount.data,
            receipt_no = form.receipt_no.data,
            notes      = form.notes.data
        )
        db.session.add(receipt)
        db.session.commit()
        flash('Token receipt issued!', 'success')
        return redirect(url_for('agent.receipts'))
    return render_template('agent/issue_receipt.html', form=form, deal=deal)


# ── Installment Plans ─────────────────────────────────────
@agent_bp.route('/installments')
@agent_required
def installments():
    agent    = get_agent()
    deal_ids = [d.id for d in Deal.query.filter_by(agent_id=agent.id).all()]
    plans    = InstallmentPlan.query.filter(InstallmentPlan.deal_id.in_(deal_ids)).all()
    return render_template('agent/installments.html', plans=plans, agent=agent)


@agent_bp.route('/installments/create/<int:deal_id>', methods=['GET', 'POST'])
@agent_required
def create_installment(deal_id):
    deal = Deal.query.get_or_404(deal_id)
    form = InstallmentPlanForm()
    if form.validate_on_submit():
        try:
            start = datetime.strptime(form.start_date.data, '%Y-%m-%d')
        except ValueError:
            start = datetime.utcnow()
        plan = InstallmentPlan(
            deal_id            = deal_id,
            total_amount       = form.total_amount.data,
            down_payment       = form.down_payment.data or 0,
            installments_count = form.installments_count.data,
            frequency          = form.frequency.data,
            start_date         = start
        )
        db.session.add(plan)
        db.session.flush()

        # Generate installment records
        remaining = form.total_amount.data - (form.down_payment.data or 0)
        monthly   = remaining / form.installments_count.data
        freq_days = {'Monthly': 30, 'Quarterly': 90, 'Yearly': 365}
        days      = freq_days.get(form.frequency.data, 30)
        for i in range(form.installments_count.data):
            due = start + timedelta(days=days * (i + 1))
            rec = InstallmentRecord(plan_id=plan.id, due_date=due, amount=round(monthly, 2))
            db.session.add(rec)
        db.session.commit()
        flash('Installment plan created!', 'success')
        return redirect(url_for('agent.installments'))
    form.total_amount.data = deal.deal_price
    return render_template('agent/create_installment.html', form=form, deal=deal)


# ── Commissions ───────────────────────────────────────────
@agent_bp.route('/commissions')
@agent_required
def commissions():
    agent = get_agent()
    comms = Commission.query.filter_by(agent_id=agent.id).order_by(Commission.id.desc()).all()
    total_earned  = sum(c.amount for c in comms if c.status == 'Paid')
    total_pending = sum(c.amount for c in comms if c.status == 'Pending')
    return render_template('agent/commissions.html',
        comms=comms, agent=agent, total_earned=total_earned, total_pending=total_pending)


# ── Blog Management ───────────────────────────────────────
@agent_bp.route('/blogs')
@agent_required
def blogs():
    uid   = session['user_id']
    posts = Blog.query.filter_by(author_id=uid).order_by(Blog.created_at.desc()).all()
    return render_template('agent/blogs.html', posts=posts)


@agent_bp.route('/blogs/add', methods=['GET', 'POST'])
@agent_required
def add_blog():
    form = BlogForm()
    if form.validate_on_submit():
        slug = form.title.data.lower().replace(' ', '-').replace('/', '-')[:220]
        # Ensure slug unique
        existing = Blog.query.filter_by(slug=slug).first()
        if existing:
            slug = f"{slug}-{uuid.uuid4().hex[:6]}"
        cover = None
        if form.cover_image.data and form.cover_image.data.filename:
            cover = save_image(form.cover_image.data)
        blog = Blog(
            title       = form.title.data,
            slug        = slug,
            excerpt     = form.excerpt.data,
            content     = form.content.data,
            cover_image = cover,
            author_id   = session['user_id'],
            is_published= form.is_published.data,
            published_at= datetime.utcnow() if form.is_published.data else None
        )
        db.session.add(blog)
        db.session.commit()
        flash('Blog post saved!', 'success')
        return redirect(url_for('agent.blogs'))
    return render_template('agent/add_blog.html', form=form)


@agent_bp.route('/blogs/<int:blog_id>/delete', methods=['POST'])
@agent_required
def delete_blog(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    if blog.author_id != session['user_id'] and session.get('user_role') != 1:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('agent.blogs'))
    db.session.delete(blog)
    db.session.commit()
    flash('Blog post deleted.', 'info')
    return redirect(url_for('agent.blogs'))
