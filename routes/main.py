from flask import Blueprint, render_template, flash, url_for, redirect
from models import CarListing,User, Review
from forms import ProfileForm
from flask_login import login_required, current_user
from extensions import db

main_bp = Blueprint('main', __name__)

BRANDS = ['BMW', 'Mercedes-Benz', 'Audi', 'Volkswagen', 'Opel', 'Toyota',
          'Ford', 'Peugeot', 'Renault', 'Hyundai', 'Kia', 'Škoda', 'Dacia', 'Lancia', 
          'Honda', 'Porsche', 'Suzuki', 'Jaguar']

@main_bp.route('/')
def index():
    latest = CarListing.query.filter_by(status='active').order_by(
        CarListing.created_at.desc()
    ).limit(8).all()
    featured = CarListing.query.filter(
        CarListing.status == 'active',
        CarListing.listing_type == 'featured'
    ).limit(4).all()
    premium = CarListing.query.filter(
        CarListing.status == 'active',
        CarListing.listing_type == 'premium'
    ).limit(4).all()
    return render_template('main/index.html', 
                           latest = latest, featured = featured, premium = premium, brands = BRANDS)

@main_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.phone = form.phone.data
        current_user.city = form.city.data
        db.session.commit()
        flash('Профилот е успешно зачуван.', 'success')
        return redirect(url_for('main.profile'))
    return render_template('main/profile.html', form=form)

@main_bp.route('/profile/<int:user_id>')
def public_profile(user_id):
    user = User.query.get_or_404(user_id)
    listings = user.listings.filter_by(status='active').limit(6).all()
    reviews = user.reviews_received.order_by(Review.created_at.desc()).all()
    return render_template('main/public_profile.html', user=user,
                           listings=listings, reviews=reviews)