"""
PrimeKey Estates - SQLAlchemy Models
45 tables covering all real-estate domain entities
"""
from datetime import datetime
from app import db


# ─────────────────────────────────────────────
# 1. ROLES
# ─────────────────────────────────────────────
class Role(db.Model):
    __tablename__ = 'roles'
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    users       = db.relationship('User', back_populates='role', lazy=True)


# ─────────────────────────────────────────────
# 2. USERS
# ─────────────────────────────────────────────
class User(db.Model):
    __tablename__ = 'users'
    id           = db.Column(db.Integer, primary_key=True)
    name         = db.Column(db.String(100), nullable=False)
    email        = db.Column(db.String(120), unique=True, nullable=False)
    password     = db.Column(db.String(200), nullable=False)
    phone        = db.Column(db.String(20))
    cnic         = db.Column(db.String(20))
    profile_pic  = db.Column(db.String(200), default='default_user.png')
    role_id      = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False, default=3)
    is_active    = db.Column(db.Boolean, default=True)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)

    role              = db.relationship('Role', back_populates='users')
    agent_profile     = db.relationship('Agent', back_populates='user', uselist=False)
    favorites         = db.relationship('Favorite', back_populates='client', lazy=True)
    inquiries         = db.relationship('Inquiry', back_populates='client', lazy=True)
    offers            = db.relationship('Offer', back_populates='client', lazy=True)
    deals_as_buyer    = db.relationship('Deal', foreign_keys='Deal.buyer_id', back_populates='buyer', lazy=True)
    site_visits       = db.relationship('SiteVisit', foreign_keys='SiteVisit.client_id', back_populates='client', lazy=True)
    notifications     = db.relationship('Notification', back_populates='user', lazy=True)
    activity_logs     = db.relationship('ActivityLog', back_populates='user', lazy=True)
    blogs             = db.relationship('Blog', back_populates='author', lazy=True)
    shortlists        = db.relationship('Shortlist', back_populates='client', lazy=True)
    property_views    = db.relationship('PropertyView', back_populates='user', lazy=True)
    search_logs       = db.relationship('SearchLog', back_populates='user', lazy=True)
    reviews_given     = db.relationship('AgentReview', back_populates='client', lazy=True)
    rent_as_tenant    = db.relationship('RentAgreement', foreign_keys='RentAgreement.tenant_id', back_populates='tenant', lazy=True)
    maintenance_reqs  = db.relationship('MaintenanceRequest', back_populates='tenant', lazy=True)
    coupon_uses       = db.relationship('CouponUse', back_populates='user', lazy=True)
    business_reports  = db.relationship('BusinessReport', back_populates='generated_by_user', lazy=True)


# ─────────────────────────────────────────────
# 3. CITIES
# ─────────────────────────────────────────────
class City(db.Model):
    __tablename__ = 'cities'
    id       = db.Column(db.Integer, primary_key=True)
    name     = db.Column(db.String(100), nullable=False)
    province = db.Column(db.String(100))
    areas    = db.relationship('Area', back_populates='city', lazy=True)


# ─────────────────────────────────────────────
# 4. AREAS
# ─────────────────────────────────────────────
class Area(db.Model):
    __tablename__ = 'areas'
    id      = db.Column(db.Integer, primary_key=True)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'), nullable=False)
    name    = db.Column(db.String(100), nullable=False)
    city    = db.relationship('City', back_populates='areas')
    sectors = db.relationship('Sector', back_populates='area', lazy=True)


# ─────────────────────────────────────────────
# 5. SECTORS
# ─────────────────────────────────────────────
class Sector(db.Model):
    __tablename__ = 'sectors'
    id      = db.Column(db.Integer, primary_key=True)
    area_id = db.Column(db.Integer, db.ForeignKey('areas.id'), nullable=False)
    name    = db.Column(db.String(100), nullable=False)
    area    = db.relationship('Area', back_populates='sectors')


# ─────────────────────────────────────────────
# 6. LOCATIONS
# ─────────────────────────────────────────────
class Location(db.Model):
    __tablename__ = 'locations'
    id         = db.Column(db.Integer, primary_key=True)
    city_id    = db.Column(db.Integer, db.ForeignKey('cities.id'))
    area_id    = db.Column(db.Integer, db.ForeignKey('areas.id'))
    sector_id  = db.Column(db.Integer, db.ForeignKey('sectors.id'))
    address    = db.Column(db.String(300))
    map_lat    = db.Column(db.Float, default=0.0)
    map_lng    = db.Column(db.Float, default=0.0)
    city       = db.relationship('City')
    area       = db.relationship('Area')
    sector     = db.relationship('Sector')
    properties = db.relationship('Property', back_populates='location', lazy=True)


# ─────────────────────────────────────────────
# 7. PROPERTY TYPES
# ─────────────────────────────────────────────
class PropertyType(db.Model):
    __tablename__ = 'property_types'
    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(50), nullable=False)   # House/Plot/Flat/Shop
    icon       = db.Column(db.String(100))
    properties = db.relationship('Property', back_populates='property_type', lazy=True)


# ─────────────────────────────────────────────
# 8. AGENTS
# ─────────────────────────────────────────────
class Agent(db.Model):
    __tablename__ = 'agents'
    id               = db.Column(db.Integer, primary_key=True)
    user_id          = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    agency_name      = db.Column(db.String(150))
    license_no       = db.Column(db.String(50))
    experience_years = db.Column(db.Integer, default=0)
    bio              = db.Column(db.Text)
    rating           = db.Column(db.Float, default=0.0)
    total_deals      = db.Column(db.Integer, default=0)

    user        = db.relationship('User', back_populates='agent_profile')
    properties  = db.relationship('Property', back_populates='agent', lazy=True)
    commissions = db.relationship('Commission', back_populates='agent', lazy=True)
    reviews     = db.relationship('AgentReview', back_populates='agent', lazy=True)
    deals       = db.relationship('Deal', foreign_keys='Deal.agent_id', back_populates='agent', lazy=True)
    site_visits = db.relationship('SiteVisit', foreign_keys='SiteVisit.agent_id', back_populates='agent', lazy=True)


# ─────────────────────────────────────────────
# 9. PROPERTIES
# ─────────────────────────────────────────────
class Property(db.Model):
    __tablename__ = 'properties'
    id           = db.Column(db.Integer, primary_key=True)
    title        = db.Column(db.String(200), nullable=False)
    description  = db.Column(db.Text)
    price        = db.Column(db.Float, nullable=False)
    size         = db.Column(db.Float)              # in marla or sq ft
    size_unit    = db.Column(db.String(20), default='Marla')
    bedrooms     = db.Column(db.Integer, default=0)
    bathrooms    = db.Column(db.Integer, default=0)
    floors       = db.Column(db.Integer, default=1)
    year_built   = db.Column(db.Integer)
    type_id      = db.Column(db.Integer, db.ForeignKey('property_types.id'), nullable=False)
    location_id  = db.Column(db.Integer, db.ForeignKey('locations.id'))
    agent_id     = db.Column(db.Integer, db.ForeignKey('agents.id'))
    status       = db.Column(db.String(30), default='Available')   # Available/Sold/Rented
    listing_type = db.Column(db.String(20), default='Sale')        # Sale/Rent
    is_featured  = db.Column(db.Boolean, default=False)
    is_verified  = db.Column(db.Boolean, default=False)
    views_count  = db.Column(db.Integer, default=0)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at   = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    property_type   = db.relationship('PropertyType', back_populates='properties')
    location        = db.relationship('Location', back_populates='properties')
    agent           = db.relationship('Agent', back_populates='properties')
    images          = db.relationship('PropertyImage', back_populates='property', lazy=True, cascade='all, delete-orphan')
    features        = db.relationship('PropertyFeatureMap', back_populates='property', lazy=True, cascade='all, delete-orphan')
    amenities       = db.relationship('PropertyAmenity', back_populates='property', lazy=True, cascade='all, delete-orphan')
    favorites       = db.relationship('Favorite', back_populates='property', lazy=True)
    inquiries       = db.relationship('Inquiry', back_populates='property', lazy=True)
    offers          = db.relationship('Offer', back_populates='property', lazy=True)
    deals           = db.relationship('Deal', back_populates='property', lazy=True)
    site_visits     = db.relationship('SiteVisit', back_populates='property', lazy=True)
    price_history   = db.relationship('PriceHistory', back_populates='property', lazy=True)
    prop_views      = db.relationship('PropertyView', back_populates='property', lazy=True)
    listing         = db.relationship('Listing', back_populates='property', uselist=False, lazy=True)
    shortlist_items = db.relationship('ShortlistProperty', back_populates='property', lazy=True)
    rent_agreements = db.relationship('RentAgreement', back_populates='property', lazy=True)
    maintenance_reqs= db.relationship('MaintenanceRequest', back_populates='property', lazy=True)


