from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from extensions import db
from models import CarListing, Payment

payments_bp = Blueprint('payments', __name__)

PACKAGES = {
    'featured_7':  {'type': 'featured', 'days': 7,  'amount': 300,  'label': 'Истакнат оглас 7 дена'},
    'featured_15': {'type': 'featured', 'days': 15, 'amount': 500,  'label': 'Истакнат оглас 15 дена'},
    'featured_30': {'type': 'featured', 'days': 30, 'amount': 800,  'label': 'Истакнат оглас 30 дена'},
    'premium_7':  {'type': 'premium',  'days': 7,  'amount': 600,  'label': 'Премиум оглас 7 дена'},
    'premium_15': {'type': 'premium',  'days': 15, 'amount': 1000, 'label': 'Премиум оглас 15 дена'},
    'premium_30': {'type': 'premium',  'days': 30, 'amount': 1500, 'label': 'Премиум оглас 30 дена'},
}

@payments_bp.route('/payments/create/<int:car_id>', methods=['GET', 'POST'])
@login_required
def create(car_id):
    listing = CarListing.query.get_or_404(car_id)
    if listing.user_id != current_user.id:
        abort(403)
    if request.method == 'POST':
        pkg_key = request.form.get('package')
        pkg = PACKAGES.get(pkg_key)
        if pkg:
            from datetime import timedelta
            payment = Payment(
                user_id = current_user.id,
                car_listing_id = car_id,
                package_type = pkg_key,
                amount = pkg['amount'],
                currency = 'MKD',
                status = 'pending',
                starts_at = datetime.utcnow(),
                ends_at = datetime.utcnow() + timedelta(days=pkg['days']),
            )
            db.session.add(payment)
            db.session.commit()
            flash('Барањето за промоција е испратено. Чека потврда од админ.', 'info')
            return redirect(url_for('cars.my_cars'))
    return render_template('payments/packages.html', listing=listing, packages=PACKAGES)