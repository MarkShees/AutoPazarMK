from datetime import datetime, timedelta
from app import create_app
from extensions import db
from models import User, CarListing, Review, Message, Report, Payment

app = create_app()

SAMPLE_CARS = [
    {'brand': 'BMW', 'model': '320d', 'year': 2019, 'price': 18500, 'mileage': 95000},
    {'brand': 'Audi', 'model': 'A4', 'year': 2020, 'price': 22000, 'mileage': 72000},
    {'brand': 'Volkswagen', 'model': 'Golf 7', 'year': 2018, 'price': 12000, 'mileage': 110000},
    {'brand': 'Mercedes-Benz', 'model': 'C220', 'year': 2017, 'price': 21000, 'mileage': 130000},
    {'brand': 'Toyota', 'model': 'Corolla', 'year': 2021, 'price': 16000, 'mileage': 45000},
    {'brand': 'Ford', 'model': 'Focus', 'year': 2016, 'price': 7500, 'mileage': 145000},
    {'brand': 'Opel', 'model': 'Astra', 'year': 2019, 'price': 9800, 'mileage': 88000},
    {'brand': 'Peugeot', 'model': '308', 'year': 2018, 'price': 8900, 'mileage': 92000},
    {'brand': 'Renault', 'model': 'Megane', 'year': 2017, 'price': 8200, 'mileage': 105000},
    {'brand': 'Hyundai', 'model': 'i30', 'year': 2020, 'price': 11500, 'mileage': 68000},
    {'brand': 'Kia', 'model': 'Ceed', 'year': 2019, 'price': 10900, 'mileage': 77000},
    {'brand': 'Škoda', 'model': 'Octavia', 'year': 2018, 'price': 12500, 'mileage': 99000},
    {'brand': 'BMW', 'model': 'X3', 'year': 2020, 'price': 32000, 'mileage': 62000},
    {'brand': 'Audi', 'model': 'Q5', 'year': 2019, 'price': 28000, 'mileage': 81000},
    {'brand': 'Volkswagen', 'model': 'Passat', 'year': 2017, 'price': 13500, 'mileage': 125000},
    {'brand': 'Mercedes-Benz', 'model': 'E220', 'year': 2018, 'price': 26000, 'mileage': 98000},
    {'brand': 'Toyota', 'model': 'RAV4', 'year': 2021, 'price': 27000, 'mileage': 38000},
    {'brand': 'Ford', 'model': 'Mondeo', 'year': 2016, 'price': 9900, 'mileage': 138000},
    {'brand': 'Peugeot', 'model': '3008', 'year': 2020, 'price': 19500, 'mileage': 55000},
    {'brand': 'Hyundai', 'model': 'Tucson', 'year': 2019, 'price': 17800, 'mileage': 73000},
    {'brand': 'Škoda', 'model': 'Fabia', 'year': 2017, 'price': 7200, 'mileage': 118000},
    {'brand': 'Opel', 'model': 'Insignia', 'year': 2018, 'price': 11200, 'mileage': 102000},
]

CITIES = ['Скопје', 'Охрид', 'Битола', 'Тетово', 'Куманово', 'Прилеп', 'Струмица']

with app.app_context():
    db.drop_all()
    db.create_all()

    admin = User(name='Админ', email='admin@autopazar.mk', role='admin', city='Скопје',
                 phone='070000000')
    admin.set_password('password')
    db.session.add(admin)

    users = []
    for i, name in enumerate(['Марко', 'Ана', 'Петар'], 1):
        u = User(name=name, email=f'user{i}@test.mk', city='Скопје', phone=f'07012345{i}')
        u.set_password('password')
        users.append(u)
        db.session.add(u)

    db.session.flush()

    listings = []
    for i, car in enumerate(SAMPLE_CARS):
        listing = CarListing(
            user_id = users[i % len(users)].id,
            title = f"{car['brand']} {car['model']} {car['year']}",
            brand = car['brand'],
            model=car['model'],
            year=car['year'],
            price=car['price'],
            currency='EUR',
            mileage = car['mileage'],
            fuel_type = 'Дизел' if i % 2 == 0 else 'Бензин',
            transmission='Автоматски' if i % 3 == 0 else 'Рачен',
            body_type='SUV' if 'X3' in car['model'] or 'Q5' in car['model'] or 'RAV4' in car['model'] or 'Tucson' in car['model'] or '3008' in car['model'] else 'Лимузина',
            city = CITIES[i % len(CITIES)],
            contact_phone = f'07011122{i}',
            description='Одлично одржувано возило, регистрирано, без удари.',
            registration='Регистрирано',
            status = 'active',
            listing_type='premium' if i < 3 else ('featured' if i < 8 else 'regular'),
        )
        if listing.listing_type == 'featured':
            listing.featured_until = datetime.utcnow() + timedelta(days=15)
        if listing.listing_type == 'premium':
            listing.premium_until = datetime.utcnow() + timedelta(days=30)
        listings.append(listing)
        db.session.add(listing)

    db.session.flush()

    review = Review(
        reviewer_id = users[0].id,
        reviewed_user_id = users[1].id,
        car_listing_id = listings[0].id,
        rating = 5,
        type="seller_review",
        comment='Одличен продавач, брза комуникација.',
    )
    db.session.add(review)

    message = Message(
        sender_id = users[0].id,
        receiver_id = users[1].id,
        car_listing_id = listings[1].id,
        body='Здраво, дали возилото е уште достапно?',
    )
    db.session.add(message)

    report = Report(
        user_id = users[2].id,
        car_listing_id = listings[2].id,
        reason='Погрешна цена',
        comment='Цената не одговара на описот.',
        status='pending',
    )
    db.session.add(report)

    payment = Payment(
        user_id = users[0].id,
        car_listing_id = listings[5].id,
        package_type = 'featured_7',
        amount = 300,
        currency='MKD',
        status = 'pending',
        starts_at = datetime.utcnow(),
        ends_at = datetime.utcnow() + timedelta(days=7),
    )
    db.session.add(payment)

    db.session.commit()
    print('Seed завршен!')
    print('Admin: admin@autopazar.mk / password')
    print('User:  user1@test.mk / password')