# ─────────────────────────────────────────────
# 10. PROPERTY IMAGES
# ─────────────────────────────────────────────
class PropertyImage(db.Model):
    __tablename__ = 'property_images'
    id          = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    image_url   = db.Column(db.String(300), nullable=False)
    is_primary  = db.Column(db.Boolean, default=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    property    = db.relationship('Property', back_populates='images')


# ─────────────────────────────────────────────
# 11. PROPERTY FEATURES
# ─────────────────────────────────────────────
class PropertyFeature(db.Model):
    __tablename__ = 'property_features'
    id      = db.Column(db.Integer, primary_key=True)
    name    = db.Column(db.String(100), nullable=False, unique=True)   # Garage, Pool, Garden …
    maps    = db.relationship('PropertyFeatureMap', back_populates='feature', lazy=True)


class PropertyFeatureMap(db.Model):
    __tablename__ = 'property_feature_map'
    id          = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    feature_id  = db.Column(db.Integer, db.ForeignKey('property_features.id'), nullable=False)
    property    = db.relationship('Property', back_populates='features')
    feature     = db.relationship('PropertyFeature', back_populates='maps')


# ─────────────────────────────────────────────
# 12. AMENITIES
# ─────────────────────────────────────────────
class Amenity(db.Model):
    __tablename__ = 'amenities'
    id   = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    icon = db.Column(db.String(50))
    maps = db.relationship('PropertyAmenity', back_populates='amenity', lazy=True)


class PropertyAmenity(db.Model):
    __tablename__ = 'property_amenities'
    id          = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    amenity_id  = db.Column(db.Integer, db.ForeignKey('amenities.id'), nullable=False)
    property    = db.relationship('Property', back_populates='amenities')
    amenity     = db.relationship('Amenity', back_populates='maps')


# ─────────────────────────────────────────────
# 13. LISTINGS
# ─────────────────────────────────────────────
class Listing(db.Model):
    __tablename__ = 'listings'
    id           = db.Column(db.Integer, primary_key=True)
    property_id  = db.Column(db.Integer, db.ForeignKey('properties.id'), unique=True, nullable=False)
    listing_type = db.Column(db.String(20), nullable=False, default='Sale')   # Sale / Rent
    listed_price = db.Column(db.Float)
    listed_date  = db.Column(db.DateTime, default=datetime.utcnow)
    expiry_date  = db.Column(db.DateTime)
    is_active    = db.Column(db.Boolean, default=True)
    property     = db.relationship('Property', back_populates='listing')


# ─────────────────────────────────────────────
# 14. FAVORITES
# ─────────────────────────────────────────────
class Favorite(db.Model):
    __tablename__ = 'favorites'
    id          = db.Column(db.Integer, primary_key=True)
    client_id   = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    saved_at    = db.Column(db.DateTime, default=datetime.utcnow)
    client      = db.relationship('User', back_populates='favorites')
    property    = db.relationship('Property', back_populates='favorites')


# ─────────────────────────────────────────────
# 15. INQUIRIES
# ─────────────────────────────────────────────
class Inquiry(db.Model):
    __tablename__ = 'inquiries'
    id          = db.Column(db.Integer, primary_key=True)
    client_id   = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    message     = db.Column(db.Text, nullable=False)
    status      = db.Column(db.String(30), default='Pending')   # Pending/Replied/Closed
    reply       = db.Column(db.Text)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    client      = db.relationship('User', back_populates='inquiries')
    property    = db.relationship('Property', back_populates='inquiries')


# ─────────────────────────────────────────────
# 16. OFFERS
# ─────────────────────────────────────────────
class Offer(db.Model):
    __tablename__ = 'offers'
    id            = db.Column(db.Integer, primary_key=True)
    client_id     = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    property_id   = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    offered_price = db.Column(db.Float, nullable=False)
    status        = db.Column(db.String(30), default='Pending')  # Pending/Accepted/Rejected/Countered
    notes         = db.Column(db.Text)
    counter_price = db.Column(db.Float)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    client        = db.relationship('User', back_populates='offers')
    property      = db.relationship('Property', back_populates='offers')


# ─────────────────────────────────────────────
# 17. DEALS
# ─────────────────────────────────────────────
class Deal(db.Model):
    __tablename__ = 'deals'
    id          = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    buyer_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    agent_id    = db.Column(db.Integer, db.ForeignKey('agents.id'))
    deal_price  = db.Column(db.Float, nullable=False)
    status      = db.Column(db.String(30), default='In Progress')  # In Progress/Completed/Cancelled
    deal_type   = db.Column(db.String(20), default='Sale')         # Sale / Rent
    deal_date   = db.Column(db.DateTime, default=datetime.utcnow)
    closed_at   = db.Column(db.DateTime)

    property          = db.relationship('Property', back_populates='deals')
    buyer             = db.relationship('User', foreign_keys=[buyer_id], back_populates='deals_as_buyer')
    agent             = db.relationship('Agent', foreign_keys=[agent_id], back_populates='deals')
    token_receipts    = db.relationship('TokenReceipt', back_populates='deal', lazy=True)
    installment_plans = db.relationship('InstallmentPlan', back_populates='deal', lazy=True)
    commissions       = db.relationship('Commission', back_populates='deal', lazy=True)
    payments          = db.relationship('Payment', back_populates='deal', lazy=True)
    documents         = db.relationship('Document', back_populates='deal', lazy=True)


# ─────────────────────────────────────────────
# 18. SITE VISITS
# ─────────────────────────────────────────────
class SiteVisit(db.Model):
    __tablename__ = 'site_visits'
    id             = db.Column(db.Integer, primary_key=True)
    property_id    = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    client_id      = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    agent_id       = db.Column(db.Integer, db.ForeignKey('agents.id'))
    scheduled_date = db.Column(db.DateTime, nullable=False)
    status         = db.Column(db.String(30), default='Scheduled')  # Scheduled/Completed/Cancelled
    notes          = db.Column(db.Text)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

    property = db.relationship('Property', back_populates='site_visits')
    client   = db.relationship('User', foreign_keys=[client_id], back_populates='site_visits')
    agent    = db.relationship('Agent', foreign_keys=[agent_id], back_populates='site_visits')


# ─────────────────────────────────────────────
# 19. TOKEN RECEIPTS
# ─────────────────────────────────────────────
class TokenReceipt(db.Model):
    __tablename__ = 'token_receipts'
    id           = db.Column(db.Integer, primary_key=True)
    deal_id      = db.Column(db.Integer, db.ForeignKey('deals.id'), nullable=False)
    amount       = db.Column(db.Float, nullable=False)
    receipt_no   = db.Column(db.String(50), unique=True)
    receipt_date = db.Column(db.DateTime, default=datetime.utcnow)
    notes        = db.Column(db.Text)
    deal         = db.relationship('Deal', back_populates='token_receipts')


# ─────────────────────────────────────────────
# 20. INSTALLMENT PLANS
# ─────────────────────────────────────────────
class InstallmentPlan(db.Model):
    __tablename__ = 'installment_plans'
    id                 = db.Column(db.Integer, primary_key=True)
    deal_id            = db.Column(db.Integer, db.ForeignKey('deals.id'), nullable=False)
    total_amount       = db.Column(db.Float, nullable=False)
    down_payment       = db.Column(db.Float, default=0.0)
    installments_count = db.Column(db.Integer, nullable=False)
    frequency          = db.Column(db.String(20), default='Monthly')  # Monthly/Quarterly/Yearly
    start_date         = db.Column(db.DateTime, default=datetime.utcnow)
    created_at         = db.Column(db.DateTime, default=datetime.utcnow)

    deal    = db.relationship('Deal', back_populates='installment_plans')
    records = db.relationship('InstallmentRecord', back_populates='plan', lazy=True, cascade='all, delete-orphan')


# ─────────────────────────────────────────────
# 21. INSTALLMENT RECORDS
# ─────────────────────────────────────────────
class InstallmentRecord(db.Model):
    __tablename__ = 'installment_records'
    id        = db.Column(db.Integer, primary_key=True)
    plan_id   = db.Column(db.Integer, db.ForeignKey('installment_plans.id'), nullable=False)
    due_date  = db.Column(db.DateTime, nullable=False)
    amount    = db.Column(db.Float, nullable=False)
    paid_date = db.Column(db.DateTime)
    status    = db.Column(db.String(20), default='Pending')   # Pending/Paid/Overdue
    plan      = db.relationship('InstallmentPlan', back_populates='records')


# ─────────────────────────────────────────────
# 22. COMMISSIONS
# ─────────────────────────────────────────────
class Commission(db.Model):
    __tablename__ = 'commissions'
    id        = db.Column(db.Integer, primary_key=True)
    deal_id   = db.Column(db.Integer, db.ForeignKey('deals.id'), nullable=False)
    agent_id  = db.Column(db.Integer, db.ForeignKey('agents.id'), nullable=False)
    amount    = db.Column(db.Float, nullable=False)
    rate      = db.Column(db.Float, default=2.0)   # percentage
    paid_date = db.Column(db.DateTime)
    status    = db.Column(db.String(20), default='Pending')   # Pending/Paid
    deal      = db.relationship('Deal', back_populates='commissions')
    agent     = db.relationship('Agent', back_populates='commissions')


# ─────────────────────────────────────────────
# 23. PAYMENTS
# ─────────────────────────────────────────────
class Payment(db.Model):
    __tablename__ = 'payments'
    id           = db.Column(db.Integer, primary_key=True)
    deal_id      = db.Column(db.Integer, db.ForeignKey('deals.id'), nullable=False)
    amount       = db.Column(db.Float, nullable=False)
    payment_type = db.Column(db.String(50))   # Cash/Bank Transfer/Cheque
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    notes        = db.Column(db.Text)
    deal         = db.relationship('Deal', back_populates='payments')


# ─────────────────────────────────────────────
# 24. NOTIFICATIONS
# ─────────────────────────────────────────────
class Notification(db.Model):
    __tablename__ = 'notifications'
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message    = db.Column(db.Text, nullable=False)
    link       = db.Column(db.String(200))
    is_read    = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user       = db.relationship('User', back_populates='notifications')


# ─────────────────────────────────────────────
# 25. ACTIVITY LOGS
# ─────────────────────────────────────────────
class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'))
    action     = db.Column(db.String(200), nullable=False)
    table_name = db.Column(db.String(100))
    record_id  = db.Column(db.Integer)
    timestamp  = db.Column(db.DateTime, default=datetime.utcnow)
    user       = db.relationship('User', back_populates='activity_logs')


# ─────────────────────────────────────────────
# 26. AGENT REVIEWS
# ─────────────────────────────────────────────
class AgentReview(db.Model):
    __tablename__ = 'agent_reviews'
    id         = db.Column(db.Integer, primary_key=True)
    agent_id   = db.Column(db.Integer, db.ForeignKey('agents.id'), nullable=False)
    client_id  = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating     = db.Column(db.Float, nullable=False)
    comment    = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    agent      = db.relationship('Agent', back_populates='reviews')
    client     = db.relationship('User', back_populates='reviews_given')


# ─────────────────────────────────────────────
# 27. BLOGS
# ─────────────────────────────────────────────
class Blog(db.Model):
    __tablename__ = 'blogs'
    id           = db.Column(db.Integer, primary_key=True)
    title        = db.Column(db.String(200), nullable=False)
    slug         = db.Column(db.String(220), unique=True, nullable=False)
    content      = db.Column(db.Text, nullable=False)
    excerpt      = db.Column(db.String(300))
    cover_image  = db.Column(db.String(300))
    author_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_published = db.Column(db.Boolean, default=False)
    published_at = db.Column(db.DateTime)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)
    author       = db.relationship('User', back_populates='blogs')
    tags         = db.relationship('BlogTagMap', back_populates='blog', lazy=True, cascade='all, delete-orphan')


