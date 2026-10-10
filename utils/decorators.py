from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user
from models import CarListing

def owner_or_admin_required(f):
    @wraps(f)
    def decorated(id, *args, **kwargs):
        listing = CarListing.query.get_or_404(id)
        if listing.user_id != current_user.id and not current_user.is_admin:
            flash('Немате дозвола за оваа акција.', 'danger')
            return redirect(url_for('cars.detail', id=id))
        return f(id, *args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated