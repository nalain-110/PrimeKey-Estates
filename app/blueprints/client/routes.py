"""
Client blueprint: dashboard, favorites, inquiries, offers, deals, site visits
"""
from functools import wraps
from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash, session)
from app import db
from app.models import (User, Property, Favorite, Inquiry, Offer,
                         Deal, SiteVisit, Notification)
from app.forms.inquiry_forms import InquiryForm, OfferForm, SiteVisitForm

client_bp = Blueprint('client', __name__, template_folder='../../templates/client')


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to continue.', 'warning')
            return redirect(url_for('auth.login'))
        if session.get('user_role') not in [3, 1]:
            flash('Access denied.', 'danger')
            return redirect(url_for('public.index'))
        return f(*args, **kwargs)
    return decorated


# ── Dashboard ─────────────────────────────────────────────
@client_bp.route('/dashboard')
@login_required
def dashboard():
    uid          = session['user_id']
    user         = User.query.get_or_404(uid)
    fav_count    = Favorite.query.filter_by(client_id=uid).count()
    inq_count    = Inquiry.query.filter_by(client_id=uid).count()
    offer_count  = Offer.query.filter_by(client_id=uid).count()
    deal_count   = Deal.query.filter_by(buyer_id=uid).count()
    visit_count  = SiteVisit.query.filter_by(client_id=uid).count()
    notifs       = Notification.query.filter_by(user_id=uid, is_read=False).order_by(Notification.created_at.desc()).limit(5).all()
    recent_deals = Deal.query.filter_by(buyer_id=uid).order_by(Deal.deal_date.desc()).limit(5).all()
    return render_template('client/dashboard.html',
        user=user, fav_count=fav_count, inq_count=inq_count,
        offer_count=offer_count, deal_count=deal_count,
        visit_count=visit_count, notifs=notifs, recent_deals=recent_deals)


# ── Favorites ─────────────────────────────────────────────
@client_bp.route('/favorites')
@login_required
def favorites():
    uid  = session['user_id']
    favs = Favorite.query.filter_by(client_id=uid).order_by(Favorite.saved_at.desc()).all()
    return render_template('client/favorites.html', favs=favs)


@client_bp.route('/favorites/add/<int:prop_id>', methods=['POST'])
@login_required
def add_favorite(prop_id):
    uid = session['user_id']
    existing = Favorite.query.filter_by(client_id=uid, property_id=prop_id).first()
    if not existing:
        fav = Favorite(client_id=uid, property_id=prop_id)
        db.session.add(fav)
        db.session.commit()
        flash('Property saved to favorites!', 'success')
    else:
        flash('Already in your favorites.', 'info')
    return redirect(request.referrer or url_for('client.favorites'))


@client_bp.route('/favorites/toggle/<int:prop_id>', methods=['POST'])
@login_required
def toggle_favorite(prop_id):
    """Add the property to favorites, or remove it if already saved."""
    uid = session['user_id']
    Property.query.get_or_404(prop_id)
    fav = Favorite.query.filter_by(client_id=uid, property_id=prop_id).first()
    if fav:
        db.session.delete(fav)
        db.session.commit()
        flash('Removed from favorites.', 'info')
    else:
        db.session.add(Favorite(client_id=uid, property_id=prop_id))
        db.session.commit()
        flash('Property saved to favorites!', 'success')
    return redirect(request.referrer or url_for('public.index'))


@client_bp.route('/favorites/remove/<int:fav_id>', methods=['POST'])
@login_required
def remove_favorite(fav_id):
    fav = Favorite.query.get_or_404(fav_id)
    if fav.client_id != session['user_id']:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('client.favorites'))
    db.session.delete(fav)
    db.session.commit()
    flash('Removed from favorites.', 'info')
    return redirect(url_for('client.favorites'))


# ── Inquiries ─────────────────────────────────────────────
@client_bp.route('/inquiries')
@login_required
def inquiries():
    uid  = session['user_id']
    inqs = Inquiry.query.filter_by(client_id=uid).order_by(Inquiry.created_at.desc()).all()
    return render_template('client/inquiries.html', inqs=inqs)


