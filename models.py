from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id=db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    phone = db.Column(db.String(20))
    city = db.Column(db.String(50))
    role = db.Column(db.String(20), default='user')  # user | admin
    avatar = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    listings = db.relationship('CarListing', backref='owner', lazy='dynamic')
    sent_messages = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender', lazy='dynamic')
    received_messages = db.relationship('Message', foreign_keys='Message.receiver_id', backref='receiver', lazy='dynamic')
    reviews_written = db.relationship('Review', foreign_keys='Review.reviewer_id', backref='reviewer', lazy='dynamic')
    reviews_received = db.relationship('Review', foreign_keys='Review.reviewed_user_id', backref='reviewed_user', lazy='dynamic')
    favorites = db.relationship('Favorite', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @property
    def is_admin(self):
        return self.role == 'admin'
    
    def average_rating(self):
        reviews = self.reviews_received.all()
        if not reviews:
            return 0
        return round(sum(r.rating for r in reviews) / len(reviews), 1)
    
    def review_count(self):
        return self.reviews_received.count()

class CarListing(db.Model):
    __tablename__ = 'car_listings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    brand = db.Column(db.String(50), nullable=False, index=True)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False, index=True)
    price = db.Column(db.Float, nullable=False, index=True)
    currency = db.Column(db.String(3), default='EUR')  # EUR | MKD
    mileage = db.Column(db.Integer, nullable=False)
    fuel_type = db.Column(db.String(20), nullable=False)
    transmission = db.Column(db.String(20), nullable=False)
    body_type = db.Column(db.String(30), nullable=False)
    power_kw = db.Column(db.Integer)
    engine_size = db.Column(db.Integer)
    doors = db.Column(db.Integer)
    color = db.Column(db.String(30))
    registration = db.Column(db.String(20))
    city = db.Column(db.String(50), nullable=False, index=True)
    description = db.Column(db.Text)
    contact_phone = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='active', index=True)
    listing_type = db.Column(db.String(20), default='regular', index=True)
    featured_until = db.Column(db.DateTime)
    premium_until = db.Column(db.DateTime)
    views_count = db.Column(db.Integer, default=0)
    phone_views_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    images = db.relationship('CarImage', backref='listing', lazy='dynamic', cascade='all, delete-orphan')
    favorites = db.relationship('Favorite', backref='listing', lazy='dynamic', cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='car_listing', lazy='dynamic', cascade='all, delete-orphan')
    messages = db.relationship('Message', backref='car_listing', lazy='dynamic', cascade='all, delete-orphan')
    reports = db.relationship('Report', backref='car_listing', lazy='dynamic', cascade='all, delete-orphan')
    payments = db.relationship('Payment', backref='car_listing', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def main_image(self):
        img = self.images.filter_by(is_main = True).first()
        if img:
            return img.path
        first = self.images.order_by(CarImage.sort_order).first()
        return first.path if first else None
    
    @property
    def is_sold(self):
        return self.status == 'sold'
    
    @property
    def is_featured(self):
        return self.listing_type == 'featured' and self.featured_until and self.featured_until > datetime.utcnow()
    
    @property
    def is_premium (self):
        return self.listing_type == 'premium' and self.premium_until and self.premium_until > datetime.utcnow()

class CarImage(db.Model):
    __tablename__ = 'car_images'
    id = db.Column(db.Integer, primary_key=True)
    car_listing_id = db.Column(db.Integer, db.ForeignKey('car_listings.id'), nullable=False)
    path = db.Column(db.String(300), nullable=False)
    is_main = db.Column(db.Boolean, default=False)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)



class Favorite(db.Model):
    __tablename__ = 'favorites'
    __table_args__ = (db.UniqueConstraint('user_id', 'car_listing_id'),)
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    car_listing_id = db.Column(db.Integer, db.ForeignKey('car_listings.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Review(db.Model):
    __tablename__ = 'reviews'
    __table_args__ = (db.UniqueConstraint('reviewer_id', 'reviewed_user_id', 'car_listing_id'),)
    id = db.Column(db.Integer, primary_key=True)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reviewed_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    car_listing_id = db.Column(db.Integer, db.ForeignKey('car_listings.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(20), nullable=False)  # buyer_review | seller_review
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    car_listing_id = db.Column(db.Integer, db.ForeignKey('car_listings.id'), nullable=False)
    body = db.Column(db.Text, nullable=False)
    read_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    car_listing_id = db.Column(db.Integer, db.ForeignKey('car_listings.id'), nullable=False)
    package_type = db.Column(db.String(30), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='MKD')
    status = db.Column(db.String(20), default='pending')
    starts_at = db.Column(db.DateTime)
    ends_at = db.Column(db.DateTime)
    confirmed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='payments')


class Report(db.Model):
    __tablename__ = 'reports'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    car_listing_id = db.Column(db.Integer, db.ForeignKey('car_listings.id'), nullable=False)
    reason = db.Column(db.String(50), nullable=False)
    comment = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='reports')