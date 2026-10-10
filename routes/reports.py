from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import Report, CarListing
from forms import ReportForm

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/reports/create/<int:car_id>', methods=['GET', 'POST'])
@login_required
def create(car_id):
    listing = CarListing.query.get_or_404(car_id)
    form = ReportForm()

    if form.validate_on_submit():
        report = Report(
            user_id=current_user.id,
            car_listing_id = car_id,
            reason = form.reason.data,
            comment = form.comment.data,
            status = 'pending'
        )
        db.session.add(report)
        db.session.commit()
        flash('Пријавата е испратена.', 'success')
        return redirect(url_for('cars.detail', id=car_id))
    return render_template('reports/form.html', form=form, listing=listing)