# ─────────────────────────────────────────────
# 28. BLOG TAGS
# ─────────────────────────────────────────────
class BlogTag(db.Model):
    __tablename__ = 'blog_tags'
    id   = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    maps = db.relationship('BlogTagMap', back_populates='tag', lazy=True)


class BlogTagMap(db.Model):
    __tablename__ = 'blog_tag_map'
    id      = db.Column(db.Integer, primary_key=True)
    blog_id = db.Column(db.Integer, db.ForeignKey('blogs.id'), nullable=False)
    tag_id  = db.Column(db.Integer, db.ForeignKey('blog_tags.id'), nullable=False)
    blog    = db.relationship('Blog', back_populates='tags')
    tag     = db.relationship('BlogTag', back_populates='maps')


# ─────────────────────────────────────────────
# 29. CONTACT MESSAGES
# ─────────────────────────────────────────────
class ContactMessage(db.Model):
    __tablename__ = 'contact_messages'
    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(100), nullable=False)
    email      = db.Column(db.String(120), nullable=False)
    phone      = db.Column(db.String(20))
    subject    = db.Column(db.String(200))
    message    = db.Column(db.Text, nullable=False)
    is_read    = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ─────────────────────────────────────────────
# 30. NEWSLETTER SUBSCRIBERS
# ─────────────────────────────────────────────
class NewsletterSubscriber(db.Model):
    __tablename__ = 'newsletter_subscribers'
    id            = db.Column(db.Integer, primary_key=True)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    subscribed_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active     = db.Column(db.Boolean, default=True)


