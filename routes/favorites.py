from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from extensions import db
from models import Favorite, CarListing

favorites_bp = Blueprint('favorites', __name__)

@favorites_bp.route('/favorites')
@login_required
def list_favorites():
    favs= Favorite.query.filter_by(user_id=current_user.id).all()
    listings = [f.listing for f in favs]
    return render_template('favorites/list.html', listings=listings)

@favorites_bp.route('/favorites/add/<int:id>', methods=['POST'])
@login_required
def add(id):
    if not Favorite.query.filter_by(user_id = current_user.id, car_listing_id=id).first():
        db.session.add(Favorite(user_id=current_user.id, car_listing_id=id))
        db.session.commit()
    return redirect(request.referrer or url_for('cars.detail', id=id))

@favorites_bp.route('/favorites/remove/<int:id>', methods=['POST'])
@login_required
def remove(id):
    fav = Favorite.query.filter_by(user_id = current_user.id, car_listing_id=id).first()
    if fav:
        db.session.delete(fav)
        db.session.commit()
    return redirect(request.referrer or url_for('favorites.list_favorites'))