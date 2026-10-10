from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from extensions import db
from models import User, CarListing, Payment, Report, Review
from utils.decorators import admin_required
from utils.helpers import delete_listing_images
from routes.payments import PACKAGES

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    stats = {
        'users': User.query.count(),
        'listings': CarListing.query.count(),
        'active': CarListing.query.filter_by(status = 'active').count(),
        'sold': CarListing.query.filter_by(status='sold').count(),
        'pending_payments': Payment.query.filter_by(status='pending').count(),
        'featured': CarListing.query.filter_by(listing_type='featured').count(),
        'premium': CarListing.query.filter_by(listing_type = 'premium').count(),
        'reports': Report.query.filter_by(status = 'pending').count(),
        'reviews': Review.query.count(),
    }
    return render_template('admin/dashboard.html', stats = stats)

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/cars')
@login_required
@admin_required
def cars():
    listings = CarListing.query.order_by(CarListing.created_at.desc()).all()
    return render_template('admin/cars.html', listings=listings)


@admin_bp.route('/cars/<int:id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_car(id):
    listing = CarListing.query.get_or_404(id)
    listing.status = 'active'
    db.session.commit()
    flash('Огласот е одобрен.', 'success')
    return redirect(url_for('admin.cars'))


@admin_bp.route('/cars/<int:id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_car(id):
    listing = CarListing.query.get_or_404(id)
    listing.status = 'rejected'
    db.session.commit()
    flash('Огласот е одбиен.', 'warning')
    return redirect(url_for('admin.cars'))

@admin_bp.route('/cars/<int:id>/status', methods=['POST'])
@login_required
@admin_required
def change_car_status(id):
    listing = CarListing.query.get_or_404(id)
    status = request.form.get('status')
    allowed = {'active', 'pending', 'rejected', 'sold', 'expired'}
    if status in allowed :
        listing.status = status
        db.session.commit()
        flash('Статусот е променет.', 'success')
    else:
        flash('Невалиден статус.', 'danger')
    return redirect(url_for('admin.cars'))

@admin_bp.route('/cars/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_car(id):
    listing = CarListing.query.get_or_404(id)
    delete_listing_images(listing.id)
    db.session.delete(listing)
    db.session.commit()
    flash('Огласот е избришан.', 'success')
    return redirect(url_for('admin.cars'))

@admin_bp.route('/payments')
@login_required
@admin_required
def payments():
    payments = Payment.query.order_by(Payment.created_at.desc()).all()
    return render_template('admin/payments.html', payments=payments, packages=PACKAGES)


@admin_bp.route('/payments/<int:id>/confirm', methods=['POST'])
@login_required
@admin_required
def confirm_payment(id):
    payment = Payment.query.get_or_404(id)
    listing = payment.car_listing
    pkg = PACKAGES.get(payment.package_type)
    if payment.status != 'pending':
        flash('Оваа уплата веќе е обработена.', 'warning')
        return redirect(url_for('admin.payments'))
    if not pkg:
        flash('Непознат пакет.', 'danger')
        return redirect(url_for('admin.payments'))
    if pkg['type'] == 'featured':
        listing.listing_type = 'featured'
        listing.featured_until = payment.ends_at
    else:
        listing.listing_type = 'premium'
        listing.premium_until = payment.ends_at
    payment.status = 'confirmed'
    payment.confirmed_at = datetime.utcnow()
    db.session.commit()
    flash('Уплатата е потврдена.', 'success')
    return redirect(url_for('admin.payments'))

@admin_bp.route('/reports')
@login_required
@admin_required
def reports():
    reports = Report.query.order_by(Report.created_at.desc()).all()
    return render_template('admin/reports.html', reports=reports)

@admin_bp.route('/reports/<int:id>/status', methods=['POST'])
@login_required
@admin_required
def report_status(id):
    report = Report.query.get_or_404(id)
    status = request.form.get('status')
    if status in {'pending', 'reviewed', 'dismissed'}:
        report.status = status
        db.session.commit()
        flash('Статусот на пријавата е променет.', 'success')
    return redirect(url_for('admin.reports'))

@admin_bp.route('/reviews')
@login_required
@admin_required
def reviews():
    reviews = Review.query.order_by(Review.created_at.desc()).all()
    return render_template('admin/reviews.html', reviews=reviews)

@admin_bp.route('/reviews/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_review(id):
    review = Review.query.get_or_404(id)
    db.session.delete(review)
    db.session.commit()
    flash('Рецензијата е избришана.', 'success')
    return redirect(url_for('admin.reviews'))