# ─────────────────────────────────────────────
# 31. PROPERTY VIEWS
# ─────────────────────────────────────────────
class PropertyView(db.Model):
    __tablename__ = 'property_views'
    id          = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'))
    viewed_at   = db.Column(db.DateTime, default=datetime.utcnow)
    property    = db.relationship('Property', back_populates='prop_views')
    user        = db.relationship('User', back_populates='property_views')


# ─────────────────────────────────────────────
# 32. SEARCH LOGS
# ─────────────────────────────────────────────
class SearchLog(db.Model):
    __tablename__ = 'search_logs'
    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'))
    query       = db.Column(db.String(300))
    filters_json= db.Column(db.Text)
    searched_at = db.Column(db.DateTime, default=datetime.utcnow)
    user        = db.relationship('User', back_populates='search_logs')


# ─────────────────────────────────────────────
# 33. SHORTLISTS
# ─────────────────────────────────────────────
class Shortlist(db.Model):
    __tablename__ = 'shortlists'
    id         = db.Column(db.Integer, primary_key=True)
    client_id  = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name       = db.Column(db.String(100), default='My List')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    client     = db.relationship('User', back_populates='shortlists')
    items      = db.relationship('ShortlistProperty', back_populates='shortlist', lazy=True, cascade='all, delete-orphan')


