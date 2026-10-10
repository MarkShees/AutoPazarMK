from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import Review, User, CarListing
from forms import ReviewForm

reviews_bp = Blueprint('reviews', __name__)

@reviews_bp.route('/reviews/create/<int:user_id>/<int:car_id>', methods=['GET', 'POST'])
@login_required
def create(user_id, car_id):
    reviewed_user = User.query.get_or_404(user_id)
    listing = CarListing.query.get_or_404(car_id)

    if user_id == current_user.id:
        flash('Не можете да се оцените сами.', 'danger')
        return redirect(url_for('cars.detail', id=car_id))
    
    existing = Review.query.filter_by(
        reviewer_id = current_user.id,
        reviewed_user_id = user_id,
        car_listing_id = car_id
    ).first()

    if existing :
        flash('Веќе сте оставиле рецензија за овој оглас.', 'warning')
        return redirect(url_for('cars.detail', id=car_id))
    
    form = ReviewForm()
    if form.validate_on_submit():
        review = Review(
            reviewer_id=current_user.id,reviewed_user_id=user_id,car_listing_id=car_id,
            rating=form.rating.data,type=form.type.data,comment=form.comment.data,
        )
        db.session.add(review)
        db.session.commit()
        flash('Рецензијата е успешно додадена.', 'success')
        return redirect(url_for('main.public_profile', user_id=user_id))
    return render_template(
        'reviews/form.html',
        form=form,
        reviewed_user=reviewed_user,
        listing=listing,
    )