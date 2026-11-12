"""
seed_db.py — Populate PrimeKey Estates with demo data for viva/testing
Run: python seed_db.py
"""
from app import create_app, db
from app.models import (
    Role, User, Agent, PropertyType, City, Area, Location,
    Property, Testimonial, Blog, Setting
)
from werkzeug.security import generate_password_hash
from datetime import datetime
import random

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()
    print("Tables created.")

    # ── Roles ───────────────────────────────────────
    r_admin  = Role(id=1, name='Admin',  description='System Administrator')
    r_agent  = Role(id=2, name='Agent',  description='Property Agent')
    r_client = Role(id=3, name='Client', description='Property Buyer/Renter')
    db.session.add_all([r_admin, r_agent, r_client])
    db.session.commit()

    # ── Property Types ───────────────────────────────
    type_names = ['House', 'Plot', 'Flat', 'Shop', 'Office', 'Warehouse']
    ptype_objs = []
    for t in type_names:
        pt = PropertyType(name=t, icon=f'fa-{t.lower()}')
        db.session.add(pt)
        ptype_objs.append(pt)
    db.session.commit()

    # ── Cities & Areas ───────────────────────────────
    city_data = {
        'Lahore':     ['DHA Phase 5', 'DHA Phase 6', 'Gulberg', 'Model Town', 'Johar Town'],
        'Karachi':    ['Clifton', 'DHA Karachi', 'Bahria Town', 'North Nazimabad', 'Gulshan'],
        'Islamabad':  ['F-7', 'F-8', 'G-11', 'DHA Islamabad', 'Bahria Town Islamabad'],
        'Rawalpindi': ['Bahria Phase 4', 'Saddar', 'Chaklala', 'Askari 14'],
        'Faisalabad': ['Gulberg', 'Peoples Colony', 'Jinnah Colony'],
    }
    city_objs = {}
    area_objs = {}
    for city_name, areas_list in city_data.items():
        prov = 'Punjab' if city_name in ['Lahore','Faisalabad','Rawalpindi','Islamabad'] else 'Sindh'
        c = City(name=city_name, province=prov)
        db.session.add(c)
        db.session.flush()
        city_objs[city_name] = c
        area_objs[city_name] = []
        for area_name in areas_list:
            a = Area(name=area_name, city_id=c.id)
            db.session.add(a)
            db.session.flush()
            area_objs[city_name].append(a)
    db.session.commit()

    # ── Admin User ───────────────────────────────────
    admin = User(
        name='Admin User', email='admin@primekeyestates.pk',
        password=generate_password_hash('admin123'),
        phone='+92421111111', role_id=1, is_active=True
    )
    db.session.add(admin)
    db.session.commit()

    # ── Agent Users ──────────────────────────────────
    agent_info = [
        ('Ahmed Raza', 'ahmed@primekeyestates.pk', '+923001234567', 'Prime Realty', 5),
        ('Sara Khan', 'sara@primekeyestates.pk', '+923219876543', 'Elite Homes', 3),
        ('Bilal Chaudhry', 'bilal@primekeyestates.pk', '+923335556666', 'Chaudhry Estate', 8),
        ('Fatima Malik', 'fatima@primekeyestates.pk', '+923112223344', 'City Properties', 2),
    ]
    agent_users = []
    agent_records = []
    for name, email, phone, agency, exp in agent_info:
        u = User(
            name=name, email=email,
            password=generate_password_hash('agent123'),
            phone=phone, role_id=2, is_active=True
        )
        db.session.add(u)
        db.session.flush()
        a = Agent(
            user_id=u.id, agency_name=agency,
            license_no=f'LIC-{random.randint(10000,99999)}',
            experience_years=exp,
            rating=round(random.uniform(3.5, 5.0), 1),
            total_deals=random.randint(10, 80)
        )
        db.session.add(a)
        db.session.flush()
        agent_users.append(u)
        agent_records.append(a)
    db.session.commit()

    # ── Client Users ─────────────────────────────────
    for name, email, phone in [
        ('Usman Ali', 'usman@gmail.com', '+923009988776'),
        ('Ayesha Tariq', 'ayesha@gmail.com', '+923211122334'),
        ('Kamran Zafar', 'kamran@gmail.com', '+923334455667'),
    ]:
        u = User(
            name=name, email=email,
            password=generate_password_hash('client123'),
            phone=phone, role_id=3, is_active=True
        )
        db.session.add(u)
    db.session.commit()

    # ── Locations + Properties ───────────────────────
    prop_data = [
        ('5 Marla House in DHA Phase 5',  'House',  'Sale',  12500000, 'Lahore',    'DHA Phase 5',        3, 3, 10, 2),
        ('10 Marla House Gulberg',         'House',  'Sale',  28000000, 'Lahore',    'Gulberg',             4, 4, 20, 3),
        ('1 Kanal House Model Town',       'House',  'Sale',  55000000, 'Lahore',    'Model Town',          5, 5, 40, 4),
        ('2 Bed Flat Clifton Karachi',     'Flat',   'Rent',  85000,    'Karachi',   'Clifton',             2, 2, 8,  1),
        ('5 Marla Plot DHA Islamabad',     'Plot',   'Sale',  8500000,  'Islamabad', 'DHA Islamabad',       0, 0, 10, 0),
        ('3 Marla Shop Gulberg Lahore',    'Shop',   'Sale',  18000000, 'Lahore',    'Gulberg',             0, 1, 6,  0),
        ('Studio Flat F-7 Islamabad',      'Flat',   'Rent',  45000,    'Islamabad', 'F-7',                 1, 1, 4,  1),
        ('10 Marla Plot Bahria Phase 4',   'Plot',   'Sale',  15000000, 'Rawalpindi','Bahria Phase 4',      0, 0, 20, 0),
        ('4 Bed House DHA Karachi',        'House',  'Sale',  42000000, 'Karachi',   'DHA Karachi',         4, 4, 20, 3),
        ('Office F-8 Islamabad',           'Office', 'Rent',  120000,   'Islamabad', 'F-8',                 0, 2, 12, 0),
    ]
    props = []
    for i, (title, ptype, ltype, price, city_name, area_name, beds, baths, size, floors) in enumerate(prop_data):
        city = city_objs[city_name]
        area = next((a for a in area_objs[city_name] if a.name == area_name), area_objs[city_name][0])
        pt   = next((p for p in ptype_objs if p.name == ptype), ptype_objs[0])
        agent= agent_records[i % len(agent_records)]

        # Create Location row
        loc = Location(city_id=city.id, area_id=area.id, address=f'{area_name}, {city_name}')
        db.session.add(loc)
        db.session.flush()

        p = Property(
            title=title,
            description=f'Beautiful {title}. Well maintained in prime location with easy access to schools, hospitals and shopping centers.',
            type_id=pt.id,
            listing_type=ltype,
            price=price,
            location_id=loc.id,
            size=size,
            size_unit='Marla',
            bedrooms=beds,
            bathrooms=baths,
            floors=floors,
            year_built=2015 + i,
            agent_id=agent.id,
            status='Available',
            is_featured=(i % 3 == 0),
            is_verified=(i % 2 == 0),
            views_count=random.randint(50, 500)
        )
        db.session.add(p)
        props.append(p)
    db.session.commit()

    # ── Testimonials ─────────────────────────────────
    for name, msg, rating in [
        ('Usman Ali',    'PrimeKey made finding my dream home in DHA so simple. Highly recommended!', 5),
        ('Ayesha Tariq', 'Got genuine inquiries within days of listing my shop. Great platform!', 5),
        ('Kamran Zafar', "Closed three deals in one quarter thanks to PrimeKey's amazing tools.", 4),
    ]:
        t = Testimonial(name=name, message=msg, rating=rating, is_active=True)
        db.session.add(t)
    db.session.commit()

    # ── Blog Posts ───────────────────────────────────
    blog_data = [
        ('How to Buy Your First Home in Pakistan', 'buying-first-home',
         'Real estate investment guide for first-time buyers.',
         'Buying your first home is exciting. Here is a step-by-step guide to navigate the process in Pakistan including documentation, verification and financing options.'),
        ('Top 5 Areas to Invest in Lahore 2024', 'top-areas-lahore-2024',
         'Best investment areas in Lahore for 2024 property buyers.',
         'Lahore continues to be one of the fastest-growing real estate markets. DHA, Bahria, Gulberg and Model Town lead the charts.'),
        ('Understanding Property Taxes in Pakistan', 'property-taxes-pakistan',
         'Complete guide to property taxes, CVT, stamp duty and documentation.',
         'Property taxes in Pakistan include CVT, stamp duty, and other fees. This guide explains what you need to know before buying or selling.'),
    ]
    for title, slug, excerpt, content in blog_data:
        b = Blog(
            title=title, slug=slug, excerpt=excerpt, content=content,
            author_id=admin.id, is_published=True,
            published_at=datetime.utcnow()
        )
        db.session.add(b)
    db.session.commit()

    # ── Settings ─────────────────────────────────────
    for key, value in [
        ('site_name', 'PrimeKey Estates'),
        ('site_email', 'hello@primekeyestates.pk'),
        ('site_phone', '+92 42 111-77463'),
        ('site_address', '14-B, Main Boulevard, DHA Phase 6, Lahore'),
        ('commission_rate', '2.5'),
    ]:
        s = Setting(key=key, value=value)
        db.session.add(s)
    db.session.commit()

    print("\n" + "=" * 48)
    print("  [OK] Seed data inserted successfully!")
    print("=" * 48)
    print(f"  Admin:   admin@primekeyestates.pk / admin123")
    print(f"  Agent:   ahmed@primekeyestates.pk / agent123")
    print(f"  Client:  usman@gmail.com / client123")
    print(f"  Props:   {len(props)} properties seeded")
    print(f"  Cities:  {len(city_data)} cities")
    print("=" * 48)
    print("  Next: python run.py  -> http://127.0.0.1:5000")
    print("=" * 48)