class ShortlistProperty(db.Model):
    __tablename__ = 'shortlist_properties'
    id           = db.Column(db.Integer, primary_key=True)
    shortlist_id = db.Column(db.Integer, db.ForeignKey('shortlists.id'), nullable=False)
    property_id  = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    added_at     = db.Column(db.DateTime, default=datetime.utcnow)
    shortlist    = db.relationship('Shortlist', back_populates='items')
    property     = db.relationship('Property', back_populates='shortlist_items')


# ─────────────────────────────────────────────
# 34. PRICE HISTORY
# ─────────────────────────────────────────────
class PriceHistory(db.Model):
    __tablename__ = 'price_history'
    id          = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    old_price   = db.Column(db.Float)
    new_price   = db.Column(db.Float)
    changed_at  = db.Column(db.DateTime, default=datetime.utcnow)
    changed_by  = db.Column(db.Integer, db.ForeignKey('users.id'))
    property    = db.relationship('Property', back_populates='price_history')


# ─────────────────────────────────────────────
# 35. DOCUMENTS
# ─────────────────────────────────────────────
class Document(db.Model):
    __tablename__ = 'documents'
    id          = db.Column(db.Integer, primary_key=True)
    deal_id     = db.Column(db.Integer, db.ForeignKey('deals.id'), nullable=False)
    name        = db.Column(db.String(200), nullable=False)
    file_url    = db.Column(db.String(300), nullable=False)
    doc_type    = db.Column(db.String(50))   # Agreement/Receipt/NOC
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    deal        = db.relationship('Deal', back_populates='documents')