@client_bp.route('/inquiry/send/<int:prop_id>', methods=['GET', 'POST'])
@login_required
def send_inquiry(prop_id):
    prop = Property.query.get_or_404(prop_id)
    form = InquiryForm()
    if form.validate_on_submit():
        inq = Inquiry(
            client_id=session['user_id'],
            property_id=prop_id,
            message=form.message.data
        )
        db.session.add(inq)
        db.session.commit()
        flash('Inquiry sent successfully!', 'success')
        return redirect(url_for('client.inquiries'))
    return render_template('client/send_inquiry.html', form=form, prop=prop)


# ── Offers ────────────────────────────────────────────────
@client_bp.route('/offers')
@login_required
def offers():
    uid  = session['user_id']
    ofs  = Offer.query.filter_by(client_id=uid).order_by(Offer.created_at.desc()).all()
    return render_template('client/offers.html', ofs=ofs)


@client_bp.route('/offer/make/<int:prop_id>', methods=['GET', 'POST'])
@login_required
def make_offer(prop_id):
    prop = Property.query.get_or_404(prop_id)
    form = OfferForm()
    if form.validate_on_submit():
        offer = Offer(
            client_id=session['user_id'],
            property_id=prop_id,
            offered_price=form.offered_price.data,
            notes=form.notes.data
        )
        db.session.add(offer)
        db.session.commit()
        flash('Your offer has been submitted!', 'success')
        return redirect(url_for('client.offers'))
    form.offered_price.data = prop.price
    return render_template('client/make_offer.html', form=form, prop=prop)


# ── Deals ─────────────────────────────────────────────────
@client_bp.route('/deals')
@login_required
def deals():
    uid    = session['user_id']
    deals  = Deal.query.filter_by(buyer_id=uid).order_by(Deal.deal_date.desc()).all()
    return render_template('client/deals.html', deals=deals)


@client_bp.route('/deals/<int:deal_id>')
@login_required
def deal_detail(deal_id):
    deal = Deal.query.get_or_404(deal_id)
    if deal.buyer_id != session['user_id']:
        flash('Access denied.', 'danger')
        return redirect(url_for('client.deals'))
    return render_template('client/deal_detail.html', deal=deal)


# ── Site Visits ───────────────────────────────────────────
@client_bp.route('/visits')
@login_required
def visits():
    uid    = session['user_id']
    visits = SiteVisit.query.filter_by(client_id=uid).order_by(SiteVisit.scheduled_date.desc()).all()
    return render_template('client/visits.html', visits=visits)


@client_bp.route('/visit/schedule/<int:prop_id>', methods=['GET', 'POST'])
@login_required
def schedule_visit(prop_id):
    prop = Property.query.get_or_404(prop_id)
    form = SiteVisitForm()
    if form.validate_on_submit():
        from datetime import datetime
        try:
            sched = datetime.strptime(form.scheduled_date.data, '%Y-%m-%dT%H:%M')
        except ValueError:
            sched = datetime.strptime(form.scheduled_date.data, '%Y-%m-%d')
        visit = SiteVisit(
            property_id=prop_id,
            client_id=session['user_id'],
            scheduled_date=sched,
            notes=form.notes.data
        )
        db.session.add(visit)
        db.session.commit()
        flash('Site visit scheduled! The agent will confirm shortly.', 'success')
        return redirect(url_for('client.visits'))
    return render_template('client/schedule_visit.html', form=form, prop=prop)


# ── Notifications ─────────────────────────────────────────
@client_bp.route('/notifications')
@login_required
def notifications():
    uid   = session['user_id']
    notifs= Notification.query.filter_by(user_id=uid).order_by(Notification.created_at.desc()).all()
    # Mark all as read
    Notification.query.filter_by(user_id=uid, is_read=False).update({'is_read': True})
    db.session.commit()
    return render_template('client/notifications.html', notifs=notifs)
