"""
Public blueprint: homepage, property listings, property detail,
blog, contact, newsletter, about
"""
import os
from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash, session, current_app)
from app import db
from app.models import (Property, PropertyType, City, Area, Blog,
                         ContactMessage, NewsletterSubscriber,
                         PropertyView, SearchLog, Testimonial, FAQ, Agent)
from app.forms.inquiry_forms import ContactForm, NewsletterForm

public_bp = Blueprint('public', __name__, template_folder='../../templates')


# ── Helper ──────────────────────────────────────────────
def log_view(property_id):
    """Record a property page view."""
    pv = PropertyView(
        property_id=property_id,
        user_id=session.get('user_id')
    )
    prop = Property.query.get(property_id)
    if prop:
        prop.views_count = (prop.views_count or 0) + 1
    db.session.add(pv)
    db.session.commit()


# ── Homepage ─────────────────────────────────────────────
@public_bp.route('/')
def index():
    featured    = Property.query.filter_by(is_featured=True, status='Available').limit(6).all()
    latest      = Property.query.filter_by(status='Available').order_by(Property.created_at.desc()).limit(8).all()
    prop_types  = PropertyType.query.all()
    cities      = City.query.all()
    top_agents  = Agent.query.order_by(Agent.rating.desc()).limit(4).all()
    testimonials= Testimonial.query.filter_by(is_active=True).limit(4).all()
    total_props = Property.query.count()
    total_agents= Agent.query.count()
    total_cities= City.query.count()
    total_deals = 500   # static figure for display
    latest_blogs= Blog.query.filter_by(is_published=True).order_by(Blog.published_at.desc()).limit(3).all()
    return render_template('index.html',
        featured=featured, latest=latest, prop_types=prop_types,
        cities=cities, top_agents=top_agents, testimonials=testimonials,
        total_props=total_props, total_agents=total_agents,
        total_cities=total_cities, total_deals=total_deals,
        latest_blogs=latest_blogs)


# ── Properties List ───────────────────────────────────────
@public_bp.route('/properties')
def properties():
    query       = request.args.get('q', '')
    type_id     = request.args.get('type_id', 0, type=int)
    city_id     = request.args.get('city_id', 0, type=int)
    listing_type= request.args.get('listing_type', '')
    min_price   = request.args.get('min_price', 0, type=float)
    max_price   = request.args.get('max_price', 999999999, type=float)
    min_bed     = request.args.get('min_bed', 0, type=int)
    page        = request.args.get('page', 1, type=int)

    # Save search log
    if query and session.get('user_id'):
        sl = SearchLog(user_id=session['user_id'], query=query)
        db.session.add(sl)
        db.session.commit()

    q = Property.query.filter(Property.price.between(min_price, max_price))
    if type_id:
        q = q.filter_by(type_id=type_id)
    if listing_type:
        q = q.filter_by(listing_type=listing_type)
    if city_id:
        q = q.join(Property.location).filter_by(city_id=city_id)
    if query:
        q = q.filter(Property.title.ilike(f'%{query}%'))

    props      = q.order_by(Property.created_at.desc()).paginate(page=page, per_page=9, error_out=False)
    prop_types = PropertyType.query.all()
    cities     = City.query.all()
    filters    = {k: v for k, v in request.args.items() if k != 'page' and v}
    return render_template('properties/list.html',
        props=props, prop_types=prop_types, cities=cities, filters=filters)


# ── Property Detail ───────────────────────────────────────
@public_bp.route('/properties/<int:prop_id>')
def property_detail(prop_id):
    prop         = Property.query.get_or_404(prop_id)
    related      = Property.query.filter(
        Property.type_id == prop.type_id,
        Property.id != prop.id,
        Property.status == 'Available'
    ).limit(4).all()
    price_history = getattr(prop, 'price_history', [])
    log_view(prop_id)
    return render_template('properties/detail.html', prop=prop, related=related, price_history=price_history)


# ── Blog List ─────────────────────────────────────────────
@public_bp.route('/blog')
def blog_list():
    from app.models import BlogTag
    page    = request.args.get('page', 1, type=int)
    posts   = Blog.query.filter_by(is_published=True).order_by(Blog.published_at.desc()).paginate(page=page, per_page=6, error_out=False)
    tags    = BlogTag.query.all()
    popular = Blog.query.filter_by(is_published=True).limit(5).all()
    return render_template('blog/list.html', posts=posts, tags=tags, popular=popular)


# ── Blog Detail ───────────────────────────────────────────
@public_bp.route('/blog/<slug>')
def blog_detail(slug):
    post    = Blog.query.filter_by(slug=slug, is_published=True).first_or_404()
    related = Blog.query.filter(Blog.id != post.id, Blog.is_published == True).limit(3).all()
    post.views = (post.views or 0) + 1
    db.session.commit()
    return render_template('blog/detail.html', post=post, related=related)


# ── About ─────────────────────────────────────────────────
@public_bp.route('/about')
def about():
    top_agents   = Agent.query.order_by(Agent.rating.desc()).limit(6).all()
    total_props  = Property.query.count()
    total_agents = Agent.query.count()
    total_cities = City.query.count()
    total_deals  = 500
    return render_template('about.html', top_agents=top_agents,
        total_props=total_props, total_agents=total_agents,
        total_cities=total_cities, total_deals=total_deals)


# ── Contact ───────────────────────────────────────────────
@public_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        msg = ContactMessage(
            name=form.name.data, email=form.email.data,
            phone=form.phone.data, subject=form.subject.data,
            message=form.message.data
        )
        db.session.add(msg)
        db.session.commit()
        flash('Your message has been sent! We will get back to you soon.', 'success')
        return redirect(url_for('public.contact'))
    return render_template('contact.html', form=form)


# ── Newsletter Subscribe ──────────────────────────────────
@public_bp.route('/subscribe', methods=['POST'])
def subscribe():
    email = request.form.get('email', '').strip()
    if email:
        existing = NewsletterSubscriber.query.filter_by(email=email).first()
        if not existing:
            sub = NewsletterSubscriber(email=email)
            db.session.add(sub)
            db.session.commit()
            flash('Thank you for subscribing to our newsletter!', 'success')
        else:
            flash('You are already subscribed.', 'info')
    return redirect(request.referrer or url_for('public.index'))


# ── Agents List ───────────────────────────────────────────
@public_bp.route('/agents')
def agents_list():
    agents     = Agent.query.order_by(Agent.rating.desc()).all()
    prop_types = PropertyType.query.all()
    cities     = City.query.all()
    return render_template('agents.html', agents=agents, prop_types=prop_types, cities=cities)


# ── Agent Detail ──────────────────────────────────────────
@public_bp.route('/agents/<int:agent_id>')
def agent_detail(agent_id):
    agent      = Agent.query.get_or_404(agent_id)
    properties = Property.query.filter_by(agent_id=agent_id, status='Available').limit(6).all()
    reviews    = agent.reviews if hasattr(agent, 'reviews') else []
    return render_template('agent_detail.html', agent=agent,
                           properties=properties, reviews=reviews)