# ─────────────────────────────────────────────
# 36. SETTINGS
# ─────────────────────────────────────────────
class Setting(db.Model):
    __tablename__ = 'settings'
    id          = db.Column(db.Integer, primary_key=True)
    key         = db.Column(db.String(100), unique=True, nullable=False)
    value       = db.Column(db.Text)
    description = db.Column(db.String(300))


# ─────────────────────────────────────────────
# 37. BUSINESS REPORTS
# ─────────────────────────────────────────────
class BusinessReport(db.Model):
    __tablename__ = 'business_reports'
    id              = db.Column(db.Integer, primary_key=True)
    report_type     = db.Column(db.String(100), nullable=False)
    generated_by    = db.Column(db.Integer, db.ForeignKey('users.id'))
    generated_at    = db.Column(db.DateTime, default=datetime.utcnow)
    data_json       = db.Column(db.Text)
    generated_by_user = db.relationship('User', back_populates='business_reports')


# ─────────────────────────────────────────────
# 38. RENT AGREEMENTS
# ─────────────────────────────────────────────
class RentAgreement(db.Model):
    __tablename__ = 'rent_agreements'
    id            = db.Column(db.Integer, primary_key=True)
    property_id   = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    tenant_id     = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    landlord_id   = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    start_date    = db.Column(db.DateTime, nullable=False)
    end_date      = db.Column(db.DateTime, nullable=False)
    monthly_rent  = db.Column(db.Float, nullable=False)
    deposit       = db.Column(db.Float, default=0.0)
    status        = db.Column(db.String(20), default='Active')   # Active/Expired/Terminated
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    property      = db.relationship('Property', back_populates='rent_agreements')
    tenant        = db.relationship('User', foreign_keys=[tenant_id], back_populates='rent_as_tenant')
    landlord      = db.relationship('User', foreign_keys=[landlord_id])


# ─────────────────────────────────────────────
# 39. MAINTENANCE REQUESTS
# ─────────────────────────────────────────────
class MaintenanceRequest(db.Model):
    __tablename__ = 'maintenance_requests'
    id          = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    tenant_id   = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    priority    = db.Column(db.String(20), default='Normal')  # Low/Normal/High/Urgent
    status      = db.Column(db.String(30), default='Pending') # Pending/In Progress/Resolved
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    property    = db.relationship('Property', back_populates='maintenance_reqs')
    tenant      = db.relationship('User', back_populates='maintenance_reqs')


# ─────────────────────────────────────────────
# 40. COUPONS
# ─────────────────────────────────────────────
class Coupon(db.Model):
    __tablename__ = 'coupons'
    id           = db.Column(db.Integer, primary_key=True)
    code         = db.Column(db.String(50), unique=True, nullable=False)
    discount_pct = db.Column(db.Float, nullable=False)
    valid_from   = db.Column(db.DateTime, default=datetime.utcnow)
    valid_until  = db.Column(db.DateTime)
    max_uses     = db.Column(db.Integer, default=100)
    used_count   = db.Column(db.Integer, default=0)
    is_active    = db.Column(db.Boolean, default=True)
    uses         = db.relationship('CouponUse', back_populates='coupon', lazy=True)


# ─────────────────────────────────────────────
# 41. COUPON USES
# ─────────────────────────────────────────────
class CouponUse(db.Model):
    __tablename__ = 'coupon_uses'
    id        = db.Column(db.Integer, primary_key=True)
    coupon_id = db.Column(db.Integer, db.ForeignKey('coupons.id'), nullable=False)
    user_id   = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    used_at   = db.Column(db.DateTime, default=datetime.utcnow)
    coupon    = db.relationship('Coupon', back_populates='uses')
    user      = db.relationship('User', back_populates='coupon_uses')


# ─────────────────────────────────────────────
# 42. PROPERTY SCHEDULES (open house events)
# ─────────────────────────────────────────────
class PropertySchedule(db.Model):
    __tablename__ = 'property_schedules'
    id          = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    event_name  = db.Column(db.String(200))
    event_date  = db.Column(db.DateTime, nullable=False)
    duration_hr = db.Column(db.Float, default=1.0)
    notes       = db.Column(db.Text)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)


# ─────────────────────────────────────────────
# 43. TESTIMONIALS
# ─────────────────────────────────────────────
class Testimonial(db.Model):
    __tablename__ = 'testimonials'
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'))
    name       = db.Column(db.String(100), nullable=False)
    message    = db.Column(db.Text, nullable=False)
    rating     = db.Column(db.Float, default=5.0)
    avatar     = db.Column(db.String(200))
    is_active  = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ─────────────────────────────────────────────
# 44. FAQ
# ─────────────────────────────────────────────
class FAQ(db.Model):
    __tablename__ = 'faqs'
    id         = db.Column(db.Integer, primary_key=True)
    question   = db.Column(db.String(300), nullable=False)
    answer     = db.Column(db.Text, nullable=False)
    category   = db.Column(db.String(100))
    sort_order = db.Column(db.Integer, default=0)
    is_active  = db.Column(db.Boolean, default=True)


# ─────────────────────────────────────────────
# 45. AGENCY (Company level info)
# ─────────────────────────────────────────────
class Agency(db.Model):
    __tablename__ = 'agencies'
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(200), nullable=False)
    logo        = db.Column(db.String(300))
    address     = db.Column(db.Text)
    phone       = db.Column(db.String(20))
    email       = db.Column(db.String(120))
    website     = db.Column(db.String(200))
    description = db.Column(db.Text)
    license_no  = db.Column(db.String(50))
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
